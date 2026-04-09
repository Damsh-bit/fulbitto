import discord
from discord.ext import commands
import time
import asyncio
import database as db
from data.players import roll_player, get_player, RARITIES, PLAYERS, search_players
from .card_generator import generate_fifa_card

# Cooldown de roll: 20 roleos por hora
ROLL_COOLDOWN = 3600  # 1 hora
ROLL_LIMIT    = 20    # máximo de roleos por hora
CLAIM_WINDOW  = 30    # segundos para que alguien reclame un drop


class Cards(commands.Cog, name="⚽ Cartas"):
    """Comandos para rolear y ver cartas de fútbol."""

    def __init__(self, bot):
        self.bot = bot
        self.pending_drops: dict[int, dict] = {}  # guild_id -> {player, message, expires}

    # ─── ROLL ────────────────────────────────────────────────────────────────

    @commands.command(name="roll", aliases=["r", "tirar", "rolear"])
    @commands.cooldown(ROLL_LIMIT, ROLL_COOLDOWN, commands.BucketType.user)
    async def roll_card(self, ctx):
        """🎲 Rueda una carta aleatoria de fútbol."""
        await db.ensure_user(ctx.author.id, ctx.guild.id)

        player = roll_player()
        
        # Generar imagen estilo FIFA
        try:
            card_image = await generate_fifa_card(player)
            loading_msg = await ctx.send(
                content=f"⚽ **{player.name}** — ¡{ctx.author.display_name} consiguió esta carta! Reacciona ⚽ para reclamarla.",
                file=discord.File(card_image, filename="card.png")
            )
        except Exception as e:
            # Fallback: enviar embed si falla la generación de imagen
            print(f"Error generando imagen: {e}")
            embed = self._build_card_embed(player, ctx.author)
            embed.set_footer(text=f"¡{ctx.author.display_name} consiguió esta carta! Reacciona ⚽ para reclamarla.")
            loading_msg = await ctx.send(embed=embed)
        
        await loading_msg.add_reaction("⚽")

        # Guardar drop pendiente
        self.pending_drops[ctx.guild.id] = {
            "player":  player,
            "message": loading_msg,
            "roller":  ctx.author.id,
            "expires": time.time() + CLAIM_WINDOW,
            "claimed": False,
        }

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Maneja el reclamo de cartas con reacción ⚽."""
        if user.bot:
            return
        if str(reaction.emoji) != "⚽":
            return

        guild_id = reaction.message.guild.id if reaction.message.guild else None
        if not guild_id:
            return

        drop = self.pending_drops.get(guild_id)
        if not drop:
            return
        if drop["message"].id != reaction.message.id:
            return
        if drop["claimed"]:
            return
        if time.time() > drop["expires"]:
            return

        # Marcar como reclamado
        drop["claimed"] = True
        player = drop["player"]
        await db.ensure_user(user.id, guild_id)
        await db.add_card(user.id, guild_id, player.id)
        self.pending_drops.pop(guild_id, None)

        rarity = RARITIES[player.rarity]
        embed = self._build_card_embed(player, user)
        embed.set_footer(text=f"✅ ¡{user.display_name} reclamó esta carta!")
        await reaction.message.edit(embed=embed)

    # ─── VER CARTA ───────────────────────────────────────────────────────────

    @commands.command(name="carta", aliases=["card", "jugador", "player"])
    async def view_card(self, ctx, *, nombre: str):
        """🃏 Ver los detalles de un jugador. Ej: `$carta Messi`"""
        resultados = search_players(nombre)
        if not resultados:
            await ctx.send(f"❌ No encontré ningún jugador con **{nombre}**. Usa `$lista` para ver todos.", delete_after=10)
            return
        
        player = resultados[0]  # Primer resultado
        tienes = await db.has_card(ctx.author.id, ctx.guild.id, player.id)
        
        try:
            card_image = await generate_fifa_card(player)
            status = "✅ En tu colección" if tienes else "❌ No tienes"
            await ctx.send(
                content=f"🃏 **{player.name}** ({player.club}) — {status}",
                file=discord.File(card_image, filename="card.png")
            )
        except Exception as e:
            # Fallback: enviar embed si falla la generación de imagen
            print(f"Error generando imagen: {e}")
            embed = self._build_card_embed(player, ctx.author, tienes=tienes)
            await ctx.send(embed=embed)

    # ─── LISTA DE JUGADORES ──────────────────────────────────────────────────

    @commands.command(name="lista", aliases=["list", "jugadores", "cartas"])
    async def list_players(self, ctx, raridad: str = None):
        """📋 Lista todos los jugadores disponibles. Ej: `$lista oro`"""
        from data.players import players_by_rarity, total_players

        if raridad and raridad.lower() in RARITIES:
            grupos = {raridad.lower(): players_by_rarity()[raridad.lower()]}
        else:
            grupos = players_by_rarity()

        embed = discord.Embed(
            title="📋 Jugadores disponibles",
            color=0x2ECC71,
            description=f"Total: **{total_players()} jugadores** | Usa `$carta <nombre>` para ver detalles"
        )

        order = ["legendario", "diamante", "oro", "plata", "bronce"]
        for key in order:
            if key not in grupos:
                continue
            players = grupos[key]
            if not players:
                continue
            r = RARITIES[key]
            nombres = ", ".join(f"`{p.name}`" for p in players)
            embed.add_field(
                name=f"{r.emoji} {r.name} ({r.chance}%) — {r.stars}",
                value=nombres,
                inline=False
            )

        await ctx.send(embed=embed)

    # ─── RARIDADES ───────────────────────────────────────────────────────────

    @commands.command(name="raridades", aliases=["probabilidades", "chances"])
    async def show_rarities(self, ctx):
        """📊 Muestra las probabilidades de cada raridad."""
        embed = discord.Embed(
            title="📊 Probabilidades de raridad",
            color=0x9B59B6,
        )
        for key, r in RARITIES.items():
            embed.add_field(
                name=f"{r.emoji} {r.name}",
                value=f"**{r.chance}%** | {r.stars}",
                inline=True
            )
        embed.set_footer(text="Usa $roll para tirar una carta")
        await ctx.send(embed=embed)

    # ─── HELPER: BUILD EMBED ─────────────────────────────────────────────────

    def _build_card_embed(self, player, user, tienes: bool = None) -> discord.Embed:
        rarity = RARITIES[player.rarity]

        embed = discord.Embed(
            title=f"{rarity.emoji} {player.name}",
            color=rarity.color,
        )

        embed.add_field(name="🏟️ Club",     value=player.club,     inline=True)
        embed.add_field(name="🌍 Nación",   value=f"{player.flag} {player.nation}", inline=True)
        embed.add_field(name="📌 Posición", value=player.position,  inline=True)

        embed.add_field(name="⭐ Overall", value=f"**{player.overall}**", inline=True)
        embed.add_field(name="🏅 Raridad", value=f"{rarity.name} {rarity.stars}", inline=True)
        if tienes is not None:
            embed.add_field(name="📦 En tu colección", value="✅ Sí" if tienes else "❌ No", inline=True)

        stats = (
            f"```\n"
            f"⚡ Ritmo       {player.pace:>3}\n"
            f"🎯 Disparo     {player.shooting:>3}\n"
            f"🎭 Pase        {player.passing:>3}\n"
            f"⚽ Regate      {player.dribbling:>3}\n"
            f"🛡️ Defensa     {player.defending:>3}\n"
            f"💪 Físico      {player.physical:>3}\n"
            f"```"
        )
        embed.add_field(name="📈 Estadísticas", value=stats, inline=False)

        embed.set_thumbnail(url=player.image_url)
        embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        return embed


async def setup(bot):
    await db.init_db()
    await bot.add_cog(Cards(bot))
