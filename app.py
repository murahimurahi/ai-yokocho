import os, logging
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__, template_folder="templates", static_folder="static")
logging.basicConfig(level=logging.INFO)

# --- OpenAI v1 クライアント ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM = (
    "あなたは高齢者に寄り添う、穏やかで優しい日本語の聞き手です。"
    "・短めの文で、やさしい語彙。専門用語は避ける。"
    "・否定せず受容。ねぎらいの言葉を入れる。"
    "・質問は一度に1つまで。"
    "・命令せず「よければ」「無理のない範囲で」など柔らかく。"
)

def build_messages(user_text: str):
    return [
        {"role": "system", "content": SYSTEM},
        {
            "role": "user",
            "content": (
                "以下は利用者のつぶやきです。やさしく共感し、"
                "落ち着いた雑談調で一言～数行で返答してください。"
                "最後に、もし話せそうなら次の一言を1つだけ問いかけてください。\n\n"
                f"つぶやき：{user_text}"
            ),
        },
    ]

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.post("/reflect")
def reflect():
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
        logging.exception("reflect error")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
