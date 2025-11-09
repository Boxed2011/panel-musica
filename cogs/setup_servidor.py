import discord
from discord import app_commands
from discord.ext import commands
from config import ID_DEL_SERVIDOR, ID_DEL_OWNER

# Importar la vista de verificación
from .sistema_verificacion import VerificationView

# --- LISTA DE ROLES CON SEPARADORES ---
LISTA_DE_ROLES = [
    "--- 👑 JEFATURA 👑 ---",
    "@perra ardiente", "@owner", "@Co-owner", "@Jefe", "@Sub Jefe",
    "@FML | Sub Jefe", "@FML | admin",
    "--- 🛡️ STAFF 🛡️ ---",
    "FML | Staff", "FML | Encargado de verificacion", "FML | Mano derecha",
    "--- 💎 RANGOS ALTOS 💎 ---",
    "FML | Patron", "FML | Patron en pruebas",
    "FML | Encargado de planes", "FML | Encargado de robos",
    "FML | Capo", "FML | Sub capo",
    "--- 🔰 MIEMBROS 🔰 ---",
    "FML | Sicario", "FML | Empresario legitimo",
    "FML | Soplon", "FML | Verificado",
    "--- ⏳ INGRESO ⏳ ---",
    "FML | Postulante", "FML | En revision", "FML | No verificado"
]

# --- COLORES DE ROLES ---
ROLE_COLORS = {
    "--- 👑 JEFATURA 👑 ---": discord.Color.from_rgb(255, 255, 255), "--- 🛡️ STAFF 🛡️ ---": discord.Color.from_rgb(255, 255, 255),
    "--- 💎 RANGOS ALTOS 💎 ---": discord.Color.from_rgb(255, 255, 255), "--- 🔰 MIEMBROS 🔰 ---": discord.Color.from_rgb(255, 255, 255),
    "--- ⏳ INGRESO ⏳ ---": discord.Color.from_rgb(170, 170, 170),
    "@perra ardiente": discord.Color.from_rgb(255, 0, 0), "@owner": discord.Color.from_rgb(230, 0, 0),
    "@Co-owner": discord.Color.from_rgb(200, 0, 0), "@Jefe": discord.Color.from_rgb(180, 0, 0),
    "@Sub Jefe": discord.Color.from_rgb(160, 0, 0), "@FML | Sub Jefe": discord.Color.from_rgb(150, 0, 0),
    "@FML | admin": discord.Color.blue(), "FML | Staff": discord.Color.from_rgb(0, 150, 255),
    "FML | Patron": discord.Color.gold(), "FML | Patron en pruebas": discord.Color.from_rgb(255, 190, 0),
    "FML | Mano derecha": discord.Color.orange(), "FML | Capo": discord.Color.from_rgb(255, 120, 0),
    "FML | Sub capo": discord.Color.dark_orange(), "FML | Encargado de verificacion": discord.Color.purple(),
    "FML | Encargado de planes": discord.Color.dark_purple(), "FML | Encargado de robos": discord.Color.from_rgb(100, 0, 150),
    "FML | Empresario legitimo": discord.Color.green(), "FML | Sicario": discord.Color.dark_green(),
    "FML | Verificado": discord.Color.from_rgb(0, 180, 0), "FML | Soplon": discord.Color.dark_grey(),
    "FML | Postulante": discord.Color.light_grey(), "FML | En revision": discord.Color.from_rgb(100, 100, 100),
    "FML | No verificado": discord.Color.from_rgb(70, 70, 70),
}
ROLES_ADMIN = ["@perra ardiente", "@owner", "@Co-owner", "@Jefe", "@FML | admin"]
ROLES_STAFF = ["@Sub Jefe", "@FML | Sub Jefe", "FML | Staff", "FML | Encargado de verificacion", "FML | Mano derecha"]
CATEGORIAS_Y_CANALES = {
    "🏛️ BIENVENIDA": [("texto", "📜・reglamento"), ("texto", "✅・verificacion"), ("texto", "🌐・guia-servidor")],
    "🤵 RECLUTAMIENTO": [("texto", "📋・como-ingresar"), ("texto", "🤵・postulaciones"), ("voz", "🔊 Entrevistas")],
    "📢 ZONA PÚBLICA": [("texto", "📢・anuncios"), ("texto", "👑・jerarquia-oficial"), ("texto", "🤝・diplomacia"), ("texto", "💡・sugerencias")],
    "--- (IC) IN CHARACTER ---": [("texto", "🎬・el-barrio"), ("texto", "📍・ubicaciones"), ("texto", "💼・negocios"), ("texto", "📸・memorias-ic")],
    "--- (OOC) OUT OF CHARACTER ---": [("texto", "💬・chat-general"), ("texto", "👾・memes-y-clips"), ("texto", "🎮・otros-juegos")],
    "📈 OPERACIONES FML": [("texto", "🎯・misiones-y-planes"), ("texto", "📦・logistica"), ("texto", "🗓️・reporte-ausencias")],
    "🍸 ZONA SOCIAL (VOZ)": [("voz", "🔊 🗣️・La Cantina"), ("voz", "🔊 🗣️・El Patio"), ("voz", "🔊 📻・Radio Operaciones 1"), ("voz", "🔊 📻・Radio Operaciones 2"), ("voz", "🔊 🎶・Sala de Música"), ("texto", "🎵・comandos-musica"), ("voz", "🔊 💤・AFK")],
    "🔒 GESTIÓN DE STAFF": [("texto", "🔒・chat-staff"), ("texto", "🔧・registros-staff"), ("texto", "📑・postulantes-revision")],
    "👑 ALTO MANDO": [("texto", "👑・chat-jefatura"), ("texto", "💰・tesoreria"), ("voz", "🔊 💼・Despacho del Jefe"), ("voz", "🔊 💼・Sala de Juntas")]
}

def is_owner(interaction: discord.Interaction) -> bool:
    return interaction.user.id == ID_DEL_OWNER

class SetupCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.check(is_owner)
    @app_commands.command(name="setup_servidor", description="[SOLO OWNER] Borra y reconstruye el servidor FML.")
    async def setup_servidor_command(self, interaction: discord.Interaction):
        
        if interaction.guild.id != ID_DEL_SERVIDOR:
            await interaction.response.send_message("Este comando no se puede usar en este servidor.", ephemeral=True)
            return

        await interaction.response.send_message("... Iniciando construcción ...\nEl servidor se borrará y reconfigurará. Esto tardará unos 20-30 segundos.", ephemeral=True)
        guild = interaction.guild
        print(f"\n--- ¡CONSTRUCCIÓN INICIADA POR {interaction.user.name}! ---")

        # --- PASO 1: LIMPIAR ROLES Y CANALES ANTIGUOS ---
        print("--- Limpiando todo lo antiguo ---")
        try:
            bot_member = guild.get_member(self.bot.user.id)
            bot_top_role = bot_member.top_role
            for role in guild.roles:
                if role.name != "@everyone" and role != bot_top_role and not role.managed:
                    try: await role.delete(reason="Reinicio de servidor")
                    except: pass
            for channel in guild.channels:
                try: await channel.delete(reason="Reinicio de servidor")
                except: pass
            print("Limpieza completada.")
        except Exception as e:
            print(f"Error durante la limpieza: {e}")

        # --- PASO 2: CREAR ROLES CON PERMISOS Y COLORES ---
        print("--- Creando Roles ---")
        created_roles = {}
        
        for role_name in LISTA_DE_ROLES: 
            color = ROLE_COLORS.get(role_name, discord.Color.default())
            
            if role_name.startswith("---"): perms = discord.Permissions.none()
            elif role_name in ROLES_ADMIN: perms = discord.Permissions(administrator=True)
            elif role_name in ROLES_STAFF:
                perms = discord.Permissions(kick_members=True, ban_members=True, manage_messages=True, manage_nicknames=True, mute_members=True, deafen_members=True, move_members=True, view_audit_log=True)
            elif "FML | Verificado" in role_name:
                perms = discord.Permissions(send_messages=True, embed_links=True, attach_files=True, read_message_history=True, connect=True, speak=True, use_voice_activation=True, change_nickname=True)
            elif "Postulante" in role_name or "En revision" in role_name:
                 perms = discord.Permissions(send_messages=True, read_message_history=True, connect=True, speak=True, use_voice_activation=True)
            else:
                perms = discord.Permissions(send_messages=True, embed_links=True, attach_files=True, read_message_history=True, connect=True, speak=True, use_voice_activation=True, change_nickname=True)
            
            try:
                role = await guild.create_role(name=role_name, color=color, permissions=perms, reason="Setup automático")
                created_roles[role_name] = role
            except Exception as e:
                print(f"Error creando rol {role_name}: {e}")
        print("Roles creados.")

        # --- PASO 2.5: REORDENAR JERARQUÍA ---
        print("--- Reordenando la jerarquía de roles ---")
        try:
            bot_member = guild.get_member(self.bot.user.id)
            if not bot_member:
                print("Error crítico: El bot no está en el servidor.")
                return
            
            top_position = bot_member.top_role.position - 1
            
            positions = {}
            for role_name in LISTA_DE_ROLES:
                if role_name in created_roles:
                    role = created_roles[role_name]
                    positions[role] = top_position
                    top_position -= 1 
            
            await guild.edit_role_positions(positions=positions)
            print("Jerarquía de roles ordenada exitosamente.")
        
        except discord.Forbidden:
             print("Error: El bot no tiene permisos para 'Gestionar Roles' o su rol no es el más alto.")
        except Exception as e:
            print(f"Error reordenando roles: {e}")

        # --- PASO 3: DEFINIR NIVELES DE PERMISOS ---
        print("--- Configurando niveles de permisos ---")
        everyone_role = guild.default_role
        postulante_role = discord.utils.get(guild.roles, name="FML | Postulante")
        en_revision_role = discord.utils.get(guild.roles, name="FML | En revision")
        verificado_role = discord.utils.get(guild.roles, name="FML | Verificado")
        staff_role = discord.utils.get(guild.roles, name="FML | Staff")
        jefe_role = discord.utils.get(guild.roles, name="@Jefe")

        if not all([postulante_role, en_revision_role, verificado_role, staff_role, jefe_role]):
            print("Error: Faltan roles clave. Los permisos de canal pueden fallar.")
            return

        overwrites_gateway = {everyone_role: discord.PermissionOverwrite(read_messages=True, send_messages=False, view_channel=True)}
        overwrites_verificacion = {everyone_role: discord.PermissionOverwrite(read_messages=True, send_messages=False, view_channel=True)}
        overwrites_reclutamiento = {everyone_role: discord.PermissionOverwrite(view_channel=False), postulante_role: discord.PermissionOverwrite(view_channel=True), en_revision_role: discord.PermissionOverwrite(view_channel=True), staff_role: discord.PermissionOverwrite(view_channel=True)}
        overwrites_miembro_general = {everyone_role: discord.PermissionOverwrite(view_channel=False), verificado_role: discord.PermissionOverwrite(view_channel=True, read_messages=True)}
        overwrites_staff = {everyone_role: discord.PermissionOverwrite(view_channel=False), staff_role: discord.PermissionOverwrite(view_channel=True)}
        overwrites_jefatura = {everyone_role: discord.PermissionOverwrite(view_channel=False), staff_role: discord.PermissionOverwrite(view_channel=False), jefe_role: discord.PermissionOverwrite(view_channel=True), created_roles["@owner"]: discord.PermissionOverwrite(view_channel=True), created_roles["@Co-owner"]: discord.PermissionOverwrite(view_channel=True)}

        # --- PASO 4: CREAR CANALES CON PERMISOS ---
        print("--- Creando Estructura de Canales ---")
        verification_channel = None 
        jerarquia_channel = None 
        reglamento_channel = None
        guia_channel = None
        ingresar_channel = None
        
        for categoria_nombre, canales_lista in CATEGORIAS_Y_CANALES.items():
            permisos_categoria = {}
            if categoria_nombre == "🏛️ BIENVENIDA": permisos_categoria = overwrites_gateway
            elif categoria_nombre == "🤵 RECLUTAMIENTO": permisos_categoria = overwrites_reclutamiento
            elif categoria_nombre in ["📢 ZONA PÚBLICA", "--- (IC) IN CHARACTER ---", "--- (OOC) OUT OF CHARACTER ---", "📈 OPERACIONES FML", "🍸 ZONA SOCIAL (VOZ)"]: permisos_categoria = overwrites_miembro_general
            elif categoria_nombre == "🔒 GESTIÓN DE STAFF": permisos_categoria = overwrites_staff
            elif categoria_nombre == "👑 ALTO MANDO": permisos_categoria = overwrites_jefatura
            
            categoria = await guild.create_category(categoria_nombre, overwrites=permisos_categoria)
            print(f"Categoría creada: {categoria_nombre}")

            for tipo, nombre_canal in canales_lista:
                permisos_canal_especial = {}
                if nombre_canal == "✅・verificacion": permisos_canal_especial = overwrites_verificacion
                elif nombre_canal in ["📜・reglamento", "🌐・guia-servidor", "📢・anuncios", "👑・jerarquia-oficial", "📋・como-ingresar"]:
                    permisos_canal_especial[verificado_role] = discord.PermissionOverwrite(send_messages=False)
                    # Hacemos que @everyone tampoco pueda escribir en estos canales
                    permisos_canal_especial[everyone_role] = discord.PermissionOverwrite(send_messages=False)
                elif nombre_canal == "🎵・comandos-musica": permisos_canal_especial[verificado_role] = discord.PermissionOverwrite(send_messages=True)
                elif nombre_canal == "🤵・postulaciones":
                    permisos_canal_especial[postulante_role] = discord.PermissionOverwrite(send_messages=True)
                    permisos_canal_especial[en_revision_role] = discord.PermissionOverwrite(send_messages=True)

                if tipo == "texto": channel = await categoria.create_text_channel(nombre_canal, overwrites=permisos_canal_especial)
                elif tipo == "voz": channel = await categoria.create_voice_channel(nombre_canal)
                
                # Guardamos los canales que necesitamos poblar
                if nombre_canal == "✅・verificacion": verification_channel = channel
                if nombre_canal == "👑・jerarquia-oficial": jerarquia_channel = channel 
                if nombre_canal == "📜・reglamento": reglamento_channel = channel
                if nombre_canal == "🌐・guia-servidor": guia_channel = channel
                if nombre_canal == "📋・como-ingresar": ingresar_channel = channel
        
        # --- [NUEVO] PASO 5: POBLAR CANALES CLAVE ---
        print("--- Poblando canales de información ---")

        # 5.1 Mensaje para #📜・reglamento (Extenso)
        try:
            if reglamento_channel:
                embed_reglas = discord.Embed(title="📜 Reglamento Oficial de La Famili 📜", description="El desconocimiento de estas reglas no exime de su cumplimiento. Al verificarte, aceptas todo lo aquí expuesto.", color=discord.Color.red())
                
                embed_reglas.add_field(name="1. NORMAS BÁSICAS (OOC)", value=
                    "**1.1 Respeto:** Se prohíbe cualquier tipo de insulto, racismo, homofobia, o toxicidad OOC.\n"
                    "**1.2 Canales IC/OOC:** No mezcles información. `IC` (In Character) es tu personaje. `OOC` (Out of Character) eres tú.\n"
                    "**1.3 No Spam/NSFW:** Prohibido el spam, flood, y contenido NSFW fuera de los canales designados (si existen).\n"
                    "**1.4 Jerarquía OOC:** Respeta al Staff y al Alto Mando. Sus decisiones son finales.",
                    inline=False
                )
                
                embed_reglas.add_field(name="2. CONCEPTOS BÁSICOS DE ROLEPLAY (Sancionables)", value=
                    "**2.1 MG (Metagaming):** Usar información OOC (streams, chats de Discord) para beneficio de tu personaje IC. **Sanción grave.**\n"
                    "**2.2 PG (Powergaming):** Forzar acciones de rol sobre otro jugador, evadir rol, o actuar de forma sobrehumana (ej. *'le robo todo y salgo corriendo'* sin darle oportunidad de responder).\n"
                    "**2.3 RDM (Random Deathmatch):** Matar a alguien sin motivo de rol previo, claro y justificado.\n"
                    "**2.4 VDM (Vehicle Deathmatch):** Usar tu vehículo como arma para atropellar o matar sin un motivo de rol claro.\n"
                    "**2.5 NVL (No Valorar la Vida):** No actuar como lo harías en la vida real. Si 3 personas te apuntan con armas, no sacarás un cuchillo. Ríndete y valora la vida de tu personaje.",
                    inline=False
                )
                
                embed_reglas.add_field(name="3. NORMAS DE LA FAMILIA (IC)", value=
                    "**3.1 Lealtad (Omertà):** La Famili es lo primero. La traición o hablar con la policía (CK de soplón) resultará en un CK.\n"
                    "**3.2 Jerarquía IC:** Se debe respetar la cadena de mando. Un Sicario no da órdenes a un Capo.\n"
                    "**3.3 Discreción:** No presumas de actividades ilegales en público. Mantén un perfil bajo. No vistas con máscara y fusil para ir a comprar al 24/7.\n"
                    "**3.4 Conflictos Internos:** Los problemas entre miembros se resuelven internamente, hablando con un superior. No se inician tiroteos entre miembros.",
                    inline=False
                )

                embed_reglas.add_field(name="4. NORMAS DE CONFLICTO (Guerras/Robos)", value=
                    "**4.1 Inicio de Rol:** Siempre debe haber una interacción verbal clara antes de un tiroteo.\n"
                    "**4.2 Robos:** Solo se puede robar lo que el personaje lleva encima. No se puede forzar a sacar dinero del banco.\n"
                    "**4.3 CK (Character Kill):** La muerte permanente de un personaje. Solo puede ser aprobada por el Alto Mando de ambas facciones o por Staff.\n"
                    "**4.4 PK (Player Kill):** Si mueres en un tiroteo, tu personaje \"olvida\" toda la situación que llevó a tu muerte. No puedes volver a la zona del tiroteo por 30 minutos.",
                    inline=False
                )
                
                await reglamento_channel.send(embed=embed_reglas)
            else: print("Error: Canal '📜・reglamento' no encontrado.")
        except Exception as e:
            print(f"Error poblando reglamento: {e}")

        # 5.2 Mensaje para #🌐・guia-servidor
        try:
            if guia_channel:
                embed_guia = discord.Embed(title="🌐 Guía Rápida del Servidor", description="¡Bienvenido! Aquí tienes un mapa de cómo nos organizamos.", color=discord.Color.blue())
                embed_guia.add_field(name="🏛️ BIENVENIDA", value="Tu punto de inicio. Aquí lees las reglas y te verificas.", inline=False)
                embed_guia.add_field(name="🤵 RECLUTAMIENTO", value="Canales visibles durante tu proceso de postulación.", inline=False)
                embed_guia.add_field(name="📢 ZONA PÚBLICA", value="Anuncios, jerarquía y sugerencias. Visible para todos los miembros verificados.", inline=False)
                embed_guia.add_field(name="--- (IC) IN CHARACTER ---", value="**¡El rol ocurre aquí!** Todo lo que se escribe en estos canales es 100% tu personaje.", inline=False)
                embed_guia.add_field(name="--- (OOC) OUT OF CHARACTER ---", value="Chats generales para hablar fuera de personaje, compartir memes, clips, etc.", inline=False)
                embed_guia.add_field(name="📈 OPERACIONES FML", value="Canales de logística y planificación de misiones para miembros.", inline=False)
                embed_guia.add_field(name="🔒 GESTIÓN DE STAFF", value="Canales privados para que el Staff administre el servidor.", inline=False)
                await guia_channel.send(embed=embed_guia)
            else: print("Error: Canal '🌐・guia-servidor' no encontrado.")
        except Exception as e:
            print(f"Error poblando guia: {e}")

        # 5.3 Mensaje para #📋・como-ingresar
        try:
            if ingresar_channel:
                embed_ingreso = discord.Embed(title="📋 Cómo Ingresar a La Famili", description="Sigue estos 4 sencillos pasos para unirte.", color=discord.Color.green())
                embed_ingreso.add_field(name="Paso 1: Leer", value="Lee **TODO** el contenido de `#📜・reglamento` y `#🌐・guia-servidor`. Es obligatorio.", inline=False)
                embed_ingreso.add_field(name="Paso 2: Verificar", value="Ve al canal `#✅・verificacion` y presiona el botón verde 'Iniciar Verificación'.", inline=False)
                embed_ingreso.add_field(name="Paso 3: Rellenar", value="Se te abrirá un formulario. Rellena las preguntas sobre tu personaje y las reglas con seriedad. **Las respuestas de baja calidad serán rechazadas.**", inline=False)
                embed_ingreso.add_field(name="Paso 4: Esperar", value="Tu postulación aparecerá en `#📑・postulantes-revision`. Ten paciencia. Un miembro del Staff te 'Aceptará' o 'Rechazará'.", inline=False)
                await ingresar_channel.send(embed=embed_ingreso)
            else: print("Error: Canal '📋・como-ingresar' no encontrado.")
        except Exception as e:
            print(f"Error poblando como-ingresar: {e}")

        # 5.4 Mensaje para #✅・verificacion (El panel con el botón)
        print("--- Configurando sistema de verificación ---")
        try:
            if verification_channel:
                embed_verif = discord.Embed(title="Verificación de La Famili", description="¡Bienvenido al proceso de ingreso!\n\n1. Lee **TODO** el canal `#📜・reglamento`.\n2. Presiona el botón **'Iniciar Verificación'** para abrir el formulario.\n\n*Tu postulación será revisada por el Alto Mando.*", color=discord.Color.gold())
                await verification_channel.send(embed=embed_verif, view=VerificationView())
            else:
                print("Error: No se pudo postear el panel, canal '✅・verificacion' no encontrado.")
        except Exception as e:
            print(f"Error poblando verificacion: {e}")

        # --- PASO 6: PUBLICAR JERARQUÍA ---
        print("--- Publicando Jerarquía ---")
        try:
            if not jerarquia_channel:
                print("Error: No se encontró el canal '👑・jerarquia-oficial'.")
            else:
                embed_jerarquia = discord.Embed(title="Jerarquía Oficial de La Famili", description="Esta es la estructura de rangos oficial del servidor.", color=discord.Color.gold())
                current_category_name = ""
                category_content = ""

                for role_name in LISTA_DE_ROLES:
                    role = discord.utils.get(guild.roles, name=role_name)
                    if not role: continue
                    if role.name.startswith("---"):
                        if current_category_name:
                            embed_jerarquia.add_field(name=current_category_name, value=category_content, inline=False)
                        current_category_name = role.name
                        category_content = ""
                    else:
                        category_content += f"{role.mention}\n"
                
                if current_category_name:
                    embed_jerarquia.add_field(name=current_category_name, value=category_content, inline=False)

                await jerarquia_channel.send(embed=embed_jerarquia)
                print("Jerarquía publicada exitosamente.")
        except Exception as e:
            print(f"Error al publicar la jerarquía: {e}")

        # --- FIN ---
        print("\n--- ¡CONFIGURACIÓN DEL SERVIDOR COMPLETADA! ---")
        await interaction.followup.send("¡El servidor ha sido construido exitosamente!", ephemeral=True)

    @setup_servidor_command.error
    async def on_setup_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("❌ **Acceso Denegado**\nSolo el propietario del bot puede ejecutar este comando.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Ocurrió un error inesperado: {error}", ephemeral=True)

# Función para registrar el Cog
async def setup(bot: commands.Bot):
    await bot.add_cog(SetupCog(bot))