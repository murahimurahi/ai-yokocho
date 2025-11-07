import os, logging
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__, template_folder="templates", static_folder="static")
logging.basicConfig(level=logging.INFO)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM = (
    "あなたは高齢者の話し相手AIです。"
    "聞き上手で、ゆっくり優しい日本語で会話します。"
    "・短い文で話す。"
    "・否定せず共感。"
    "・相手を安心させる。"
    "・語尾は柔らかく、～ですね、～ですよ、などを使う。"
    "・質問は一度に1つまで。"
)

def build_messages(user_text: str):
    return [
        {"role": "system", "content": SYSTEM},
        {
            "role": "user",
            "content": f"利用者の言葉：{user_text}\nこれに対して優しく寄り添う返事をしてください。",
        },
    ]

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/talk")
def talk():
    try:
        data = request.get_json(force=True)
        user_text = (data.get("user_input") or "").strip()
        if not user_text:
            return jsonify({"error": "empty"}), 400

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=build_messages(user_text),
            temperature=0.8,
        )
        reply = resp.choices[0].message.content.strip()
        return jsonify({"reply": reply})
    except Exception as e:
        logging.exception("talk error")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
