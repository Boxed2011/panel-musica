import discord
from discord.ext import commands
import os
import asyncio
from panel_api import iniciar_servidor_api
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.reactions = True
intents.message_content = True

class LaFamiliBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        print("Cargando cogs...")
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and not filename.startswith('__'):
                cog_name = f'cogs.{filename[:-3]}'
                try:
                    await self.load_extension(cog_name)
                    print(f'Cog cargado: {cog_name}')
                except Exception as e:
                    print(f'Error cargando {cog_name}: {e}')

        # Sincronizar comandos globales
        try:
            await self.tree.sync()
            print("Comandos sincronizados globalmente")
        except Exception as e:
            print(f"Error sincronizando comandos: {e}")

    async def on_ready(self):
        print(f'Bot {self.user} listo. ID: {self.user.id}')
        await self.change_presence(activity=discord.Game(name="Supervisando La Famili"))
        # Iniciar servidor Flask para la web
        iniciar_servidor_api(self)

async def main():
    if not TOKEN:
        print("Error: TOKEN no encontrado en .env")
        return
    bot = LaFamiliBot()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
