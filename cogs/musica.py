import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
import asyncio

# --- Configuración de YTDL ---
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

# Opciones de FFmpeg
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

# Clase de fuente de audio
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('webpage_url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(YTDL_OPTIONS).extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else yt_dlp.YoutubeDL(YTDL_OPTIONS).prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)

# --- Cog de Música ---
class MusicaCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queues = {}
        self.ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)
        print("Cog de Música (FFmpeg) cargado.")

    async def get_player(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("❌ Debes estar en un canal de voz.", ephemeral=True)
            return None
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.move_to(interaction.user.voice.channel)
            return interaction.guild.voice_client
        else:
            return await interaction.user.voice.channel.connect()

    def play_next(self, interaction: discord.Interaction):
        gid = interaction.guild_id
        if gid in self.queues and self.queues[gid]:
            source = self.queues[gid].pop(0)
            interaction.guild.voice_client.play(source, after=lambda e: self.play_next(interaction))
        else:
            asyncio.create_task(interaction.guild.voice_client.disconnect())

    def play_next_from_api(self, voice_client, guild_id):
        """Callback para reproducir siguiente canción desde la API."""
        if guild_id in self.queues and self.queues[guild_id]:
            source = self.queues[guild_id].pop(0)
            voice_client.play(source, after=lambda e: self.play_next_from_api(voice_client, guild_id))
        else:
            asyncio.create_task(voice_client.disconnect())

    # --- Comandos /play, /stop, /skip ---
    @app_commands.command(name="play", description="Reproduce una canción de YouTube (requiere FFmpeg).")
    @app_commands.describe(busqueda="Nombre o URL de la canción")
    async def play_command(self, interaction: discord.Interaction, *, busqueda: str):
        voice_client = await self.get_player(interaction)
        if not voice_client:
            return
        await interaction.response.defer(thinking=True)
        try:
            source = await YTDLSource.from_url(busqueda, loop=self.bot.loop, stream=True)
            gid = interaction.guild_id
            if gid not in self.queues:
                self.queues[gid] = []
            if voice_client.is_playing() or voice_client.is_paused():
                self.queues[gid].append(source)
                await interaction.followup.send(f"✅ Se añadió a la cola: **{source.title}**")
            else:
                voice_client.play(source, after=lambda e: self.play_next(interaction))
                await interaction.followup.send(f"🎶 Ahora reproduciendo: **{source.title}**")
        except Exception as e:
            await interaction.followup.send(f"❌ Ocurrió un error: {e}")

    @app_commands.command(name="stop", description="Detiene la música y desconecta el bot.")
    async def stop_command(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client:
            await interaction.response.send_message("No estoy conectado a ningún canal de voz.", ephemeral=True)
            return
        if interaction.guild_id in self.queues:
            self.queues[interaction.guild_id] = []
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("👋 ¡Adiós! Bot desconectado.")

    @app_commands.command(name="skip", description="Salta la canción actual.")
    async def skip_command(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client or not interaction.guild.voice_client.is_playing():
            await interaction.response.send_message("No estoy reproduciendo nada ahora mismo.", ephemeral=True)
            return
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("⏭️ Canción saltada.")

    # --- Función que la web llama ---
    async def reproducir_desde_api(self, canal_voz: discord.VoiceChannel, query: str):
        guild = canal_voz.guild
        try:
            if guild.voice_client:
                await guild.voice_client.move_to(canal_voz)
            else:
                await canal_voz.connect()
            data = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.ytdl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            )
            source = YTDLSource(discord.FFmpegPCMAudio(data['url'], **FFMPEG_OPTIONS), data=data)
            if guild.id not in self.queues:
                self.queues[guild.id] = []
            self.queues[guild.id].append(source)
            if not guild.voice_client.is_playing():
                self.play_next_from_api(guild.voice_client, guild.id)
                print(f"[API Play] Reproduciendo ahora: {source.title}")
            else:
                print(f"[API Play] Añadido a la cola: {source.title}")
        except Exception as e:
            print(f"Error en reproducir_desde_api: {e}")

# --- Setup del cog ---
async def setup(bot: commands.Bot):
    await bot.add_cog(MusicaCog(bot))
