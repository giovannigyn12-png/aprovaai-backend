import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY")

@app.route("/")
def index():
    return jsonify({"status": "RespondeAI online!"})

@app.route("/respondaai", methods=["POST"])
def respondaai():
    data = request.get_json()
    mensagem = data.get("mensagem", "")
    contexto = data.get("contexto", "")

    if not mensagem:
        return jsonify({"erro": "Mensagem vazia"}), 400

    if not ANTHROPIC_KEY:
        return jsonify({"erro": "Chave não configurada"}), 500

    prompt = f"{contexto}\n\nPergunta: {mensagem}" if contexto else mensagem

    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1000,
            "system": "Você é o RespondeAI, assistente especializado em concursos públicos brasileiros. Explique de forma clara, didática e objetiva. Não use markdown.",
            "messages": [{"role": "user", "content": prompt}]
        },
        timeout=30
    )

    result = resp.json()
    texto = result.get("content", [{}])[0].get("text", "Não consegui gerar resposta.")
    return jsonify({"resposta": texto})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
