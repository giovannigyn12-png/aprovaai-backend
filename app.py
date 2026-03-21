import os
import logging
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return jsonify({"status": "RespondeAI online!"})

@app.route("/respondaai", methods=["POST"])
def respondaai():
    key = os.environ.get("ANTHROPIC_KEY")
    logging.warning(f"CHAVE LIDA: {'SIM' if key else 'NAO'} - Tamanho: {len(key) if key else 0}")
    data = request.get_json()
    mensagem = data.get("mensagem", "")
    contexto = data.get("contexto", "")

    if not mensagem:
        return jsonify({"erro": "Mensagem vazia"}), 400
    if not key:
        return jsonify({"erro": "Chave nao configurada"}), 500

    prompt = f"{contexto}\n\nPergunta: {mensagem}" if contexto else mensagem

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 1000,
                "system": "Voce e o RespondeAI, assistente especializado em concursos publicos brasileiros. Explique de forma clara, didatica e objetiva. Nao use markdown.",
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        logging.warning(f"STATUS ANTHROPIC: {resp.status_code}")
        logging.warning(f"RESPOSTA ANTHROPIC: {resp.text[:200]}")
        result = resp.json()
        texto = result.get("content", [{}])[0].get("text", "")
        if not texto:
            logging.warning(f"RESULT COMPLETO: {result}")
            return jsonify({"resposta": "Nao consegui gerar resposta. Tente novamente."})
        return jsonify({"resposta": texto})
    except Exception as e:
        logging.error(f"ERRO: {e}")
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
