from flask import Flask, request, jsonify
import os
import requests
import openai

app = Flask(__name__)

# Configuración (estas variables se establecen en Render.com)
PAGE_ACCESS_TOKEN = os.getenv('PAGE_ACCESS_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')

# Personalidad del bot
BOT_PERSONALITY = """
Eres una novia virtual cariñosa y atenta. Usa emojis (❤️😘💌) y lenguaje informal.
Ejemplo de respuestas:
- "Hola" → "¡Hola mi amor! ¿Cómo estás hoy? 💖"
- "¿Qué haces?" → "Pensando en ti... 😊 ¿Y tú qué haces?"
"""

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    token = request.args.get('hub.verify_token')
    if token == VERIFY_TOKEN:
        return request.args.get('hub.challenge')
    return "Token inválido."

@app.route('/webhook', methods=['POST'])
def handle_messages():
    try:
        data = request.json
        sender_id = data['entry'][0]['messaging'][0]['sender']['id']
        message_text = data['entry'][0]['messaging'][0]['message']['text']
        
        # Generar respuesta con IA
        response = generate_ai_response(message_text)
        send_message(sender_id, response)
        
    except Exception as e:
        print(f"Error: {e}")
    
    return jsonify({"status": "ok"})

def generate_ai_response(prompt):
    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": BOT_PERSONALITY},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message['content']

def send_message(sender_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": sender_id},
        "message": {"text": text}
    }
    headers = {'Content-Type': 'application/json'}
    requests.post(url, headers=headers, json=payload)

# Solo para desarrollo local
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
