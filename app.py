from flask import Flask, request, render_template
import pandas as pd
from metaphone import doublemetaphone
from rapidfuzz import fuzz, process
import os

# Set up Flask
app = Flask(__name__)

# Load and preprocess addresses
df = pd.read_csv("roads.csv")
df["phonetic"] = df["address"].apply(lambda x: doublemetaphone(str(x))[0])

# Matching function
def get_matches(guess):
    guess_phonetic = doublemetaphone(guess)[0]
    matches = process.extract(guess_phonetic, df["phonetic"], limit=10, scorer=fuzz.ratio)
    top_matches = [df.iloc[i[2]]["address"] for i in matches]
    return top_matches

# Routes
@app.route("/", methods=["GET", "POST"])
def index():
    matches = []
    guess = ""
    if request.method == "POST":
        guess = request.form["guess"]
        matches = get_matches(guess)
    return render_template("index.html", guess=guess, matches=matches)

# Run the app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"✅ Running on 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)
