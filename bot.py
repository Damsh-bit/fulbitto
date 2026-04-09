import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=["$", "!"], intents=intents, help_command=None)

COGS = ["cogs.cards", "cogs.collection", "cogs.social", "cogs.admin"]

@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name="⚽ $roll | $ayuda"
        )
    )
    print(f"✅ Bot conectado como {bot.user} (ID: {bot.user.id})")
    print(f"🌐 En {len(bot.guilds)} servidor(es)")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        minutos = int(error.retry_after // 60)
        segundos = int(error.retry_after % 60)
        tiempo = f"{minutos}m {segundos}s" if minutos > 0 else f"{segundos}s"
        embed = discord.Embed(
            description=f"⏳ **¡Espera {tiempo}** antes de volver a tirar!",
            color=0xE74C3C
        )
        await ctx.send(embed=embed, delete_after=10)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Argumento faltante. Usa `$ayuda` para ver los comandos.", delete_after=8)
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ Argumento inválido.", delete_after=8)
    elif isinstance(error, commands.CommandNotFound):
        pass  # Ignorar comandos desconocidos
    else:
        print(f"Error no manejado: {error}")

async def main():
    async with bot:
        for cog in COGS:
            try:
                await bot.load_extension(cog)
                print(f"  ✅ Cog cargado: {cog}")
            except Exception as e:
                print(f"  ❌ Error cargando {cog}: {e}")
        
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            raise ValueError("❌ No se encontró DISCORD_TOKEN en el archivo .env")
        
        await bot.start(token)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
