import io
import aiohttp
from PIL import Image, ImageDraw, ImageFont
from data.players import Player, RARITIES

# Colores por raridad (RGB)
RARITY_COLORS = {
    "bronce": (205, 127, 50),       # Bronce
    "plata": (192, 192, 192),        # Plata
    "oro": (255, 215, 0),            # Oro
    "diamante": (0, 191, 255),       # Diamante (cyan)
    "legendario": (255, 0, 255),     # Legendario (magenta)
}

async def generate_fifa_card(player: Player) -> io.BytesIO:
    """Genera una carta estilo FIFA del jugador."""
    
    # Descargar imagen del jugador
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(player.image_url) as resp:
                if resp.status == 200:
                    player_img = Image.open(io.BytesIO(await resp.read())).convert("RGBA")
                else:
                    player_img = None
    except Exception:
        player_img = None

    # Crear imagen base (450x650 píxeles típico de FIFA)
    card_width, card_height = 390, 580
    rarity_color = RARITY_COLORS.get(player.rarity, (100, 100, 100))
    
    # Fondo gradual (superior color raro, inferior más oscuro)
    card = Image.new("RGB", (card_width, card_height), rarity_color)
    draw = ImageDraw.Draw(card, "RGBA")

    # ─── IMAGEN DEL JUGADOR ─────────────────────────────────────────────────
    if player_img:
        # Redimensionar la imagen
        player_img.thumbnail((280, 320), Image.Resampling.LANCZOS)
        # Pegar en el centro superior
        x_offset = (card_width - player_img.width) // 2
        y_offset = 50
        card.paste(player_img, (x_offset, y_offset), player_img)

    # ─── OVERALL (esquina superior izquierda) ───────────────────────────────
    try:
        font_large = ImageFont.truetype("arial.ttf", 60)
        font_medium = ImageFont.truetype("arial.ttf", 16)
        font_small = ImageFont.truetype("arial.ttf", 12)
    except:
        # Fallback si no hay fuentes disponibles
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text((15, 15), str(player.overall), fill="white", font=font_large)
    
    # ─── POSICIÓN (esquina superior derecha) ────────────────────────────────
    draw.text((card_width - 50, 20), player.position, fill="white", font=font_medium)

    # ─── NOMBRE Y CLUB (parte baja) ──────────────────────────────────────────
    name_y = card_height - 145
    draw.text((20, name_y), player.name[:20], fill="white", font=font_medium)
    draw.text((20, name_y + 25), player.club[:20], fill="white", font=font_small)
    draw.text((20, name_y + 40), f"{player.flag} {player.nation}", fill="white", font=font_small)

    # ─── ESTADÍSTICAS (fila inferior) ────────────────────────────────────────
    stats = [
        ("PAC", player.pace),
        ("SHO", player.shooting),
        ("PAS", player.passing),
        ("DRI", player.dribbling),
        ("DEF", player.defending),
        ("PHY", player.physical),
    ]
    
    stat_x = 20
    stat_y = card_height - 50
    stat_spacing = 60

    for label, value in stats:
        draw.text((stat_x, stat_y - 15), label, fill="white", font=font_small)
        draw.text((stat_x + 2, stat_y), str(value), fill="white", font=font_medium)
        stat_x += stat_spacing

    # ─── RARIDEZ (emoji en la esquina inferior derecha) ─────────────────────
    rarity_info = RARITIES.get(player.rarity)
    if rarity_info:
        draw.text((card_width - 60, card_height - 30), rarity_info.emoji, font=font_large)

    # ───────────────────────────────────────────────────────────────────────────
    # Guardar en BytesIO
    img_bytes = io.BytesIO()
    card.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return img_bytes
