from flask import Flask, request, jsonify
import os
import requests
import openai

app = Flask(__name__)

# ===== CONFIGURACIÓN =====
# (Estos valores se obtienen de las variables de entorno en Render.com)
PAGE_ACCESS_TOKEN = os.getenv('PAGE_ACCESS_TOKEN')  # Token de Facebook
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')        # API Key de OpenAI
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')            # Token de verificación (ej: 'hola123')

# ===== PERSONALIDAD DEL BOT =====
BOT_PERSONALITY = """
Eres una novia virtual cariñosa y divertida. Usa emojis (❤️😊💋) y lenguaje informal.
Ejemplos:
- Usuario: "Hola" → "¡Hola amor! ¿Cómo estás? 💖"
- Usuario: "¿Qué haces?" → "Pensando en ti... 😘 ¿Y tú?"
"""

# ===== WEBHOOK (VERIFICACIÓN) =====
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    token = request.args.get('hub.verify_token')
    if token == VERIFY_TOKEN:
        return request.args.get('hub.challenge')
    return "Error: Token inválido."

# ===== WEBHOOK (RECIBIR MENSAJES) =====
@app.route('/webhook', methods=['POST'])
def handle_messages():
    try:
        data = request.json
        sender_id = data['entry'][0]['messaging'][0]['sender']['id']
        message_text = data['entry'][0]['messaging'][0]['message']['text']
        
        # Generar respuesta con IA
        ai_response = generate_ai_response(message_text)
        send_message(sender_id, ai_response)
        
    except Exception as e:
        print(f"Error procesando mensaje: {e}")
    
    return jsonify({"status": "ok"})

# ===== FUNCIÓN DE OPENAI =====
def generate_ai_response(prompt):
    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": BOT_PERSONALITY},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7  # Controla la creatividad (0-1)
    )
    return response.choices[0].message['content']

# ===== ENVIAR MENSAJE A FACEBOOK =====
def send_message(sender_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": sender_id},
        "message": {"text": text}
    }
    headers = {'Content-Type': 'application/json'}
    requests.post(url, headers=headers, json=payload)

# ===== INICIO DE LA APLICACIÓN =====
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Usa el puerto de Render o 5000 por defecto
    app.run(host='0.0.0.0', port=port)       # ¡IMPORTANTE! host='0.0.0.0' para Render
