import discord
from discord.ext import commands
import asyncio
import database as db
from data.players import get_player, RARITIES, search_players

TRADE_TIMEOUT = 60  # segundos para aceptar un intercambio


class Social(commands.Cog, name="🤝 Social"):
    """Comandos para regalar cartas, intercambiar y ver rankings."""

    def __init__(self, bot):
        self.bot = bot
        self.pending_trades: dict = {}  # (user1_id, user2_id) -> trade_data

    # ─── REGALAR ─────────────────────────────────────────────────────────────

    @commands.command(name="regalar", aliases=["give", "donar", "dar"])
    async def give_card(self, ctx, miembro: discord.Member, *, nombre: str):
        """🎁 Regala una carta a otro usuario. Ej: `$regalar @amigo Messi`"""
        if miembro.bot:
            await ctx.send("❌ No puedes regalar cartas a bots.", delete_after=6)
            return
        if miembro == ctx.author:
            await ctx.send("❌ No puedes regalarte cartas a ti mismo.", delete_after=6)
            return

        resultados = search_players(nombre)
        if not resultados:
            await ctx.send(f"❌ No encontré a **{nombre}**.", delete_after=8)
            return

        player = resultados[0]
        tienes = await db.has_card(ctx.author.id, ctx.guild.id, player.id)
        if not tienes:
            await ctx.send(f"❌ No tienes una carta de **{player.name}**.", delete_after=8)
            return

        await db.ensure_user(miembro.id, ctx.guild.id)
        eliminada = await db.remove_one_card(ctx.author.id, ctx.guild.id, player.id)
        if not eliminada:
            await ctx.send("❌ Error al eliminar la carta. Intenta de nuevo.", delete_after=6)
            return

        await db.add_card(miembro.id, ctx.guild.id, player.id)
        r = RARITIES[player.rarity]
        embed = discord.Embed(
            title="🎁 ¡Carta regalada!",
            description=f"{ctx.author.mention} le regaló **{r.emoji} {player.name}** a {miembro.mention}",
            color=r.color
        )
        embed.set_footer(text=f"{player.club} • {player.nation} {player.flag}")
        await ctx.send(embed=embed)

    # ─── INTERCAMBIO ─────────────────────────────────────────────────────────

    @commands.command(name="intercambio", aliases=["trade", "cambio", "swap"])
    async def trade(self, ctx, miembro: discord.Member, carta_tuya: str, *, carta_de_el: str):
        """🔄 Propone un intercambio de cartas. Ej: `$intercambio @amigo Messi Haaland`"""
        if miembro.bot or miembro == ctx.author:
            await ctx.send("❌ Destinatario inválido.", delete_after=6)
            return

        r1 = search_players(carta_tuya)
        r2 = search_players(carta_de_el)
        if not r1 or not r2:
            await ctx.send("❌ No encontré alguno de los jugadores.", delete_after=8)
            return

        p1, p2 = r1[0], r2[0]

        if not await db.has_card(ctx.author.id, ctx.guild.id, p1.id):
            await ctx.send(f"❌ No tienes una carta de **{p1.name}**.", delete_after=8)
            return
        if not await db.has_card(miembro.id, ctx.guild.id, p2.id):
            await ctx.send(f"❌ {miembro.display_name} no tiene una carta de **{p2.name}**.", delete_after=8)
            return

        rar1 = RARITIES[p1.rarity]
        rar2 = RARITIES[p2.rarity]

        embed = discord.Embed(
            title="🔄 Propuesta de Intercambio",
            color=0xE67E22,
            description=(
                f"**{ctx.author.display_name}** ofrece:\n"
                f"> {rar1.emoji} **{p1.name}** ({p1.club})\n\n"
                f"**{miembro.display_name}** daría:\n"
                f"> {rar2.emoji} **{p2.name}** ({p2.club})\n\n"
                f"{miembro.mention}, reacciona ✅ para aceptar o ❌ para rechazar.\n"
                f"Tienes **{TRADE_TIMEOUT} segundos**."
            )
        )
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        def check(reaction, user):
            return (user == miembro
                    and str(reaction.emoji) in ("✅", "❌")
                    and reaction.message.id == msg.id)

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=TRADE_TIMEOUT, check=check)
        except asyncio.TimeoutError:
            embed.description = "⏰ El intercambio expiró sin respuesta."
            embed.color = 0x95A5A6
            await msg.edit(embed=embed)
            return

        if str(reaction.emoji) == "❌":
            embed.description = f"❌ {miembro.display_name} rechazó el intercambio."
            embed.color = 0xE74C3C
            await msg.edit(embed=embed)
            return

        # Ejecutar intercambio
        ok1 = await db.remove_one_card(ctx.author.id, ctx.guild.id, p1.id)
        ok2 = await db.remove_one_card(miembro.id, ctx.guild.id, p2.id)
        if ok1 and ok2:
            await db.add_card(ctx.author.id, ctx.guild.id, p2.id)
            await db.add_card(miembro.id, ctx.guild.id, p1.id)
            embed.description = (
                f"✅ **¡Intercambio exitoso!**\n\n"
                f"{ctx.author.display_name} → recibió **{p2.name}** {rar2.emoji}\n"
                f"{miembro.display_name} → recibió **{p1.name}** {rar1.emoji}"
            )
            embed.color = 0x2ECC71
        else:
            embed.description = "❌ Error durante el intercambio. Inténtalo de nuevo."
            embed.color = 0xE74C3C
            # Revertir si algo falló
            if ok1:
                await db.add_card(ctx.author.id, ctx.guild.id, p1.id)
            if ok2:
                await db.add_card(miembro.id, ctx.guild.id, p2.id)

        await msg.edit(embed=embed)

    # ─── RANKING ─────────────────────────────────────────────────────────────

    @commands.command(name="top", aliases=["ranking", "leaderboard", "lb"])
    async def leaderboard(self, ctx):
        """🏆 Ranking de coleccionistas del servidor."""
        top = await db.get_top_collectors(ctx.guild.id, 10)
        if not top:
            await ctx.send("📭 Nadie tiene cartas todavía. ¡Sé el primero con `$roll`!")
            return

        embed = discord.Embed(
            title=f"🏆 Top coleccionistas de {ctx.guild.name}",
            color=0xFFD700
        )
        medallas = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
        lineas = []
        for i, row in enumerate(top):
            try:
                usuario = await ctx.guild.fetch_member(row["user_id"])
                nombre  = usuario.display_name
            except:
                nombre = f"Usuario #{row['user_id']}"
            lineas.append(
                f"{medallas[i]} **{nombre}** — "
                f"**{row['total']}** cartas | {row['unicos']} únicas"
            )

        embed.description = "\n".join(lineas)
        embed.set_footer(text="Usa $roll para conseguir más cartas")
        await ctx.send(embed=embed)

    @commands.command(name="toppersonajes", aliases=["topjugadores", "masrolados"])
    async def top_players(self, ctx):
        """📈 Los jugadores más rolados en el servidor."""
        top = await db.get_most_rolled_players(ctx.guild.id, 10)
        if not top:
            await ctx.send("📭 Nadie ha rolado todavía.")
            return

        embed = discord.Embed(
            title=f"📈 Jugadores más populares en {ctx.guild.name}",
            color=0x3498DB
        )
        lineas = []
        for i, row in enumerate(top, 1):
            p = get_player(row["player_id"])
            if not p:
                continue
            r = RARITIES[p.rarity]
            lineas.append(f"**{i}.** {r.emoji} **{p.name}** — {row['veces']} veces")

        embed.description = "\n".join(lineas)
        await ctx.send(embed=embed)

    # ─── DUELO ───────────────────────────────────────────────────────────────

    @commands.command(name="duelo", aliases=["batalla", "vs"])
    async def duel(self, ctx, *, nombre1_vs_nombre2: str):
        """⚔️ Compara dos jugadores. Ej: `$duelo Messi vs Ronaldo`"""
        if " vs " not in nombre1_vs_nombre2.lower():
            await ctx.send("❌ Formato correcto: `$duelo Messi vs Ronaldo`", delete_after=8)
            return

        partes  = nombre1_vs_nombre2.lower().split(" vs ", 1)
        r1      = search_players(partes[0].strip())
        r2      = search_players(partes[1].strip())

        if not r1 or not r2:
            await ctx.send("❌ No encontré alguno de los jugadores.", delete_after=8)
            return

        p1, p2  = r1[0], r2[0]
        rar1    = RARITIES[p1.rarity]
        rar2    = RARITIES[p2.rarity]

        def stat_line(label, v1, v2):
            w1 = "**" if v1 > v2 else ""
            w2 = "**" if v2 > v1 else ""
            e1 = "**" if v1 > v2 else ""
            e2 = "**" if v2 > v1 else ""
            return f"`{label:<10}` {w1}{v1:>3}{e1} │ {w2}{v2:>3}{e2}"

        stats_txt = "\n".join([
            stat_line("Overall",  p1.overall,   p2.overall),
            stat_line("Ritmo",    p1.pace,       p2.pace),
            stat_line("Disparo",  p1.shooting,   p2.shooting),
            stat_line("Pase",     p1.passing,    p2.passing),
            stat_line("Regate",   p1.dribbling,  p2.dribbling),
            stat_line("Defensa",  p1.defending,  p2.defending),
            stat_line("Físico",   p1.physical,   p2.physical),
        ])

        ganador = p1 if p1.overall >= p2.overall else p2

        embed = discord.Embed(
            title=f"⚔️ {p1.name} vs {p2.name}",
            color=0xE74C3C,
            description=f"```\n{'':10} {p1.name[:8]:>8} │ {p2.name[:8]:<8}\n{'-'*32}\n{stats_txt}\n```"
        )
        embed.add_field(
            name="🏆 Ganador por Overall",
            value=f"{RARITIES[ganador.rarity].emoji} **{ganador.name}**",
            inline=False
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Social(bot))
