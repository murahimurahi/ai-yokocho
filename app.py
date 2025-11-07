from flask import Flask, render_template, request, jsonify
import openai, os, logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reflect', methods=['POST'])
def reflect():
    data = request.get_json()
    user_text = data.get("text", "")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたは優しく共感的な話し相手です。ユーザーの気持ちを整理し、前向きな一言で締めます。"},
                {"role": "user", "content": user_text}
            ],
            temperature=0.8,
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({"reply": reply})
    except Exception as e:
        logging.error(e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
