import random
from dataclasses import dataclass, field
from typing import Optional

# ─── RARIDADES ───────────────────────────────────────────────────────────────

@dataclass
class Rarity:
    name: str
    emoji: str
    color: int       # hex color para embeds
    chance: float    # probabilidad en porcentaje
    stars: str       # representación visual

RARITIES = {
    "bronce":    Rarity("Bronce",    "🟤", 0xCD7F32, 55.0, "⭐"),
    "plata":     Rarity("Plata",     "⚪", 0xC0C0C0, 25.0, "⭐⭐"),
    "oro":       Rarity("Oro",       "🟡", 0xFFD700, 12.0, "⭐⭐⭐"),
    "diamante":  Rarity("Diamante",  "💎", 0x00BFFF, 6.0,  "⭐⭐⭐⭐"),
    "legendario":Rarity("Legendario","🔮", 0xFF00FF, 2.0,  "⭐⭐⭐⭐⭐"),
}

# ─── JUGADORES ───────────────────────────────────────────────────────────────

@dataclass
class Player:
    id: str
    name: str
    club: str
    nation: str
    position: str
    rarity: str
    overall: int
    flag: str          # emoji bandera
    image_url: str     # imagen del jugador
    # Stats
    pace: int = 70
    shooting: int = 70
    passing: int = 70
    dribbling: int = 70
    defending: int = 70
    physical: int = 70

PLAYERS: dict[str, Player] = {

    # ════════════════════════════════════════
    #  LEGENDARIOS (2%)
    # ════════════════════════════════════════
    "messi": Player(
        id="messi", name="Lionel Messi", club="Inter Miami", nation="Argentina",
        position="DEL", rarity="legendario", overall=94, flag="🇦🇷",
        image_url="https://media.api-sports.io/football/players/154.png",
        pace=81, shooting=92, passing=93, dribbling=96, defending=36, physical=73
    ),
    "ronaldo": Player(
        id="ronaldo", name="Cristiano Ronaldo", club="Al Nassr", nation="Portugal",
        position="DEL", rarity="legendario", overall=92, flag="🇵🇹",
        image_url="https://media.api-sports.io/football/players/874.png",
        pace=83, shooting=94, passing=83, dribbling=89, defending=34, physical=88
    ),
    "neymar": Player(
        id="neymar", name="Neymar Jr.", club="Al Hilal", nation="Brasil",
        position="DEL", rarity="legendario", overall=89, flag="🇧🇷",
        image_url="https://media.api-sports.io/football/players/276.png",
        pace=91, shooting=85, passing=86, dribbling=94, defending=37, physical=63
    ),
    "mbappe": Player(
        id="mbappe", name="Kylian Mbappé", club="Real Madrid", nation="Francia",
        position="DEL", rarity="legendario", overall=93, flag="🇫🇷",
        image_url="https://media.api-sports.io/football/players/278.png",
        pace=97, shooting=90, passing=80, dribbling=92, defending=39, physical=78
    ),
    "haaland": Player(
        id="haaland", name="Erling Haaland", club="Man City", nation="Noruega",
        position="DEL", rarity="legendario", overall=91, flag="🇳🇴",
        image_url="https://media.api-sports.io/football/players/1100.png",
        pace=89, shooting=93, passing=66, dribbling=80, defending=45, physical=88
    ),

    # ════════════════════════════════════════
    #  DIAMANTE (6%)
    # ════════════════════════════════════════
    "vinicius": Player(
        id="vinicius", name="Vinícius Jr.", club="Real Madrid", nation="Brasil",
        position="EXT", rarity="diamante", overall=89, flag="🇧🇷",
        image_url="https://media.api-sports.io/football/players/1028.png",
        pace=95, shooting=80, passing=77, dribbling=91, defending=28, physical=68
    ),
    "bellingham": Player(
        id="bellingham", name="Jude Bellingham", club="Real Madrid", nation="Inglaterra",
        position="MC", rarity="diamante", overall=88, flag="🏴󠁧󠁢󠁥󠁮󠁧󠁿",
        image_url="https://media.api-sports.io/football/players/18617.png",
        pace=75, shooting=82, passing=85, dribbling=87, defending=75, physical=84
    ),
    "salah": Player(
        id="salah", name="Mohamed Salah", club="Liverpool", nation="Egipto",
        position="DEL", rarity="diamante", overall=88, flag="🇪🇬",
        image_url="https://media.api-sports.io/football/players/306.png",
        pace=93, shooting=87, passing=80, dribbling=87, defending=46, physical=74
    ),
    "debruyne": Player(
        id="debruyne", name="Kevin De Bruyne", club="Man City", nation="Bélgica",
        position="MC", rarity="diamante", overall=91, flag="🇧🇪",
        image_url="https://media.api-sports.io/football/players/627.png",
        pace=76, shooting=86, passing=93, dribbling=88, defending=64, physical=78
    ),
    "alisson": Player(
        id="alisson", name="Alisson Becker", club="Liverpool", nation="Brasil",
        position="POR", rarity="diamante", overall=89, flag="🇧🇷",
        image_url="https://media.api-sports.io/football/players/594.png",
        pace=57, shooting=15, passing=78, dribbling=40, defending=14, physical=72
    ),
    "courtois": Player(
        id="courtois", name="Thibaut Courtois", club="Real Madrid", nation="Bélgica",
        position="POR", rarity="diamante", overall=90, flag="🇧🇪",
        image_url="https://media.api-sports.io/football/players/35.png",
        pace=50, shooting=12, passing=70, dribbling=38, defending=12, physical=74
    ),
    "ter_stegen": Player(
        id="ter_stegen", name="Marc-André ter Stegen", club="Barcelona", nation="Alemania",
        position="POR", rarity="diamante", overall=89, flag="🇩🇪",
        image_url="https://media.api-sports.io/football/players/359.png",
        pace=52, shooting=18, passing=82, dribbling=42, defending=14, physical=64
    ),
    "modric": Player(
        id="modric", name="Luka Modrić", club="Real Madrid", nation="Croacia",
        position="MC", rarity="diamante", overall=87, flag="🇭🇷",
        image_url="https://media.api-sports.io/football/players/184.png",
        pace=74, shooting=76, passing=89, dribbling=90, defending=72, physical=64
    ),

    # ════════════════════════════════════════
    #  ORO (12%)
    # ════════════════════════════════════════
    "lewandowski": Player(
        id="lewandowski", name="Robert Lewandowski", club="Barcelona", nation="Polonia",
        position="DEL", rarity="oro", overall=87, flag="🇵🇱",
        image_url="https://media.api-sports.io/football/players/521.png",
        pace=78, shooting=92, passing=79, dribbling=86, defending=43, physical=82
    ),
    "kane": Player(
        id="kane", name="Harry Kane", club="Bayern Munich", nation="Inglaterra",
        position="DEL", rarity="oro", overall=87, flag="🏴󠁧󠁢󠁥󠁮󠁧󠁿",
        image_url="https://media.api-sports.io/football/players/184.png",
        pace=72, shooting=91, passing=84, dribbling=80, defending=47, physical=83
    ),
    "osimhen": Player(
        id="osimhen", name="Victor Osimhen", club="Galatasaray", nation="Nigeria",
        position="DEL", rarity="oro", overall=86, flag="🇳🇬",
        image_url="https://media.api-sports.io/football/players/19560.png",
        pace=94, shooting=87, passing=64, dribbling=80, defending=38, physical=85
    ),
    "saka": Player(
        id="saka", name="Bukayo Saka", club="Arsenal", nation="Inglaterra",
        position="EXT", rarity="oro", overall=85, flag="🏴󠁧󠁢󠁥󠁮󠁧󠁿",
        image_url="https://media.api-sports.io/football/players/19617.png",
        pace=87, shooting=80, passing=82, dribbling=87, defending=63, physical=66
    ),
    "pedri": Player(
        id="pedri", name="Pedri", club="Barcelona", nation="España",
        position="MC", rarity="oro", overall=85, flag="🇪🇸",
        image_url="https://media.api-sports.io/football/players/35845.png",
        pace=76, shooting=74, passing=87, dribbling=88, defending=72, physical=63
    ),
    "rabiot": Player(
        id="rabiot", name="Adrien Rabiot", club="Juventus", nation="Francia",
        position="MC", rarity="oro", overall=82, flag="🇫🇷",
        image_url="https://media.api-sports.io/football/players/369.png",
        pace=77, shooting=74, passing=80, dribbling=80, defending=72, physical=79
    ),
    "ruben_dias": Player(
        id="ruben_dias", name="Rúben Dias", club="Man City", nation="Portugal",
        position="DEF", rarity="oro", overall=87, flag="🇵🇹",
        image_url="https://media.api-sports.io/football/players/1543.png",
        pace=72, shooting=41, passing=71, dribbling=54, defending=90, physical=83
    ),
    "militao": Player(
        id="militao", name="Éder Militão", club="Real Madrid", nation="Brasil",
        position="DEF", rarity="oro", overall=85, flag="🇧🇷",
        image_url="https://media.api-sports.io/football/players/2535.png",
        pace=80, shooting=37, passing=67, dribbling=56, defending=87, physical=80
    ),
    "rodrigo": Player(
        id="rodrigo", name="Rodri", club="Man City", nation="España",
        position="MCD", rarity="oro", overall=89, flag="🇪🇸",
        image_url="https://media.api-sports.io/football/players/19218.png",
        pace=64, shooting=75, passing=87, dribbling=80, defending=88, physical=80
    ),
    "guler": Player(
        id="guler", name="Arda Güler", club="Real Madrid", nation="Turquía",
        position="MC", rarity="oro", overall=82, flag="🇹🇷",
        image_url="https://media.api-sports.io/football/players/338.png",
        pace=77, shooting=80, passing=81, dribbling=85, defending=44, physical=62
    ),
    "olmo": Player(
        id="olmo", name="Dani Olmo", club="Barcelona", nation="España",
        position="MC", rarity="oro", overall=83, flag="🇪🇸",
        image_url="https://media.api-sports.io/football/players/20215.png",
        pace=82, shooting=78, passing=82, dribbling=83, defending=62, physical=72
    ),

    # ════════════════════════════════════════
    #  PLATA (25%)
    # ════════════════════════════════════════
    "griezmann": Player(
        id="griezmann", name="Antoine Griezmann", club="Atlético Madrid", nation="Francia",
        position="DEL", rarity="plata", overall=83, flag="🇫🇷",
        image_url="https://media.api-sports.io/football/players/87.png",
        pace=78, shooting=84, passing=79, dribbling=82, defending=54, physical=72
    ),
    "son": Player(
        id="son", name="Heung-min Son", club="Tottenham", nation="Corea del Sur",
        position="EXT", rarity="plata", overall=85, flag="🇰🇷",
        image_url="https://media.api-sports.io/football/players/629.png",
        pace=88, shooting=87, passing=78, dribbling=86, defending=44, physical=69
    ),
    "chiesa": Player(
        id="chiesa", name="Federico Chiesa", club="Liverpool", nation="Italia",
        position="EXT", rarity="plata", overall=81, flag="🇮🇹",
        image_url="https://media.api-sports.io/football/players/3655.png",
        pace=89, shooting=78, passing=71, dribbling=83, defending=50, physical=74
    ),
    "camavinga": Player(
        id="camavinga", name="Eduardo Camavinga", club="Real Madrid", nation="Francia",
        position="MC", rarity="plata", overall=82, flag="🇫🇷",
        image_url="https://media.api-sports.io/football/players/47365.png",
        pace=80, shooting=67, passing=80, dribbling=82, defending=77, physical=78
    ),
    "valverde": Player(
        id="valverde", name="Federico Valverde", club="Real Madrid", nation="Uruguay",
        position="MC", rarity="plata", overall=84, flag="🇺🇾",
        image_url="https://media.api-sports.io/football/players/3055.png",
        pace=84, shooting=78, passing=80, dribbling=80, defending=75, physical=82
    ),
    "pulisic": Player(
        id="pulisic", name="Christian Pulisic", club="AC Milan", nation="EEUU",
        position="EXT", rarity="plata", overall=81, flag="🇺🇸",
        image_url="https://media.api-sports.io/football/players/889.png",
        pace=87, shooting=76, passing=72, dribbling=83, defending=46, physical=65
    ),
    "carvajal": Player(
        id="carvajal", name="Dani Carvajal", club="Real Madrid", nation="España",
        position="LAT", rarity="plata", overall=83, flag="🇪🇸",
        image_url="https://media.api-sports.io/football/players/240.png",
        pace=79, shooting=57, passing=78, dribbling=78, defending=83, physical=74
    ),
    "theo": Player(
        id="theo", name="Theo Hernández", club="AC Milan", nation="Francia",
        position="LAT", rarity="plata", overall=85, flag="🇫🇷",
        image_url="https://media.api-sports.io/football/players/1303.png",
        pace=91, shooting=70, passing=72, dribbling=80, defending=75, physical=80
    ),
    "maguire": Player(
        id="maguire", name="Harry Maguire", club="Man United", nation="Inglaterra",
        position="DEF", rarity="plata", overall=76, flag="🏴󠁧󠁢󠁥󠁮󠁧󠁿",
        image_url="https://media.api-sports.io/football/players/629.png",
        pace=60, shooting=40, passing=70, dribbling=48, defending=79, physical=85
    ),
    "lukaku": Player(
        id="lukaku", name="Romelu Lukaku", club="Napoli", nation="Bélgica",
        position="DEL", rarity="plata", overall=82, flag="🇧🇪",
        image_url="https://media.api-sports.io/football/players/463.png",
        pace=80, shooting=83, passing=63, dribbling=72, defending=42, physical=90
    ),
    "diaz": Player(
        id="diaz", name="Luis Díaz", club="Liverpool", nation="Colombia",
        position="EXT", rarity="plata", overall=83, flag="🇨🇴",
        image_url="https://media.api-sports.io/football/players/887.png",
        pace=91, shooting=78, passing=73, dribbling=85, defending=44, physical=68
    ),
    "nunez": Player(
        id="nunez", name="Darwin Núñez", club="Liverpool", nation="Uruguay",
        position="DEL", rarity="plata", overall=82, flag="🇺🇾",
        image_url="https://media.api-sports.io/football/players/53.png",
        pace=95, shooting=81, passing=63, dribbling=76, defending=42, physical=83
    ),

    # ════════════════════════════════════════
    #  BRONCE (55%)
    # ════════════════════════════════════════
    "rashford": Player(
        id="rashford", name="Marcus Rashford", club="Man United", nation="Inglaterra",
        position="DEL", rarity="bronce", overall=80, flag="🏴󠁧󠁢󠁥󠁮󠁧󠁿",
        image_url="https://media.api-sports.io/football/players/879.png",
        pace=89, shooting=79, passing=72, dribbling=82, defending=40, physical=72
    ),
    "demiral": Player(
        id="demiral", name="Merih Demiral", club="Al Ahli", nation="Turquía",
        position="DEF", rarity="bronce", overall=78, flag="🇹🇷",
        image_url="https://media.api-sports.io/football/players/338.png",
        pace=74, shooting=35, passing=60, dribbling=46, defending=82, physical=83
    ),
    "brozovic": Player(
        id="brozovic", name="Marcelo Brozović", club="Al Nassr", nation="Croacia",
        position="MCD", rarity="bronce", overall=82, flag="🇭🇷",
        image_url="https://media.api-sports.io/football/players/623.png",
        pace=67, shooting=72, passing=84, dribbling=79, defending=80, physical=74
    ),
    "cuadrado": Player(
        id="cuadrado", name="Juan Cuadrado", club="Inter", nation="Colombia",
        position="LAT", rarity="bronce", overall=78, flag="🇨🇴",
        image_url="https://media.api-sports.io/football/players/232.png",
        pace=88, shooting=73, passing=76, dribbling=83, defending=57, physical=67
    ),
    "firmino": Player(
        id="firmino", name="Roberto Firmino", club="Al Ahli", nation="Brasil",
        position="DEL", rarity="bronce", overall=79, flag="🇧🇷",
        image_url="https://media.api-sports.io/football/players/179.png",
        pace=76, shooting=80, passing=83, dribbling=84, defending=47, physical=72
    ),
    "mahrez": Player(
        id="mahrez", name="Riyad Mahrez", club="Al Ahli", nation="Argelia",
        position="EXT", rarity="bronce", overall=80, flag="🇩🇿",
        image_url="https://media.api-sports.io/football/players/189.png",
        pace=80, shooting=80, passing=79, dribbling=87, defending=38, physical=61
    ),
    "james": Player(
        id="james", name="Reece James", club="Chelsea", nation="Inglaterra",
        position="LAT", rarity="bronce", overall=82, flag="🏴󠁧󠁢󠁥󠁮󠁧󠁿",
        image_url="https://media.api-sports.io/football/players/19181.png",
        pace=78, shooting=68, passing=78, dribbling=79, defending=83, physical=79
    ),
    "depay": Player(
        id="depay", name="Memphis Depay", club="Atlético Madrid", nation="Holanda",
        position="DEL", rarity="bronce", overall=80, flag="🇳🇱",
        image_url="https://media.api-sports.io/football/players/306.png",
        pace=87, shooting=82, passing=77, dribbling=86, defending=37, physical=70
    ),
    "allan": Player(
        id="allan", name="Allan Saint-Maximin", club="Al Ahli", nation="Francia",
        position="EXT", rarity="bronce", overall=78, flag="🇫🇷",
        image_url="https://media.api-sports.io/football/players/1521.png",
        pace=95, shooting=70, passing=65, dribbling=87, defending=28, physical=64
    ),
    "diallo": Player(
        id="diallo", name="Amad Diallo", club="Man United", nation="Costa de Marfil",
        position="EXT", rarity="bronce", overall=75, flag="🇨🇮",
        image_url="https://media.api-sports.io/football/players/35598.png",
        pace=80, shooting=72, passing=67, dribbling=81, defending=38, physical=62
    ),
    "ivan": Player(
        id="ivan", name="Iván Toney", club="Al Ahli", nation="Inglaterra",
        position="DEL", rarity="bronce", overall=79, flag="🏴󠁧󠁢󠁥󠁮󠁧󠁿",
        image_url="https://media.api-sports.io/football/players/629.png",
        pace=72, shooting=83, passing=73, dribbling=74, defending=45, physical=82
    ),
    "gabriel": Player(
        id="gabriel", name="Gabriel Magalhães", club="Arsenal", nation="Brasil",
        position="DEF", rarity="bronce", overall=83, flag="🇧🇷",
        image_url="https://media.api-sports.io/football/players/11467.png",
        pace=73, shooting=43, passing=67, dribbling=50, defending=86, physical=82
    ),
    "savinho": Player(
        id="savinho", name="Savinho", club="Man City", nation="Brasil",
        position="EXT", rarity="bronce", overall=79, flag="🇧🇷",
        image_url="https://media.api-sports.io/football/players/338.png",
        pace=90, shooting=73, passing=71, dribbling=84, defending=38, physical=65
    ),
    "musiala": Player(
        id="musiala", name="Jamal Musiala", club="Bayern Munich", nation="Alemania",
        position="MC", rarity="bronce", overall=84, flag="🇩🇪",
        image_url="https://media.api-sports.io/football/players/338.png",
        pace=80, shooting=77, passing=80, dribbling=89, defending=52, physical=68
    ),
    "wirtz": Player(
        id="wirtz", name="Florian Wirtz", club="Bayer Leverkusen", nation="Alemania",
        position="MC", rarity="bronce", overall=84, flag="🇩🇪",
        image_url="https://media.api-sports.io/football/players/338.png",
        pace=79, shooting=80, passing=82, dribbling=88, defending=49, physical=65
    ),
}

# ─── SISTEMA DE GACHA ─────────────────────────────────────────────────────────

def _weighted_roll_rarity() -> str:
    """Selecciona raridad basada en probabilidades."""
    rand = random.uniform(0, 100)
    cumulative = 0.0
    # Ordenar por rareza (menor probabilidad primero para que "legendario" tenga prioridad al acumularse)
    order = ["legendario", "diamante", "oro", "plata", "bronce"]
    for rarity_key in order:
        r = RARITIES[rarity_key]
        cumulative += r.chance
        if rand <= cumulative:
            return rarity_key
    return "bronce"

def roll_player() -> Player:
    """Obtiene un jugador aleatorio según las probabilidades de raridad."""
    rarity = _weighted_roll_rarity()
    # Filtrar jugadores de esa raridad
    pool = [p for p in PLAYERS.values() if p.rarity == rarity]
    if not pool:
        pool = list(PLAYERS.values())
    return random.choice(pool)

def get_player(player_id: str) -> Optional[Player]:
    return PLAYERS.get(player_id.lower())

def search_players(query: str) -> list[Player]:
    """Busca jugadores por nombre parcial."""
    q = query.lower()
    return [p for p in PLAYERS.values()
            if q in p.name.lower() or q in p.id.lower() or q in p.club.lower()]

def get_rarity(key: str) -> Optional[Rarity]:
    return RARITIES.get(key)

def total_players() -> int:
    return len(PLAYERS)

def players_by_rarity() -> dict:
    result = {k: [] for k in RARITIES}
    for p in PLAYERS.values():
        result[p.rarity].append(p)
    return result
