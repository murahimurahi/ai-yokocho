import os, logging
from flask import Flask, render_template, request, jsonify, send_file
from openai import OpenAI

app = Flask(__name__, template_folder="templates", static_folder="static")
logging.basicConfig(level=logging.INFO)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = (
    "あなたは60歳以上の利用者の話し相手です。"
    "穏やかでゆっくり話す方に寄り添うように自然な日本語で返答してください。"
    "返答は50文字以内。名前や敬称は付けず、やさしい言葉にしてください。"
)

VOICE_MAP = {
    "misa": "verse",    # 明るい女性
    "yuu": "nova",      # 若い男性（少年寄り）
    "souta": "alloy",   # 落ち着いた男性
}

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/talk")
def talk():
    data = request.get_json(force=True)
    user_input = (data.get("user_input") or "").strip()
    voice_type = data.get("voice_type", "souta")

    if not user_input:
        return jsonify({"error": "入力が空です"})

    try:
        # Step1: 返答生成
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            temperature=0.8,
        )
        reply = completion.choices[0].message.content.strip()

        # Step2: 音声生成
        tts = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice=VOICE_MAP.get(voice_type, "alloy"),
            input=reply
        )

        mp3_path = "static/reply.mp3"
        with open(mp3_path, "wb") as f:
            f.write(tts.read())

        return jsonify({"reply": reply, "audio_url": f"/{mp3_path}"})
    except Exception as e:
        logging.exception("Error in /talk")
        return jsonify({"error": str(e)}), 500

@app.get("/static/reply.mp3")
def serve_audio():
    return send_file("static/reply.mp3", mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
