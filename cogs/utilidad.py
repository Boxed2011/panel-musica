import discord
from discord import app_commands
from discord.ext import commands
import time

class UtilidadCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("Cog de Utilidad cargado.")

    # --- Comando /ping ---
    @app_commands.command(name="ping", description="Comprueba la latencia del bot.")
    async def ping_command(self, interaction: discord.Interaction):
        start_time = time.time()
        await interaction.response.send_message("Midiendo latencia...", ephemeral=True)
        end_time = time.time()
        api_latency = round(self.bot.latency * 1000)
        response_latency = round((end_time - start_time) * 1000)
        await interaction.edit_original_response(
            content=f"¡Pong! 🏓\n"
                    f"Latencia del API (WebSocket): **{api_latency}ms**\n"
                    f"Latencia de respuesta (Cliente ↔️ Discord): **{response_latency}ms**"
        )

    # --- Comando /avatar ---
    @app_commands.command(name="avatar", description="Muestra el avatar de un miembro.")
    @app_commands.describe(miembro="El miembro del que quieres ver el avatar (opcional)")
    async def avatar_command(self, interaction: discord.Interaction, miembro: discord.Member = None):
        miembro = miembro or interaction.user
        embed = discord.Embed(
            title=f"Avatar de {miembro.display_name}",
            color=miembro.color
        )
        embed.set_image(url=miembro.display_avatar.url)
        embed.set_footer(text=f"Solicitado por: {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

    # --- Comando /userinfo ---
    @app_commands.command(name="userinfo", description="Muestra información detallada de un miembro.")
    @app_commands.describe(miembro="El miembro del que quieres ver la información (opcional)")
    async def userinfo_command(self, interaction: discord.Interaction, miembro: discord.Member = None):
        miembro = miembro or interaction.user
        embed = discord.Embed(
            title=f"Información de {miembro.display_name}",
            color=miembro.color
        )
        embed.set_thumbnail(url=miembro.display_avatar.url)
        embed.add_field(name="📋 Nombre de Usuario", value=f"`{miembro.name}`", inline=True)
        embed.add_field(name="🆔 ID de Usuario", value=f"`{miembro.id}`", inline=True)
        embed.add_field(name="👑 Rol más alto", value=miembro.top_role.mention, inline=False)
        embed.add_field(name="🗓️ Se unió al servidor", value=discord.utils.format_dt(miembro.joined_at, style='R'), inline=True)
        embed.add_field(name="🎂 Creó su cuenta", value=discord.utils.format_dt(miembro.created_at, style='R'), inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # --- Comando /decir (Admin) ---
    @app_commands.command(name="decir", description="[STAFF] Envía un mensaje como el bot en un canal.")
    @app_commands.describe(canal="El canal donde se enviará el mensaje.", mensaje="El texto que quieres que diga el bot.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def decir_command(self, interaction: discord.Interaction, canal: discord.TextChannel, mensaje: str):
        embed = discord.Embed(description=mensaje, color=discord.Color.blue())
        try:
            await canal.send(embed=embed)
            # Aquí usamos followup porque interaction ya fue respondido
            await interaction.response.send_message(f"✅ Mensaje enviado a {canal.mention}.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("❌ Error: No tengo permisos para hablar en ese canal.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Ocurrió un error: {e}", ephemeral=True)

    # --- Manejador de errores ---
    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ No tienes los permisos necesarios para usar este comando.", ephemeral=True)
        else:
            # Para errores después de la primera respuesta usamos followup
            try:
                await interaction.response.send_message(f"Ocurrió un error con este comando: {error}", ephemeral=True)
            except discord.errors.InteractionResponded:
                await interaction.followup.send(f"Ocurrió un error con este comando: {error}", ephemeral=True)
            print(f"Error en comando de utilidad: {error}")

# Setup del Cog
async def setup(bot: commands.Bot):
    await bot.add_cog(UtilidadCog(bot))
