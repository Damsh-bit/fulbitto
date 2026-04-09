import io
import aiohttp
from PIL import Image, ImageDraw, ImageFont
from data.players import Player, RARITIES

# Colores por raridad (RGB) - Fondos mejorados
RARITY_COLORS = {
    "bronce": {
        "top": (139, 90, 43),         # Marrón oscuro
        "bottom": (184, 134, 11),     # Amarillo oscuro
        "accent": (210, 180, 140),    # Tan
    },
    "plata": {
        "top": (169, 169, 169),       # Gris oscuro
        "bottom": (211, 211, 211),    # Gris claro
        "accent": (240, 240, 240),    # Casi blanco
    },
    "oro": {
        "top": (218, 165, 32),        # Goldenrod
        "bottom": (255, 215, 0),      # Gold
        "accent": (255, 255, 100),    # Yellow accent
    },
    "diamante": {
        "top": (0, 150, 200),         # Cyan oscuro
        "bottom": (0, 191, 255),      # Cyan claro
        "accent": (173, 216, 230),    # Light blue
    },
    "legendario": {
        "top": (180, 0, 200),         # Morado oscuro
        "bottom": (255, 0, 255),      # Magenta
        "accent": (255, 100, 255),    # Pink/Magenta claro
    },
}

async def generate_fifa_card(player: Player) -> io.BytesIO:
    """Genera una carta estilizada estilo FIFA del jugador."""
    
    # Descargar imagen del jugador
    player_img = None
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(player.image_url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    player_img = Image.open(io.BytesIO(await resp.read())).convert("RGBA")
    except Exception as e:
        print(f"Error descargando imagen: {e}")

    # Dimensiones de la carta
    card_width, card_height = 410, 620
    
    # Crear imagen base
    card = Image.new("RGB", (card_width, card_height), (255, 255, 255))
    draw = ImageDraw.Draw(card, "RGBA")
    
    colors = RARITY_COLORS.get(player.rarity, RARITY_COLORS["bronce"])

    # ─── FONDO DEGRADADO ─────────────────────────────────────────────────────
    # Crear un fondo con gradiente de color
    for y in range(card_height // 2):
        ratio = y / (card_height // 2)
        r = int(colors["top"][0] * (1 - ratio) + colors["bottom"][0] * ratio)
        g = int(colors["top"][1] * (1 - ratio) + colors["bottom"][1] * ratio)
        b = int(colors["top"][2] * (1 - ratio) + colors["bottom"][2] * ratio)
        draw.line([(0, y), (card_width, y)], fill=(r, g, b))
    
    # Rellenar la segunda mitad
    for y in range(card_height // 2, card_height):
        draw.line([(0, y), (card_width, y)], fill=colors["bottom"])

    # ─── BORDE SUPERIOR ──────────────────────────────────────────────────────
    draw.rectangle([(0, 0), (card_width, 8)], fill=colors["accent"])

    # ─── CARGAR FUENTES ─────────────────────────────────────────────────────
    try:
        font_overall = ImageFont.truetype("arial.ttf", 72)
        font_name = ImageFont.truetype("arial.ttf", 20)
        font_stat_label = ImageFont.truetype("arial.ttf", 13)
        font_stat_value = ImageFont.truetype("arial.ttf", 18)
        font_club = ImageFont.truetype("arial.ttf", 14)
    except:
        font_overall = ImageFont.load_default()
        font_name = ImageFont.load_default()
        font_stat_label = ImageFont.load_default()
        font_stat_value = ImageFont.load_default()
        font_club = ImageFont.load_default()

    # ─── IMAGEN DEL JUGADOR ─────────────────────────────────────────────────
    if player_img:
        # Redimensionar y recortar al círculo
        size = 280
        player_img_resized = player_img.resize((size, size), Image.Resampling.LANCZOS)
        
        # Crear máscara circular
        mask = Image.new('L', (size, size), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse([(0, 0), (size, size)], fill=255)
        player_img_resized.putalpha(mask)
        
        # Pegar imagen
        x_offset = (card_width - size) // 2
        y_offset = 30
        card.paste(player_img_resized, (x_offset, y_offset), player_img_resized)

    # ─── OVERALL (esquina superior izquierda) ───────────────────────────────
    draw.text((12, 12), str(player.overall), fill="white", font=font_overall, stroke_width=2, stroke_fill="black")

    # ─── POSICIÓN (esquina superior derecha) ────────────────────────────────
    pos_text = player.position
    draw.text((card_width - 50, 25), pos_text, fill="white", font=font_stat_label, stroke_width=2, stroke_fill="black")

    # ─── NOMBRE Y CLUB (parte media baja) ────────────────────────────────────
    name_y = 330
    
    # Fondo blanco/translúcido para texto
    text_bg_height = 80
    draw.rectangle(
        [(0, name_y - 10), (card_width, name_y + text_bg_height)],
        fill=(*colors["accent"], 220)
    )
    
    draw.text((15, name_y), player.name[:25], fill="black", font=font_name)
    draw.text((15, name_y + 28), player.club[:25], fill="black", font=font_club)
    draw.text((15, name_y + 48), f"{player.flag} {player.nation}", fill="black", font=font_club)

    # ─── ESTADÍSTICAS (fila inferior) ────────────────────────────────────────
    stats = [
        ("PAC", player.pace),
        ("SHO", player.shooting),
        ("PAS", player.passing),
        ("DRI", player.dribbling),
        ("DEF", player.defending),
        ("PHY", player.physical),
    ]
    
    stat_y_top = 430
    stat_x_start = 15
    stat_width = 60
    stat_height = 55

    for i, (label, value) in enumerate(stats):
        x = stat_x_start + (i * stat_width)
        
        # Fondo para cada stat
        draw.rectangle(
            [(x, stat_y_top), (x + stat_width - 5, stat_y_top + stat_height)],
            fill=(*colors["top"], 200),
            outline="white",
            width=2
        )
        
        # Valor
        draw.text((x + 8, stat_y_top + 5), str(value), fill="white", font=font_stat_value)
        # Etiqueta
        draw.text((x + 5, stat_y_top + 30), label, fill="white", font=font_stat_label)

    # ─── RAREZA (esquina inferior derecha) ───────────────────────────────────
    rarity_info = RARITIES.get(player.rarity)
    if rarity_info:
        draw.text((card_width - 50, card_height - 40), rarity_info.emoji, font=font_overall)

    # ─── BORDE INFERIOR ──────────────────────────────────────────────────────
    draw.rectangle([(0, card_height - 8), (card_width, card_height)], fill=colors["accent"])

    # ───────────────────────────────────────────────────────────────────────────
    # Guardar en BytesIO
    img_bytes = io.BytesIO()
    card.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return img_bytes

