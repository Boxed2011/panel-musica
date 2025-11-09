import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio
from datetime import datetime, timedelta

class DiversionCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("Cog de Diversión cargado.")

    # --- Comando /moneda (ya lo tenías) ---
    @app_commands.command(name="moneda", description="Lanza una moneda.")
    async def moneda(self, interaction: discord.Interaction):
        if random.choice(["cara", "cruz"]) == "cara":
            await interaction.response.send_message("¡Ha salido **Cara**! 🪙")
        else:
            await interaction.response.send_message("¡Ha salido **Cruz**! 🪙")


# Función setup para cargar el Cog
async def setup(bot: commands.Bot):
    await bot.add_cog(DiversionCog(bot))