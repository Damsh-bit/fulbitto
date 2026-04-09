import discord
from discord.ext import commands
import database as db
from data.players import get_player, RARITIES, search_players, total_players


class Admin(commands.Cog, name="🛠️ Admin"):
    """Comandos de administración y ayuda general."""

    def __init__(self, bot):
        self.bot = bot

    # ─── AYUDA ───────────────────────────────────────────────────────────────

    @commands.command(name="ayuda", aliases=["help", "h", "comandos"])
    async def help_cmd(self, ctx):
        """❓ Muestra todos los comandos disponibles."""
        embed = discord.Embed(
            title="⚽ FutCard Bot — Comandos",
            description="Bot de roleo y colección de cartas de fútbol estilo Mudae.",
            color=0x27AE60
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed.add_field(name="⚽ Ruleta", value=(
            "`$roll` / `$r` — Tirar una carta (cooldown 1h)\n"
            "`$carta <nombre>` — Ver detalles de un jugador\n"
            "`$lista [raridad]` — Ver todos los jugadores\n"
            "`$raridades` — Ver probabilidades por raridad"
        ), inline=False)

        embed.add_field(name="📦 Colección", value=(
            "`$coleccion [@usuario]` — Ver tu colección\n"
            "`$perfil [@usuario]` — Ver estadísticas de perfil\n"
            "`$desear <jugador>` — Añadir a wishlist\n"
            "`$wishlist [@usuario]` — Ver wishlist\n"
            "`$deseareliminar <jugador>` — Quitar de wishlist"
        ), inline=False)

        embed.add_field(name="🤝 Social", value=(
            "`$regalar @usuario <jugador>` — Regalar una carta\n"
            "`$intercambio @usuario <tuya> <suya>` — Proponer intercambio\n"
            "`$duelo <jugador1> vs <jugador2>` — Comparar jugadores\n"
            "`$top` — Ranking del servidor\n"
            "`$toppersonajes` — Jugadores más rolados"
        ), inline=False)

        embed.add_field(name="🛠️ Admin", value=(
            "`$darCarta @usuario <jugador>` — Dar carta manualmente *(solo admins)*\n"
            "`$quitarCarta @usuario <jugador>` — Quitar carta *(solo admins)*\n"
            "`$resetCooldown @usuario` — Resetear cooldown *(solo admins)*"
        ), inline=False)

        embed.set_footer(text=f"Total de jugadores: {total_players()} | Prefijos: $ o !")
        await ctx.send(embed=embed)

    # ─── COMANDOS ADMIN ──────────────────────────────────────────────────────

    @commands.command(name="darCarta", aliases=["giveCarta", "spawnCarta"])
    @commands.has_permissions(administrator=True)
    async def admin_give(self, ctx, miembro: discord.Member, *, nombre: str):
        """[Admin] Dar una carta a un usuario."""
        resultados = search_players(nombre)
        if not resultados:
            await ctx.send(f"❌ No encontré a **{nombre}**.", delete_after=8)
            return
        player = resultados[0]
        await db.ensure_user(miembro.id, ctx.guild.id)
        await db.add_card(miembro.id, ctx.guild.id, player.id)
        r = RARITIES[player.rarity]
        await ctx.send(f"✅ Se dio {r.emoji} **{player.name}** a {miembro.display_name}.")

    @commands.command(name="quitarCarta", aliases=["removeCarta"])
    @commands.has_permissions(administrator=True)
    async def admin_remove(self, ctx, miembro: discord.Member, *, nombre: str):
        """[Admin] Quitar una carta de un usuario."""
        resultados = search_players(nombre)
        if not resultados:
            await ctx.send(f"❌ No encontré a **{nombre}**.", delete_after=8)
            return
        player = resultados[0]
        eliminada = await db.remove_one_card(miembro.id, ctx.guild.id, player.id)
        if eliminada:
            await ctx.send(f"✅ Se quitó **{player.name}** de la colección de {miembro.display_name}.")
        else:
            await ctx.send(f"❌ {miembro.display_name} no tiene una carta de **{player.name}**.")

    @commands.command(name="resetCooldown", aliases=["resetCD", "resetRoll"])
    @commands.has_permissions(administrator=True)
    async def admin_reset_cooldown(self, ctx, miembro: discord.Member = None):
        """[Admin] Resetear el cooldown de roll de un usuario."""
        target = miembro or ctx.author
        # Resetear el cooldown de discord.py
        ctx.bot.get_cog("⚽ Cartas").roll_card.reset_cooldown(
            await ctx.bot.get_context(ctx.message)
        )
        # Forma alternativa directa
        bucket = ctx.bot.get_cog("⚽ Cartas").roll_card._buckets.get_bucket(ctx.message)
        if bucket:
            bucket.reset()
        await ctx.send(f"✅ Cooldown de **{target.display_name}** reseteado.")

    @commands.command(name="estadisticas", aliases=["serverStats", "botStats"])
    async def server_stats(self, ctx):
        """📊 Estadísticas globales del bot en este servidor."""
        top_coleccionistas = await db.get_top_collectors(ctx.guild.id, 1)
        top_jugadores      = await db.get_most_rolled_players(ctx.guild.id, 3)

        total_cartas = 0
        if top_coleccionistas:
            coleccionistas = await db.get_top_collectors(ctx.guild.id, 999)
            total_cartas   = sum(r["total"] for r in coleccionistas)

        embed = discord.Embed(
            title=f"📊 Estadísticas de {ctx.guild.name}",
            color=0x8E44AD
        )
        embed.add_field(name="🃏 Cartas totales en el servidor", value=str(total_cartas), inline=True)
        embed.add_field(name="🌍 Jugadores disponibles",          value=str(total_players()), inline=True)

        if top_jugadores:
            jug_txt = "\n".join(
                f"• **{get_player(r['player_id']).name if get_player(r['player_id']) else r['player_id']}** — {r['veces']} veces"
                for r in top_jugadores
            )
            embed.add_field(name="🔥 Top 3 más rolados", value=jug_txt, inline=False)

        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Admin(bot))
