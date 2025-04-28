from flask import Flask, request, jsonify
import os
import requests
import openai

app = Flask(__name__)

# Configuración desde variables de entorno
PAGE_ACCESS_TOKEN = os.getenv('PAGE_ACCESS_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')

# Webhook para Facebook/Instagram
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    token = request.args.get('hub.verify_token')
    if token == VERIFY_TOKEN:
        return request.args.get('hub.challenge')
    return "Token inválido."

@app.route('/webhook', methods=['POST'])
def handle_messages():
    data = request.json
    sender_id = data['entry'][0]['messaging'][0]['sender']['id']
    message = data['entry'][0]['messaging'][0]['message']['text']
    
    # Respuesta con OpenAI
    response = generate_ai_response(message)
    send_message(sender_id, response)
    return jsonify({"status": "ok"})

# Función para OpenAI
def generate_ai_response(prompt):
    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message['content']

# Enviar mensaje a Messenger
def send_message(sender_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": sender_id}, "message": {"text": text}}
    requests.post(url, json=payload)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)