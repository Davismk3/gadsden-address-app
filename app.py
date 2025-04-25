from flask import Flask, request, render_template
import pandas as pd
from metaphone import doublemetaphone
from rapidfuzz import fuzz
import os

app = Flask(__name__)

# 🔁 Full-word phonetic encoding
def get_full_phonetic(text):
    words = str(text).lower().split()
    codes = [doublemetaphone(w)[0] for w in words]
    return " ".join(codes)

# Load and preprocess
df = pd.read_csv("roads.csv")
df["phonetic"] = df["address"].apply(get_full_phonetic)

# 🔍 Improved matcher
def get_matches(guess):
    guess = guess.lower()
    guess_phonetic = get_full_phonetic(guess)

    df["text_score"] = df["address"].apply(lambda x: fuzz.ratio(guess, x.lower()))
    df["phonetic_score"] = df["phonetic"].apply(lambda x: fuzz.ratio(guess_phonetic, x))
    df["combined_score"] = 0.5 * df["text_score"] + 0.5 * df["phonetic_score"]

    top_matches = df.sort_values("combined_score", ascending=False).head(20)["address"].tolist()
    return top_matches

# Route
@app.route("/", methods=["GET", "POST"])
def index():
    matches = []
    guess = ""
    if request.method == "POST":
        guess = request.form["guess"]
        matches = get_matches(guess)
    return render_template("index.html", guess=guess, matches=matches)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"✅ Running on 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)
