import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
import requests
from urllib.parse import urlparse

app = Flask(__name__)

# Get keys from environment
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_IDS = {
    "left": os.getenv("SEARCH_ENGINE_ID_LEFT"),
    "center": os.getenv("SEARCH_ENGINE_ID_CENTER"),
    "right": os.getenv("SEARCH_ENGINE_ID_RIGHT")
}


def get_articles(bias, query):
    engine_id = SEARCH_ENGINE_IDS.get(bias.lower())
    if not engine_id:
        return [("Error", "#", f"Invalid bias selected: {bias}")]

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": engine_id,
        "q": query,
        "num": 10
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return [("Error", "#", f"{response.status_code} - {response.text}")]

    data = response.json()
    articles = []

    for item in data.get("items", []):
        title = item.get("title", "No Title")
        link = item.get("link", "#")
        snippet = item.get("snippet", "")
        source = item.get("displayLink", "Unknown Source")
        full_title = f"{source} – {title}"
        articles.append((full_title, link, snippet))

    return articles


@app.route("/", methods=["GET", "POST"])
def index():
    articles = []
    bias = ""
    query = ""

    if request.method == "POST":
        bias = request.form.get("bias", "").lower()
        query = request.form.get("question", "")
        print(f"FORM DATA: bias={bias}, query={query}")

        articles = get_articles(bias, query)

    return render_template("index.html", articles=articles, bias=bias, query=query)

if __name__ == "__main__":
    app.run(debug=True)
