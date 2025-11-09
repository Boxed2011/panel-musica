import discord
from discord import ui, app_commands
from discord.ext import commands
import re 

# --- Nombres de Canales y Roles (Configuración) ---
CANAL_REVISION_NOMBRE = "📑・postulantes-revision"
ROL_VERIFICADO_NOMBRE = "FML | Verificado"
ROL_REVISION_NOMBRE = "FML | En revision"
# ROL_STAFF_PERMISO = "FML | Staff" # <- Ya no usamos esto

# --- Vista de Botones para el Staff (Aceptar/Rechazar) ---
class StaffReviewView(ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Botones persistentes

    async def _get_context(self, interaction: discord.Interaction):
        """Función helper para obtener los objetos clave."""
        
        # --- [CAMBIO CLAVE] ---
        # 1. Comprobar permisos del Staff
        # Cualquiera que pueda "Expulsar Miembros" puede aceptar/rechazar.
        # Esto incluye a @Sub Jefe y todo tu staff.
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message(
                f"❌ No tienes permisos de staff para usar estos botones.",
                ephemeral=True
            )
            return None, None, None, None
        # --- Fin del cambio ---

        # 2. Extraer el ID del miembro desde el embed
        try:
            embed = interaction.message.embeds[0]
            match = re.search(r'ID de Usuario: (\d+)', embed.footer.text)
            if not match:
                raise ValueError("No se encontró el ID de usuario en el footer del embed.")
            
            member_id = int(match.group(1))
            member = interaction.guild.get_member(member_id)
            
            if not member:
                await interaction.response.send_message("❌ Error: No se pudo encontrar a ese miembro. Es probable que haya abandonado el servidor.", ephemeral=True)
                return None, None, None, None

        except (IndexError, ValueError, AttributeError) as e:
            print(f"Error extrayendo ID: {e}")
            await interaction.response.send_message(f"❌ Error crítico: No se pudo leer el ID del usuario desde el embed.", ephemeral=True)
            return None, None, None, None

        # 3. Obtener roles
        rol_verificado = discord.utils.get(interaction.guild.roles, name=ROL_VERIFICADO_NOMBRE)
        rol_revision = discord.utils.get(interaction.guild.roles, name=ROL_REVISION_NOMBRE)

        if not rol_verificado or not rol_revision:
            await interaction.response.send_message("❌ Error de configuración: No se encontró el rol verificado o el rol de revisión.", ephemeral=True)
            return None, None, None, None
            
        return member, rol_verificado, rol_revision, embed

    @ui.button(label="Aceptar", style=discord.ButtonStyle.success, custom_id="review_accept_button")
    async def aceptar_button(self, interaction: discord.Interaction, button: ui.Button):
        
        member, rol_verificado, rol_revision, embed = await self._get_context(interaction)
        if not member: return # El error ya fue enviado
        
        try:
            await member.add_roles(rol_verificado, reason=f"Postulación aceptada por {interaction.user.name}")
            await member.remove_roles(rol_revision, reason="Postulación aceptada")
            
            try:
                await member.send(f"¡Felicidades! Tu postulación en **{interaction.guild.name}** ha sido **ACEPTADA**. Ya tienes acceso al servidor.")
            except discord.Forbidden:
                print(f"No se pudo enviar DM de bienvenida a {member.name}")

            embed.title = f"Postulación ACEPTADA de: {member.name}"
            embed.color = discord.Color.green()
            embed.set_footer(text=f"Aceptado por: {interaction.user.name}")

            for child in self.children:
                child.disabled = True
            
            await interaction.response.edit_message(embed=embed, view=self)

        except discord.Forbidden:
            await interaction.response.send_message("❌ Error: No tengo permisos para cambiar los roles de ese miembro.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Ocurrió un error inesperado: {e}", ephemeral=True)


    @ui.button(label="Rechazar", style=discord.ButtonStyle.danger, custom_id="review_reject_button")
    async def rechazar_button(self, interaction: discord.Interaction, button: ui.Button):

        member, _, rol_revision, embed = await self._get_context(interaction)
        if not member: return

        try:
            await member.remove_roles(rol_revision, reason=f"Postulación rechazada por {interaction.user.name}")

            try:
                await member.send(f"Lo sentimos, tu postulación en **{interaction.guild.name}** ha sido **RECHAZADA**.")
            except discord.Forbidden:
                print(f"No se pudo enviar DM de rechazo a {member.name}")

            embed.title = f"Postulación RECHAZADA de: {member.name}"
            embed.color = discord.Color.red()
            embed.set_footer(text=f"Rechazado por: {interaction.user.name}")
            
            for child in self.children:
                child.disabled = True
            
            await interaction.response.edit_message(embed=embed, view=self)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ Error: No tengo permisos para cambiar los roles de ese miembro.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Ocurrió un error inesperado: {e}", ephemeral=True)


# --- El Modal (Panel de Preguntas) ---
class VerificationModal(ui.Modal, title='Cuestionario de La Famili'):
    
    nombre_ic = ui.TextInput(label='Nombre y Apellido (In-Character)', placeholder='Ej: Tony Soprano', style=discord.TextStyle.short, required=True, max_length=50)
    regla_oro = ui.TextInput(label='¿Cuál es la regla de oro de la banda?', placeholder='Escribe la regla aquí...', style=discord.TextStyle.short, required=True, max_length=100)
    concepto_pj = ui.TextInput(label='Breve concepto de tu personaje', placeholder='¿De dónde viene? ¿Por qué se une? ¿Cuáles son sus motivaciones?', style=discord.TextStyle.paragraph, required=True, min_length=50, max_length=500)
    
    async def on_submit(self, interaction: discord.Interaction):
        canal_revision = discord.utils.get(interaction.guild.channels, name=CANAL_REVISION_NOMBRE)
        
        if not canal_revision:
            await interaction.response.send_message(f"Error: No se encontró el canal `{CANAL_REVISION_NOMBRE}`. Avisa a un admin.", ephemeral=True)
            return

        embed = discord.Embed(title=f"Nueva Postulación de: {self.nombre_ic.value}", description=f"**Usuario de Discord:** {interaction.user.mention}", color=discord.Color.gold())
        embed.add_field(name="Nombre IC", value=self.nombre_ic.value, inline=False)
        embed.add_field(name="Regla de Oro", value=self.regla_oro.value, inline=False)
        embed.add_field(name="Concepto de Personaje", value=self.concepto_pj.value, inline=False)
        embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else None)
        embed.set_footer(text=f"ID de Usuario: {interaction.user.id}")

        rol_revision = discord.utils.get(interaction.guild.roles, name=ROL_REVISION_NOMBRE)
        if rol_revision:
            try:
                await interaction.user.add_roles(rol_revision, reason="Postulación enviada")
            except discord.Forbidden:
                await interaction.response.send_message("❌ Error: No pude asignarte el rol 'En Revisión'. Avisa a un admin.", ephemeral=True)
                return
        else:
            await interaction.response.send_message(f"❌ Error: No se encontró el rol `{ROL_REVISION_NOMBRE}`. Avisa a un admin.", ephemeral=True)
            return
            
        await canal_revision.send(embed=embed, view=StaffReviewView())
        
        await interaction.response.send_message("¡Gracias! Tus respuestas han sido enviadas al Alto Mando. Se te asignó el rol 'En Revisión'.\nPor favor, espera pacientemente.", ephemeral=True)

# --- La Vista con el Botón Persistente (para iniciar) ---
class VerificationView(ui.View):
    def __init__(self):
        super().__init__(timeout=None) 

    @ui.button(label='Iniciar Verificación', style=discord.ButtonStyle.success, custom_id='iniciar_verificacion_fml')
    async def verificar_button(self, interaction: discord.Interaction, button: ui.Button):
        rol_verificado = discord.utils.get(interaction.guild.roles, name=ROL_VERIFICADO_NOMBRE)
        rol_revision = discord.utils.get(interaction.guild.roles, name=ROL_REVISION_NOMBRE)

        if rol_verificado in interaction.user.roles:
            await interaction.response.send_message("Ya estás verificado.", ephemeral=True)
            return
        if rol_revision in interaction.user.roles:
            await interaction.response.send_message("Tu postulación ya está 'En Revisión'. Por favor, ten paciencia.", ephemeral=True)
            return
            
        await interaction.response.send_modal(VerificationModal())


# --- El Cog (para cargar las Vistas) ---
class VerificationCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.add_view(VerificationView())
        self.bot.add_view(StaffReviewView()) # AÑADIMOS LA NUEVA VISTA

    @commands.Cog.listener()
    async def on_ready(self):
        print("VerificationCog: Vistas persistentes de verificación y staff listas.")

# --- Función setup OBLIGATORIA ---
async def setup(bot: commands.Bot):
    await bot.add_cog(VerificationCog(bot))