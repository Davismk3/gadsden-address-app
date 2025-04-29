from flask import Flask, request, render_template
import pandas as pd
from metaphone import doublemetaphone
from rapidfuzz import fuzz
import os

app = Flask(__name__)

# Full-word phonetic encoding
def get_full_phonetic(text):  # converts a string into phonetic codes 
    words = str(text).lower().split()  # converts a string to lowercase, then splits into words 
    codes = [doublemetaphone(w)[0] for w in words]  # converts words into phonetic codes 
    return " ".join(codes)  # joins phonetic codes 

# Load and preprocess
df = pd.read_csv("roads.csv")  # reads csv file
df["phonetic"] = df["address"].apply(get_full_phonetic)  # converts all in address column into phonetic code

# Improved matcher
def get_matches(guess):
    guess = guess.lower()  # lowercase the user's input, seems to improve the results
    guess_phonetic = get_full_phonetic(guess).lower()  # phonetic code for input 

    df["text_score"] = df["address"].apply(lambda x: fuzz.ratio(guess, x.lower()))  # save spelling score in new column
    df["phonetic_score"] = df["phonetic"].apply(lambda x: fuzz.ratio(guess_phonetic, x))  # save phonetic score in new column
    df["combined_score"] = 0.5 * df["text_score"] + 0.5 * df["phonetic_score"]  # combine spelling and phonetic score
    
    """
    For example, the new data file will look like this:

    address, phonetic, text_score, phonetic_score, combined_score
    'main street', 'MN STRT', 85, 90, 87.5
    """

    # Sort with highest score first, show the top 20, select only the address column, convert to python list
    top_matches = df.sort_values("combined_score", ascending=False).head(20)["address"].tolist()
    return top_matches

# Website stuff
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
    print(f"Running on 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)
