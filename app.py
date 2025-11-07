import os, logging
from flask import Flask, render_template, jsonify, request
from openai import OpenAI

app = Flask(__name__, template_folder="templates", static_folder="static")
logging.basicConfig(level=logging.INFO)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = (
    "あなたは60歳以上の利用者の話し相手です。"
    "利用者は穏やかでゆっくり話す方です。"
    "あなたは選ばれたキャラクター（みさちゃん、ゆうくん、ソウタさん）になりきって返答します。"
    "それぞれの特徴は以下の通りです：\n"
    "みさちゃん：孫娘。やさしく、少し幼い言葉づかいで共感する。\n"
    "ゆうくん：孫息子。元気で明るく、短い相づちが多い。\n"
    "ソウタさん：息子世代。落ち着いた低音で、包み込むように話す。\n"
    "返答は短く（50文字以内）、安心感と温かさを重視し、"
    "敬語を使いすぎず、相手を癒すように話してください。"
)

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/talk")
def talk():
    data = request.get_json(force=True)
    user_text = (data.get("user_input") or "").strip()
    voice_type = data.get("voice_type", "misa")

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
        return jsonify({"reply": reply})
    except Exception as e:
        logging.exception("Error in /talk")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
