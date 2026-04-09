# ? FutCard Bot � Bot de cartas de f�tbol para Discord

Bot tipo **Mudae** pero de f�tbol. Rueda cartas de tus jugadores favoritos, colecci�nalos, interc�mbialos con amigos y compite en el ranking del servidor.

---

## ?? Descripci�n general

FutCard Bot es un bot de Discord que permite:
- rolear cartas de jugadores de f�tbol
- reclamar cartas con reacciones
- guardar colecciones y wishlist
- regalar cartas e intercambiar con otros usuarios
- ver rankings y estad�sticas del servidor

El bot est� modularizado usando `cogs` para separar comandos, colecci�n, social y administraci�n.

---

## ?? Requisitos

- Python 3.10 o superior
- Una cuenta de desarrollador de Discord
- Token de bot de Discord

---

## ?? Configuraci�n del bot en Discord

1. Ve a https://discord.com/developers/applications
2. Haz clic en **New Application** y ponle un nombre
3. Ve a **Bot** ? **Add Bot**
4. En **Privileged Gateway Intents** activa:
   - `MESSAGE CONTENT INTENT`
   - `SERVER MEMBERS INTENT`
5. Copia el **Token** del bot
6. Ve a **OAuth2 ? URL Generator**:
   - Scopes: `bot`
   - Bot Permissions: `Send Messages`, `Read Messages/View Channels`, `Add Reactions`, `Embed Links`, `Read Message History`
7. Abre la URL generada e invita el bot a tu servidor

---

## ??? Configurar el proyecto

```bash
# Clonar / descargar el proyecto
cd futbol-bot

# Instalar dependencias
pip install -r requirements.txt
```

### Crear el archivo de configuraci�n local

En Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

En Linux/macOS o WSL:

```bash
cp .env.example .env
```

Luego edita `.env` y reemplaza:

```env
DISCORD_TOKEN=tu_token_aqui
```

---

## ?? Ejecutar el bot

```bash
python bot.py
```

---

## ?? Estructura del proyecto

```
futbol-bot/
+-- bot.py              # Entrada principal
+-- database.py         # Operaciones con SQLite
+-- requirements.txt
+-- .env                # Tu token (NO subir a git)
+-- .env.example
+-- data/
�   +-- __init__.py
�   +-- players.py      # Base de datos de jugadores y sistema gacha
+-- cogs/
    +-- __init__.py
    +-- cards.py        # Comandos de roll y cartas
    +-- collection.py   # Colecci�n, wishlist, perfil
    +-- social.py       # Regalar, intercambio, ranking, duelo
    +-- admin.py        # Comandos admin y ayuda
```

---

## ?? Comandos principales

### ? Ruleta
| Comando | Descripci�n |
|---------|-------------|
| `$roll` / `$r` | Tira una carta aleatoria (20 por hora) |
| `$carta <nombre>` | Ver detalles de un jugador |
| `$lista [raridad]` | Lista los jugadores disponibles |
| `$raridades` | Muestra probabilidades por raridad |

### ?? Colecci�n
| Comando | Descripci�n |
|---------|-------------|
| `$coleccion [@usuario]` | Ver tu colecci�n |
| `$perfil [@usuario]` | Ver estad�sticas de perfil |
| `$desear <jugador>` | A�adir jugador a wishlist |
| `$wishlist [@usuario]` | Ver wishlist |
| `$deseareliminar <jugador>` | Quitar jugador de wishlist |

### ?? Social
| Comando | Descripci�n |
|---------|-------------|
| `$regalar @usuario <jugador>` | Regalar carta |
| `$intercambio @usuario <tuya> <suya>` | Proponer intercambio |
| `$duelo <jugador1> vs <jugador2>` | Comparar dos jugadores |
| `$top` | Ranking de coleccionistas |
| `$toppersonajes` | Jugadores m�s rolados |

### ??? Admin (solo administradores)
| Comando | Descripci�n |
|---------|-------------|
| `$darCarta @usuario <jugador>` | Dar carta manualmente |
| `$quitarCarta @usuario <jugador>` | Quitar una carta |
| `$resetCooldown [@usuario]` | Resetear cooldown |
| `$estadisticas` | Ver estad�sticas del servidor |

---

## ?? Sistema de raridades

| Raridad | Emoji | Probabilidad | Jugadores ejemplo |
|---------|-------|-------------|-------------------|
| ?? Legendario | ????? | 2% | Messi, Ronaldo, Mbapp�, Haaland |
| ?? Diamante | ???? | 6% | Vin�cius, Bellingham, Salah, De Bruyne |
| ?? Oro | ??? | 12% | Lewandowski, Rodri, Pedri, Kane |
| ? Plata | ?? | 25% | Griezmann, Son, Valverde, Diaz |
| ?? Bronce | ? | 55% | Rashford, Musiala, Wirtz, Gabriel |

---

## ? Agregar m�s jugadores

Edita `data/players.py` y a�ade una entrada en el diccionario `PLAYERS`:

```python
"tu_jugador": Player(
    id="tu_jugador",
    name="Nombre Completo",
    club="Nombre del Club",
    nation="Pa�s",
    position="DEL",       # DEL, EXT, MC, MCD, LAT, DEF, POR
    rarity="oro",         # bronce, plata, oro, diamante, legendario
    overall=85,
    flag="????",
    image_url="https://url-de-imagen.com/jugador.png",
    pace=80, shooting=85, passing=75, dribbling=82, defending=40, physical=75
),
```

---

## ?? Seguridad

- El archivo `.env` NO debe subirse a GitHub.
- `.env.example` es seguro y contiene solo el formato necesario.
- `.gitignore` ya excluye:
  - `.env`
  - `futbol_cards.db`
  - `__pycache__/`
  - `*.pyc`

---

## ?? Comprobaciones realizadas

- El bot usa `DISCORD_TOKEN` desde `.env`.
- La carpeta `cogs/` contiene los m�dulos del bot.
- La carpeta `data/` contiene los jugadores y el sistema gacha.

---

Hecho con ?? y ?
