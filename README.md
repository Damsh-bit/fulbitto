# ? FutCard Bot — Bot de cartas de fútbol para Discord

Bot tipo **Mudae** pero de fútbol. Rueda cartas de tus jugadores favoritos, colecciónalos, intercámbialos con amigos y compite en el ranking del servidor.

---

## ?? Descripción general

FutCard Bot es un bot de Discord que permite:
- rolear cartas de jugadores de fútbol
- reclamar cartas con reacciones
- guardar colecciones y wishlist
- regalar cartas e intercambiar con otros usuarios
- ver rankings y estadísticas del servidor

## ?? Comandos principales

### ? Ruleta
| Comando | Descripción |
|---------|-------------|
| `$roll` / `$r` | Tira una carta aleatoria (cooldown 1 hora) |
| `$carta <nombre>` | Ver detalles de un jugador |
| `$lista [raridad]` | Lista los jugadores disponibles |
| `$raridades` | Muestra probabilidades por raridad |

### ?? Colección
| Comando | Descripción |
|---------|-------------|
| `$coleccion [@usuario]` | Ver tu colección |
| `$perfil [@usuario]` | Ver estadísticas de perfil |
| `$desear <jugador>` | Añadir jugador a wishlist |
| `$wishlist [@usuario]` | Ver wishlist |
| `$deseareliminar <jugador>` | Quitar jugador de wishlist |

### ?? Social
| Comando | Descripción |
|---------|-------------|
| `$regalar @usuario <jugador>` | Regalar carta |
| `$intercambio @usuario <tuya> <suya>` | Proponer intercambio |
| `$duelo <jugador1> vs <jugador2>` | Comparar dos jugadores |
| `$top` | Ranking de coleccionistas |
| `$toppersonajes` | Jugadores más rolados |

### ??? Admin (solo administradores)
| Comando | Descripción |
|---------|-------------|
| `$darCarta @usuario <jugador>` | Dar carta manualmente |
| `$quitarCarta @usuario <jugador>` | Quitar una carta |
| `$resetCooldown [@usuario]` | Resetear cooldown |
| `$estadisticas` | Ver estadísticas del servidor |

---

## ?? Sistema de raridades

| Raridad | Emoji | Probabilidad | Jugadores ejemplo |
|---------|-------|-------------|-------------------|
| ?? Legendario | ????? | 2% | Messi, Ronaldo, Mbappé, Haaland |
| ?? Diamante | ???? | 6% | Vinícius, Bellingham, Salah, De Bruyne |
| ?? Oro | ??? | 12% | Lewandowski, Rodri, Pedri, Kane |
| ? Plata | ?? | 25% | Griezmann, Son, Valverde, Diaz |
| ?? Bronce | ? | 55% | Rashford, Musiala, Wirtz, Gabriel |

---
Hecho con ?? y ?
