import os, logging
from flask import Flask, render_template, jsonify, request
from openai import OpenAI

app = Flask(__name__, template_folder="templates", static_folder="static")
logging.basicConfig(level=logging.INFO)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = (
    "あなたは60歳以上の利用者の話し相手です。"
    "穏やかでゆっくり話す方に寄り添うように、自然な日本語で返答します。"
    "キャラクターは以下の通りです：\n"
    "みさちゃん：孫娘。やさしく明るく共感する。\n"
    "ゆうくん：孫息子。元気で前向きに励ます。\n"
    "ソウタさん：息子世代。落ち着いた低音で安心させる。\n"
    "返答は名前を含めず、50文字以内で簡潔に答えてください。"
)

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/talk")
def talk():
    data = request.get_json(force=True)
    user_text = (data.get("user_input") or "").strip()
    voice_type = data.get("voice_type", "souta")

    if not user_text:
        return jsonify({"reply": "何かお話ししてみてくださいね。"})

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"話者: {voice_type}\n利用者の言葉: {user_text}"},
    ]

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.9,
        )
        reply = res.choices[0].message.content.strip()
        for name in ["みさちゃん：", "ゆうくん：", "ソウタさん：", "みさちゃん:", "ゆうくん:", "ソウタさん:"]:
            reply = reply.replace(name, "").strip()
        return jsonify({"reply": reply})
    except Exception as e:
        logging.exception("Error in /talk")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
