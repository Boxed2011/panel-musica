import discord
from discord import app_commands
from discord.ext import commands
import time # Usaremos esto para el comando de ping más preciso

# Definimos la clase del Cog (nuestra categoría de comandos)
class UtilidadCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("Cog de Utilidad cargado.")

    # --- Comando /ping ---
    # Muestra la latencia del bot. Esencial para ver si el bot está laggeado.
    @app_commands.command(name="ping", description="Comprueba la latencia del bot.")
    async def ping_command(self, interaction: discord.Interaction):
        # Mide el tiempo antes de enviar el mensaje
        start_time = time.time()
        
        # Envía un mensaje inicial (ephemeral)
        await interaction.response.send_message("Midiendo latencia...", ephemeral=True)
        
        # Mide el tiempo después de que Discord responde
        end_time = time.time()
        
        # Calcula la latencia del API de Discord
        api_latency = round(self.bot.latency * 1000) # Latencia del "corazón" del bot
        # Calcula la latencia de ida y vuelta del mensaje
        response_latency = round((end_time - start_time) * 1000)
        
        # Edita el mensaje original con los resultados
        await interaction.edit_original_response(
            content=f"¡Pong! 🏓\n"
                    f"Latencia del API (WebSocket): **{api_latency}ms**\n"
                    f"Latencia de respuesta (Cliente ↔️ Discord): **{response_latency}ms**"
        )

    # --- Comando /avatar ---
    # Muestra el avatar de un usuario (o el tuyo si no mencionas a nadie)
    @app_commands.command(name="avatar", description="Muestra el avatar de un miembro.")
    @app_commands.describe(miembro="El miembro del que quieres ver el avatar (opcional)")
    async def avatar_command(self, interaction: discord.Interaction, miembro: discord.Member = None):
        # Si no se especifica un miembro, usa el autor del comando
        if miembro is None:
            miembro = interaction.user

        # Crea un Embed (mensaje bonito)
        embed = discord.Embed(
            title=f"Avatar de {miembro.display_name}",
            color=miembro.color # Usa el color del rol más alto del miembro
        )
        embed.set_image(url=miembro.display_avatar.url) # Pone el avatar como imagen
        embed.set_footer(text=f"Solicitado por: {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed)

    # --- Comando /userinfo ---
    # Muestra información detallada de un usuario
    @app_commands.command(name="userinfo", description="Muestra información detallada de un miembro.")
    @app_commands.describe(miembro="El miembro del que quieres ver la información (opcional)")
    async def userinfo_command(self, interaction: discord.Interaction, miembro: discord.Member = None):
        if miembro is None:
            miembro = interaction.user

        embed = discord.Embed(
            title=f"Información de {miembro.display_name}",
            color=miembro.color
        )
        embed.set_thumbnail(url=miembro.display_avatar.url) # Miniatura
        
        embed.add_field(name="📋 Nombre de Usuario", value=f"`{miembro.name}`", inline=True)
        embed.add_field(name="🆔 ID de Usuario", value=f"`{miembro.id}`", inline=True)
        embed.add_field(name="👑 Rol más alto", value=miembro.top_role.mention, inline=False)
        
        # discord.utils.format_dt() formatea la fecha en un estilo que Discord entiende
        # 'R' significa "Relativo" (ej. "hace 2 meses")
        embed.add_field(name="🗓️ Se unió al servidor", value=discord.utils.format_dt(miembro.joined_at, style='R'), inline=True)
        embed.add_field(name="🎂 Creó su cuenta", value=discord.utils.format_dt(miembro.created_at, style='R'), inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True) # Ephemeral para no spamear

    # --- Comando /decir (Admin) ---
    # Un comando para que el bot envíe un mensaje en un canal específico
    @app_commands.command(name="decir", description="[STAFF] Envía un mensaje como el bot en un canal.")
    @app_commands.describe(canal="El canal donde se enviará el mensaje.", mensaje="El texto que quieres que diga el bot.")
    @app_commands.checks.has_permissions(manage_messages=True) # Solo staff con permiso de "Gestionar Mensajes"
    async def decir_command(self, interaction: discord.Interaction, canal: discord.TextChannel, mensaje: str):
        
        # Crea un Embed para que se vea más profesional
        embed = discord.Embed(
            description=mensaje,
            color=discord.Color.blue() # Puedes cambiar el color
        )
        
        try:
            await canal.send(embed=embed)
            await interaction.response.send_message(f"✅ Mensaje enviado exitosamente a {canal.mention}.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Error: No tengo permisos para hablar en ese canal.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Ocurrió un error: {e}", ephemeral=True)

    # --- Manejador de errores para este Cog ---
    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ No tienes los permisos necesarios para usar este comando.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Ocurrió un error con este comando: {error}", ephemeral=True)
            print(f"Error en comando de utilidad: {error}") # Para que lo veas en tu consola


# --- Función setup OBLIGATORIA ---
# Esto es lo que main.py busca para cargar el Cog
async def setup(bot: commands.Bot):
    await bot.add_cog(UtilidadCog(bot))