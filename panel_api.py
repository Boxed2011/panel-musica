import threading
from discord.ext import commands
from flask import Flask, request, jsonify, abort, send_from_directory
from flask_cors import CORS
import discord
import asyncio
import os

API_KEY_SECRETA = "Zyn0rX ツ 0124"
app = Flask(__name__)
CORS(app)

bot_instance: commands.Bot = None

@app.before_request
def verificar_api_key():
    if request.path.startswith('/health') or request.path.startswith('/'):
        return
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != API_KEY_SECRETA:
        abort(401)

@app.route('/health')
def health_check():
    return "OK", 200

# Servir web
@app.route('/')
def index():
    return send_from_directory('web', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('web', path)

# Reproducir música desde web
@app.route('/play', methods=['POST'])
async def api_play():
    if not bot_instance:
        return jsonify({"error": "Bot no está listo"}), 503

    datos = request.json
    guild_id = datos.get('guild_id')
    user_id = datos.get('user_id')
    query = datos.get('query')

    if not all([guild_id, user_id, query]):
        return jsonify({"error": "Faltan datos"}), 400

    try:
        guild = bot_instance.get_guild(int(guild_id))
        if not guild:
            return jsonify({"error": "Servidor no encontrado"}), 404

        member = guild.get_member(int(user_id))
        if not member or not member.voice:
            return jsonify({"error": "Usuario no en canal de voz"}), 400

        canal_voz = member.voice.channel
        musica_cog = bot_instance.get_cog("MusicaCog")
        if not musica_cog:
            return jsonify({"error": "Cog Musica no cargado"}), 500

        asyncio.create_task(musica_cog.reproducir_desde_api(canal_voz, query))
        return jsonify({"message": f"Reproduciendo: {query}"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def iniciar_servidor_api(bot: commands.Bot):
    global bot_instance
    bot_instance = bot
    print("Iniciando servidor API y web...")
    threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), use_reloader=False),
        daemon=True
    ).start()
