import discord
from discord import ui, app_commands
from discord.ext import commands
import datetime
import re
import asyncio # <-- IMPORTANTE: Lo necesitamos para el sleep

# --- Configuración ---
CATEGORIA_TICKETS_NOMBRE = "📨 TICKETS" # Nombre de la categoría donde se crearán los tickets
LOG_CANAL_NOMBRE = "🔧・registros-staff" # Canal donde se logueará la creación de tickets

# --- Nombres de roles para el sistema de verificación (de cogs/sistema_verificacion.py) ---
ROL_VERIFICADO_NOMBRE = "FML | Verificado"
ROL_REVISION_NOMBRE = "FML | En revision"
ROL_STAFF_NOMBRE = "FML | Staff" # <-- Añadido para la creación de tickets

# --- URL de tu imagen ---
URL_IMAGEN_BANNER = "https://cdn.discordapp.com/attachments/1413161019269972158/1433247256185667606/IMG_2265.jpg?ex=6904a7c6&is=69035646&hm=e615901588ef58117e82af8b11c9f219b34a96329f93d3348e68fdd4bb1f77fd"


# --- [NUEVO] Botón de Cierre para DENTRO del ticket ---
class TicketCloseView(ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Persistente

    @ui.button(label="Cerrar Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket_button_fml")
    async def cerrar_ticket_button(self, interaction: discord.Interaction, button: ui.Button):
        channel = interaction.channel
        
        # --- Permiso ---
        # Solo staff (con permiso de kick) puede cerrar
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message("❌ Solo el Staff puede cerrar un ticket.", ephemeral=True)
            return

        # Desactivar botones (para evitar doble clic)
        button.disabled = True
        button.label = "Cerrando..."
        await interaction.response.edit_message(view=self)

        await channel.send(f"Ticket marcado para cerrar por {interaction.user.mention}. Eliminando en 5 segundos...")
        await asyncio.sleep(5)
        
        try:
            await channel.delete(reason=f"Ticket cerrado por {interaction.user.name}")
        except Exception as e:
            # Si falla (ej. borrado manual), que lo sepa el admin
            try:
                await interaction.followup.send(f"Error al borrar el canal (quizás ya fue borrado): {e}", ephemeral=True)
            except:
                pass # El canal/interacción ya no existe


# --- Menú desplegable para seleccionar el tipo de ticket ---
class TicketSelect(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Soporte General", description="Ayuda general, dudas sobre el servidor o Discord.", value="soporte", emoji="🙋"),
            discord.SelectOption(label="Alianza de Bandas", description="Formulario para iniciar diplomacia o alianza.", value="alianza", emoji="🤝"),
            discord.SelectOption(label="Reportar a un Usuario", description="Reportar a un miembro por romper las reglas (MG, PG, RDM, etc.)", value="reporte", emoji="🚩"),
        ]
        super().__init__(placeholder="Selecciona una categoría...", options=options, custom_id="ticket_category_select")

    async def callback(self, interaction: discord.Interaction):
        await self.create_ticket(interaction, self.values[0])

    async def create_ticket(self, interaction: discord.Interaction, category_value: str):
        guild = interaction.guild
        user = interaction.user
        
        staff_role = discord.utils.get(guild.roles, name=ROL_STAFF_NOMBRE)
        everyone_role = guild.default_role

        if not staff_role:
            await interaction.response.send_message(f"❌ Error: No se encontró el rol `{ROL_STAFF_NOMBRE}`. Avisa a un admin.", ephemeral=True)
            return

        ticket_category = discord.utils.get(guild.categories, name=CATEGORIA_TICKETS_NOMBRE)
        if not ticket_category:
            try:
                category_overwrites = {
                    everyone_role: discord.PermissionOverwrite(view_channel=False),
                    staff_role: discord.PermissionOverwrite(view_channel=True)
                }
                ticket_category = await guild.create_category(CATEGORIA_TICKETS_NOMBRE, overwrites=category_overwrites)
            except discord.Forbidden:
                await interaction.response.send_message("❌ Error: El bot no tiene permisos para crear categorías.", ephemeral=True)
                return

        channel_overwrites = {
            everyone_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        ticket_name = f"{category_value}-{user.name}"
        try:
            ticket_channel = await guild.create_text_channel(
                name=ticket_name,
                category=ticket_category,
                overwrites=channel_overwrites,
                topic=f"Ticket de {user.name} ({user.id}) | Categoría: {category_value}"
            )
        except discord.Forbidden:
            await interaction.response.send_message("❌ Error: El bot no tiene permisos para crear canales.", ephemeral=True)
            return

        await interaction.response.send_message(f"✅ ¡Tu ticket ha sido creado en {ticket_channel.mention}!", ephemeral=True)

        embed = discord.Embed(
            title=f"Ticket de {category_value.capitalize()} Abierto",
            description=f"¡Hola {user.mention}!\n\n"
                        f"Por favor, describe tu solicitud o problema en detalle. Un miembro de {staff_role.mention} te atenderá pronto.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(text="Un Staff cerrará este ticket cuando se resuelva.") # <-- Texto del footer cambiado
        
        if category_value == "alianza":
            embed.add_field(name="Información Requerida", value="Por favor, indica:\n- Nombre de tu banda:\n- Líder de la banda (con @Discord):\n- Motivo de la alianza:", inline=False)
        elif category_value == "reporte":
            embed.add_field(name="Información Requerida", value="Por favor, indica:\n- Usuario reportado (con @Discord):\n- Regla rota:\n- Pruebas (clips, fotos, etc.):\n- Descripción detallada de lo sucedido:", inline=False)

        # --- [CAMBIO CLAVE] ---
        # Enviamos el mensaje de bienvenida CON el botón de cerrar
        await ticket_channel.send(content=f"{user.mention} {staff_role.mention}", embed=embed, view=TicketCloseView())
        
        log_channel = discord.utils.get(guild.channels, name=LOG_CANAL_NOMBRE)
        if log_channel:
            log_embed = discord.Embed(
                title="Nuevo Ticket Creado",
                description=f"**Usuario:** {user.mention}\n**Tipo:** {category_value}\n**Canal:** {ticket_channel.mention}",
                color=discord.Color.blue()
            )
            await log_channel.send(embed=log_embed)

# --- Vista del Panel (la que tiene el menú desplegable) ---
class TicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Persistente
        self.add_item(TicketSelect())

# --- El Cog de Tickets ---
class TicketCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.add_view(TicketView()) # Vista para el panel
        self.bot.add_view(TicketCloseView()) # Vista para el botón de cerrar
        print("Cog de Tickets cargado.")

    # --- Comando /ticket_panel ---
    @app_commands.command(name="ticket_panel", description="[STAFF] Muestra el panel para que los usuarios abran tickets.")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket_panel(self, interaction: discord.Interaction, canal: discord.TextChannel = None):
        if canal is None:
            canal = interaction.channel

        embed = discord.Embed(
            title="Centro de Soporte de La Famili",
            description="¿Necesitas ayuda, quieres proponer una alianza o reportar a un miembro?\n\n"
                        "Selecciona la categoría correcta en el menú de abajo para crear un ticket privado.",
            color=discord.Color.gold()
        )
        embed.set_image(url=URL_IMAGEN_BANNER)
        embed.set_footer(text="Tu ticket solo será visible para ti y el Staff.")
        
        await canal.send(embed=embed, view=TicketView())
        await interaction.response.send_message(f"Panel de tickets enviado a {canal.mention}", ephemeral=True)

    # --- Comando /cerrar ELIMINADO ---
    # (Ya no lo necesitamos, usamos el botón)
            
    # Manejador de errores para este Cog
    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ No tienes los permisos de staff necesarios para usar este comando.", ephemeral=True)
        else:
            print(f"Error en comando de ticket: {error}")
            await interaction.response.send_message(f"Ocurrió un error con este comando.", ephemeral=True)

# --- Función setup OBLIGATORIA ---
async def setup(bot: commands.Bot):
    await bot.add_cog(TicketCog(bot))