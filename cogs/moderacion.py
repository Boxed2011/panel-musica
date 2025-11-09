import discord
from discord import app_commands
from discord.ext import commands

# Definimos la clase del Cog (nuestra categoría de comandos)
class ModeracionCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("Cog de Moderación cargado.")

    # --- Comando /kick ---
    @app_commands.command(name="kick", description="Expulsa a un miembro del servidor.")
    @app_commands.describe(miembro="El miembro que quieres expulsar", razon="La razón de la expulsión")
    @app_commands.checks.has_permissions(kick_members=True) # Solo miembros con permiso de kick
    async def kick_command(self, interaction: discord.Interaction, miembro: discord.Member, razon: str = "No se especificó una razón."):
        
        # Comprobaciones de seguridad
        if miembro.id == interaction.user.id:
            await interaction.response.send_message("No te puedes kickear a ti mismo.", ephemeral=True)
            return
        if miembro.id == self.bot.user.id:
            await interaction.response.send_message("No me puedes kickear a mí.", ephemeral=True)
            return
        if miembro.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("No puedes kickear a alguien con un rol igual o superior al tuyo.", ephemeral=True)
            return

        try:
            # Enviar DM al usuario kickeado (opcional pero profesional)
            try:
                await miembro.send(f"Has sido expulsado del servidor **{interaction.guild.name}** por la siguiente razón: {razon}")
            except discord.Forbidden:
                print(f"No se pudo enviar DM a {miembro.name} (DMs cerrados).")

            # Kickear al miembro
            await miembro.kick(reason=f"{razon} (Expulsado por: {interaction.user.name})")
            
            # Mensaje de confirmación en el canal
            embed = discord.Embed(
                title="👟 Miembro Expulsado",
                description=f"**Miembro:** {miembro.mention} (`{miembro.id}`)\n**Razón:** {razon}",
                color=discord.Color.orange()
            )
            embed.set_footer(text=f"Expulsado por: {interaction.user.name}")
            await interaction.response.send_message(embed=embed)

        except discord.Forbidden:
            await interaction.response.send_message("Error: No tengo permisos para kickear a ese miembro. (¿Su rol es más alto que el mío?)", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Ocurrió un error inesperado: {e}", ephemeral=True)

    # --- Comando /ban ---
    @app_commands.command(name="ban", description="Banea a un miembro del servidor.")
    @app_commands.describe(miembro="El miembro que quieres banear", razon="La razón del baneo")
    @app_commands.checks.has_permissions(ban_members=True) # Solo miembros con permiso de ban
    async def ban_command(self, interaction: discord.Interaction, miembro: discord.Member, razon: str = "No se especificó una razón."):
        
        if miembro.id == interaction.user.id:
            await interaction.response.send_message("No te puedes banear a ti mismo.", ephemeral=True)
            return
        
        try:
            # Banners al miembro
            await miembro.ban(reason=f"{razon} (Baneado por: {interaction.user.name})")
            
            # Mensaje de confirmación
            embed = discord.Embed(
                title="🔨 Miembro Baneado",
                description=f"**Miembro:** {miembro.mention} (`{miembro.id}`)\n**Razón:** {razon}",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Baneado por: {interaction.user.name}")
            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message("Error: No tengo permisos para banear a ese miembro.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Ocurrió un error: {e}", ephemeral=True)

    # --- Manejador de errores para este Cog ---
    # Esto captura si alguien intenta usar /kick o /ban sin permisos
    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ No tienes los permisos necesarios para usar este comando.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Ocurrió un error con este comando: {error}", ephemeral=True)


# --- Función setup OBLIGATORIA ---
# Esto es lo que main.py busca para cargar el Cog
async def setup(bot: commands.Bot):
    await bot.add_cog(ModeracionCog(bot))