import discord
from discord.ext import commands
import math
import database as db
from data.players import get_player, RARITIES, PLAYERS

CARDS_PER_PAGE = 10


class Collection(commands.Cog, name="📦 Colección"):
    """Comandos para ver y gestionar tu colección de cartas."""

    def __init__(self, bot):
        self.bot = bot

    # ─── VER COLECCIÓN ───────────────────────────────────────────────────────

    @commands.command(name="coleccion", aliases=["col", "micsartas", "album"])
    async def view_collection(self, ctx, miembro: discord.Member = None, pagina: int = 1):
        """📦 Ver tu colección de cartas. Ej: `$coleccion` o `$coleccion @amigo`"""
        target = miembro or ctx.author
        await db.ensure_user(target.id, ctx.guild.id)
        
        cartas = await db.get_user_cards(target.id, ctx.guild.id)
        if not cartas:
            msg = "Tu colección está vacía" if target == ctx.author else f"{target.display_name} no tiene cartas"
            await ctx.send(f"📭 **{msg}**. Usa `$roll` para conseguir cartas.")
            return

        total       = len(cartas)
        total_copias = sum(r["cantidad"] for r in cartas)
        total_pags  = math.ceil(total / CARDS_PER_PAGE)
        pagina      = max(1, min(pagina, total_pags))
        inicio      = (pagina - 1) * CARDS_PER_PAGE
        fin         = inicio + CARDS_PER_PAGE
        cartas_pag  = cartas[inicio:fin]

        # Agrupar por raridad para estadísticas
        stats_rarity = {}
        for row in cartas:
            pid   = row["player_id"]
            pdata = get_player(pid)
            if pdata:
                stats_rarity[pdata.rarity] = stats_rarity.get(pdata.rarity, 0) + 1

        embed = discord.Embed(
            title=f"📦 Colección de {target.display_name}",
            color=0x3498DB,
        )

        # Resumen
        resumen_parts = []
        for key in ["legendario", "diamante", "oro", "plata", "bronce"]:
            if key in stats_rarity:
                r = RARITIES[key]
                resumen_parts.append(f"{r.emoji} {stats_rarity[key]}")
        embed.description = (
            f"**{total_copias}** cartas totales | **{total}** únicas\n"
            + " | ".join(resumen_parts)
        )

        # Lista de cartas en esta página
        lineas = []
        for row in cartas_pag:
            pid      = row["player_id"]
            cantidad = row["cantidad"]
            pdata    = get_player(pid)
            if not pdata:
                continue
            r = RARITIES[pdata.rarity]
            cantidad_str = f" x{cantidad}" if cantidad > 1 else ""
            lineas.append(f"{r.emoji} **{pdata.name}** — {pdata.club}{cantidad_str}")

        embed.add_field(
            name=f"Cartas (pág. {pagina}/{total_pags})",
            value="\n".join(lineas) if lineas else "Vacío",
            inline=False
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.set_footer(text=f"Página {pagina}/{total_pags} • $coleccion [usuario] [página]")

        msg = await ctx.send(embed=embed)

        # Paginación con reacciones si hay más de 1 página
        if total_pags > 1:
            await msg.add_reaction("⬅️")
            await msg.add_reaction("➡️")

            def check(reaction, user):
                return (user == ctx.author
                        and str(reaction.emoji) in ("⬅️", "➡️")
                        and reaction.message.id == msg.id)

            current_page = pagina
            import asyncio
            while True:
                try:
                    reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                except asyncio.TimeoutError:
                    break

                if str(reaction.emoji) == "➡️":
                    current_page = min(current_page + 1, total_pags)
                else:
                    current_page = max(current_page - 1, 1)

                inicio_n = (current_page - 1) * CARDS_PER_PAGE
                cartas_n = cartas[inicio_n:inicio_n + CARDS_PER_PAGE]
                lineas_n = []
                for row in cartas_n:
                    pid      = row["player_id"]
                    cantidad = row["cantidad"]
                    pdata    = get_player(pid)
                    if not pdata:
                        continue
                    r = RARITIES[pdata.rarity]
                    cantidad_str = f" x{cantidad}" if cantidad > 1 else ""
                    lineas_n.append(f"{r.emoji} **{pdata.name}** — {pdata.club}{cantidad_str}")

                embed.set_field_at(0,
                    name=f"Cartas (pág. {current_page}/{total_pags})",
                    value="\n".join(lineas_n) if lineas_n else "Vacío",
                    inline=False
                )
                await msg.edit(embed=embed)
                try:
                    await msg.remove_reaction(reaction.emoji, ctx.author)
                except:
                    pass

    # ─── WISHLIST ────────────────────────────────────────────────────────────

    @commands.command(name="desear", aliases=["wish", "quiero"])
    async def wish(self, ctx, *, nombre: str):
        """⭐ Añade un jugador a tu wishlist. Ej: `$desear Messi`"""
        from data.players import search_players
        resultados = search_players(nombre)
        if not resultados:
            await ctx.send(f"❌ No encontré a **{nombre}** en la base de datos.", delete_after=8)
            return

        player = resultados[0]
        await db.ensure_user(ctx.author.id, ctx.guild.id)
        lista = await db.get_wishlist(ctx.author.id, ctx.guild.id)

        if player.id in lista:
            await ctx.send(f"⭐ **{player.name}** ya está en tu wishlist.", delete_after=6)
            return
        if len(lista) >= 10:
            await ctx.send("❌ Tu wishlist ya tiene **10 jugadores** (máximo). Usa `$deseareliminar` para hacer espacio.", delete_after=8)
            return

        lista.append(player.id)
        await db.set_wishlist(ctx.author.id, ctx.guild.id, lista)
        r = RARITIES[player.rarity]
        await ctx.send(f"⭐ ¡**{player.name}** {r.emoji} añadido a tu wishlist!")

    @commands.command(name="wishlist", aliases=["mis_deseos", "quiero_ver"])
    async def view_wishlist(self, ctx, miembro: discord.Member = None):
        """⭐ Ver tu wishlist. Ej: `$wishlist`"""
        target = miembro or ctx.author
        await db.ensure_user(target.id, ctx.guild.id)
        lista = await db.get_wishlist(target.id, ctx.guild.id)

        if not lista:
            await ctx.send(f"{'Tu' if target==ctx.author else f'La'} wishlist está vacía. Usa `$desear <jugador>`.")
            return

        embed = discord.Embed(
            title=f"⭐ Wishlist de {target.display_name}",
            color=0xF1C40F
        )
        lineas = []
        for pid in lista:
            p = get_player(pid)
            if p:
                r = RARITIES[p.rarity]
                tienes = await db.has_card(target.id, ctx.guild.id, pid)
                tick = "✅" if tienes else "❌"
                lineas.append(f"{tick} {r.emoji} **{p.name}** — {p.club}")
        embed.description = "\n".join(lineas)
        embed.set_footer(text="✅ = la tienes | ❌ = aún no")
        await ctx.send(embed=embed)

    @commands.command(name="deseareliminar", aliases=["unwish", "quitardeseo"])
    async def unwish(self, ctx, *, nombre: str):
        """❌ Quita un jugador de tu wishlist. Ej: `$deseareliminar Messi`"""
        from data.players import search_players
        resultados = search_players(nombre)
        if not resultados:
            await ctx.send(f"❌ No encontré a **{nombre}**.", delete_after=8)
            return

        player = resultados[0]
        lista  = await db.get_wishlist(ctx.author.id, ctx.guild.id)
        if player.id not in lista:
            await ctx.send(f"❌ **{player.name}** no está en tu wishlist.", delete_after=6)
            return

        lista.remove(player.id)
        await db.set_wishlist(ctx.author.id, ctx.guild.id, lista)
        await ctx.send(f"🗑️ **{player.name}** eliminado de tu wishlist.")

    # ─── PERFIL ──────────────────────────────────────────────────────────────

    @commands.command(name="perfil", aliases=["profile", "stats", "yo"])
    async def profile(self, ctx, miembro: discord.Member = None):
        """👤 Ver el perfil de un jugador. Ej: `$perfil`"""
        target = miembro or ctx.author
        await db.ensure_user(target.id, ctx.guild.id)
        
        total    = await db.count_user_cards(target.id, ctx.guild.id)
        unicos   = await db.count_unique_cards(target.id, ctx.guild.id)
        wishlist = await db.get_wishlist(target.id, ctx.guild.id)
        cartas   = await db.get_user_cards(target.id, ctx.guild.id)

        # Mejor carta (mayor overall)
        mejor = None
        for row in cartas:
            p = get_player(row["player_id"])
            if p and (mejor is None or p.overall > mejor.overall):
                mejor = p

        embed = discord.Embed(
            title=f"👤 Perfil de {target.display_name}",
            color=0x1ABC9C
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="📦 Cartas totales", value=str(total),  inline=True)
        embed.add_field(name="🃏 Cartas únicas",  value=str(unicos), inline=True)
        embed.add_field(name="⭐ Wishlist",       value=str(len(wishlist)), inline=True)

        if mejor:
            r = RARITIES[mejor.rarity]
            embed.add_field(
                name="🏆 Mejor carta",
                value=f"{r.emoji} **{mejor.name}** (OVR {mejor.overall})",
                inline=False
            )
        
        # % del total completado
        from data.players import total_players
        pct = round(unicos / total_players() * 100, 1)
        embed.add_field(
            name=f"📊 Colección completada",
            value=f"**{pct}%** ({unicos}/{total_players()})",
            inline=False
        )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Collection(bot))
