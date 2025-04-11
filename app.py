import json
import string
import random
from flask import Flask, request, render_template, redirect
from datetime import datetime

app = Flask(__name__)

def load_urls():
    try:
        with open("urls.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_urls(urls):
    with open("urls.json", "w") as f:
        json.dump(urls, f, indent=4, ensure_ascii=False)

def generate_short_id(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route("/", methods=["GET", "POST"])
def index():
    urls = load_urls()

    if request.method == "POST":
        original_url = request.form["original_url"]
        custom_domain = request.form.get("custom_domain", "default") or "default"

        short_id = generate_short_id()
        while short_id in urls:
            short_id = generate_short_id()

        urls[short_id] = {
            "original_url": original_url,
            "custom_domain": custom_domain,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "clicks": 0
        }

        save_urls(urls)

        # هنا نعدل الرابط المختصر ليظهر اسم المنصة
        short_url = f"{request.host_url}{custom_domain}/{short_id}"
        return render_template("index.html", short_url=short_url)

    return render_template("index.html")

@app.route("/<custom_domain>/<short_id>")
def redirect_to_url(custom_domain, short_id):
    urls = load_urls()
    if short_id in urls and urls[short_id]["custom_domain"] == custom_domain:
        urls[short_id]["clicks"] += 1
        save_urls(urls)

        return redirect(urls[short_id]["original_url"])
    return "الرابط غير موجود", 404

if __name__ == "__main__":
    app.run(debug=True)
