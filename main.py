"""
Pixel Quest: The Jumping Hero
Módulo 1 - Semana 6 (Versión Final Completa)

VERSIÓN FINAL CON:
1. Sistema completo de sonidos
2. Nivel más largo y desafiante
3. Más monedas y enemigos
4. Código optimizado y comentado
5. Listo para exportar
"""

import os
import sys
import asyncio
import pygame

# -----------------------------
# CONFIGURACIÓN DEL JUEGO
# -----------------------------

WIDTH, HEIGHT = 960, 540
FPS = 60
TILE = 48

# Colores
SKY = (120, 190, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 100, 100)
YELLOW = (255, 255, 0)
GREEN = (100, 255, 100)
GOLD = (255, 215, 0)

# Constantes de física
GRAVITY = 0.8
JUMP_POWER = -15
HERO_SPEED = 5

# Constantes de puntos
POINTS_COIN = 10
POINTS_ENEMY = 50

# Rutas (compatible with PyInstaller bundling)
if getattr(sys, 'frozen', False):
    _BASE = sys._MEIPASS  # PyInstaller extracts here
else:
    _BASE = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(_BASE, "assets")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")


# -----------------------------
# FUNCIONES DE CARGA
# -----------------------------

def load_image(name: str) -> pygame.Surface:
    """Carga un sprite PNG desde /assets."""
    path = os.path.join(ASSETS_DIR, name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo: {path}")
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, (TILE, TILE))


def load_sound(name: str) -> pygame.mixer.Sound:
    """
    Carga un efecto de sonido desde /assets/sounds/.
    Si el archivo no existe, devuelve None y el juego continúa sin el sonido.
    """
    path = os.path.join(SOUNDS_DIR, name)
    try:
        sound = pygame.mixer.Sound(path)
        return sound
    except:
        print(f"⚠️ No se pudo cargar el sonido: {name}")
        return None


# ---------------------------------------------------------------------------
# MAPA DESAFIANTE (150 cols × 12 rows, TILE=48)
# Auto-validates: after placement, any column with G in two adjacent rows
#   has the HIGHER row cleared → no invisible walls ever.
# ---------------------------------------------------------------------------

def _build_map():
    rows = [['.']*150 for _ in range(12)]

    def G(row, c1, c2):
        for c in range(c1, min(c2+1, 150)):
            rows[row][c] = 'G'

    # Rows 10-11: always solid
    G(10, 0, 149); G(11, 0, 149)

    # ── ROW 9: main floor with gaps ─────────────────────────────────────────
    G(9,  0, 36)    # Z1-Z2 (flat start → first gap at 37)
    G(9, 41, 62)    # Z2-Z3 (gap 37-40)
    G(9, 67, 88)    # Z3-Z4 (gap 63-66)
    G(9, 94,110)    # Z4-Z5 (gap 89-93)
    G(9,115,120)    # Z5 bridge (gap 111-114)
    G(9,126,149)    # Z6 final  (gap 121-125)

    # ── ROW 9 surface trenches (1-2 tile holes, row 10 visible below) ──────
    # These create visual variety: small dips in the ground.
    # Hero walks off the edge, drops 1 tile, walks on row 10, steps back up.
    def hole(c1, c2):
        for c in range(c1, min(c2+1, 150)):
            rows[9][c] = '.'

    hole(14, 15)    # Z1 first trench (teaches falling 1 tile)
    hole(22, 23)    # Z1 near tutorial C
    hole(44, 45)    # Z2 trench
    hole(53, 54)    # Z2 trench
    hole(71, 72)    # Z3 trench
    hole(81, 82)    # Z3-Z4 trench
    hole(97, 98)    # Z4 trench
    hole(104,105)   # Z4 trench
    hole(129,130)   # Z6 trench
    hole(143,144)   # Z6 trench

    # ── ROW 8: tutorial steps + gap bridges + OBSTACLE BLOCKS ──────────────
    G(8,  7,  9)    # Z1 tutorial A
    G(8, 16, 18)    # Z1 tutorial B
    G(8, 25, 27)    # Z1 tutorial C
    # Obstacle blocks: give enemies things to bounce off + parkour points
    G(8, 33, 34)    # Z1 obstacle pillar
    G(8, 37, 40)    # bridge gap 37-40
    G(8, 50, 52)    # Z2 platform
    G(8, 63, 66)    # bridge gap 63-66
    G(8, 73, 75)    # Z3 step-1
    G(8, 77, 78)    # Z3 obstacle pillar
    G(8, 84, 85)    # Z4 obstacle pillar
    G(8, 91, 93)    # bridge gap 89-93
    G(8,100,102)    # Z4 platform
    G(8,104,105)    # Z4 obstacle pillar (moved from 106-107: was too close to row7 107-109)
    G(8,111,114)    # bridge gap 111-114
    G(8,118,119)    # Z5 stepping stone (needed to reach row7 107-109 area)
    G(8,121,125)    # bridge gap 121-125
    G(8,128,129)    # Z6 obstacle pillar (moved from 131-132: was clearing row7 130-132)
    G(8,135,137)    # Z6 platform
    G(8,147,148)    # Z6 obstacle pillar (moved from 140-141: was clearing row7 140-142)
    G(8,144,146)    # Z6 platform

    # ── ROW 7: mid-height platforms ─────────────────────────────────────────
    G(7, 12, 14)    # Z1 high bonus
    G(7, 32, 34)    # Z2 high
    G(7, 45, 47)    # Z2 high
    G(7, 57, 59)    # Z3 step-2
    G(7, 79, 81)    # Z3 high
    G(7, 86, 88)    # Z4 high
    G(7, 96, 98)    # Z4-Z5
    G(7,107,109)    # Z5 high
    G(7,130,132)    # Z6 step
    G(7,140,142)    # Z6 step

    # ── ROW 6: tall platforms ───────────────────────────────────────────────
    G(6, 50, 52)    # Z2 very high
    G(6, 62, 64)    # Z3 step-3
    G(6, 83, 85)    # Z4 tall
    G(6, 91, 93)    # Z4 tall
    G(6,111,113)    # Z5 tall
    G(6,128,130)    # Z6 tall
    G(6,136,138)    # Z6 tall
    G(6,147,149)    # Z6 peak-base

    # ── ROW 5: very high ────────────────────────────────────────────────────
    G(5, 67, 69)    # Z3 step-4
    G(5, 87, 89)    # Z4 peak
    G(5,115,117)    # Z5 peak
    G(5,133,135)    # Z6 peak approach

    # ── ROW 4: peaks ────────────────────────────────────────────────────────
    G(4, 71, 73)    # Z3 peak
    G(4,139,141)    # Z6 peak

    # ── ROW 3: absolute peak ────────────────────────────────────────────────
    G(3, 75, 77)    # Z3 absolute peak

    # ── AUTO-FIX: clear SIDE-WALL violations between adjacent rows ─────────
    # A tile at (r,c) creates a wall if the row below has G within 1-2 cols
    # to the LEFT or RIGHT (not directly below — that's a valid stack).
    # EXCEPTION: row-8 tiles above row-9 gaps are BRIDGES — keep them.
    MIN_GAP = 2
    for r in range(2, 9):
        to_clear = []
        for c in range(150):
            if rows[r][c] != 'G':
                continue
            # Protect bridges: row-8 tile above a row-9 gap → keep it
            if r == 8 and rows[9][c] == '.':
                continue
            # Check for G in row r+1 at nearby-but-not-same columns
            for dc in range(-MIN_GAP, MIN_GAP + 1):
                if dc == 0:
                    continue
                nc = c + dc
                if 0 <= nc < 150 and rows[r+1][nc] == 'G':
                    to_clear.append(c)
                    break
        for c in to_clear:
            rows[r][c] = '.'

    return [''.join(r) for r in rows]


WORLD_MAP  = _build_map()
WORLD_WIDTH = len(WORLD_MAP[0]) * TILE


def _top_of_ground(col: int) -> int:
    """Devuelve el y-pixel de la parte SUPERIOR del tile sólido más alto en 'col'.
    Coloca una moneda en:  y = _top_of_ground(col) - TILE  (justo encima del suelo).
    Si no hay suelo devuelve HEIGHT (fuera de pantalla — no debería ocurrir).
    """
    for row in range(len(WORLD_MAP)):
        r = WORLD_MAP[row]
        if 0 <= col < len(r) and r[col] == 'G':
            return row * TILE
    return HEIGHT


# -----------------------------
# FUNCIONES DEL MUNDO
# -----------------------------

def get_tile_at(world_x: int, world_y: int) -> str:
    """Devuelve el tipo de bloque en una posición del mundo."""
    col = int(world_x) // TILE
    row = int(world_y) // TILE
    
    if row < 0 or row >= len(WORLD_MAP):
        return '.'
        
    current_row_len = len(WORLD_MAP[row])
    
    if col < 0 or col >= current_row_len:
        return 'G'
    
    return WORLD_MAP[row][col]


def check_collision_with_tiles(x: int, y: int, width: int, height: int) -> dict:
    """Verifica colisiones con bloques del mundo."""
    collision = {'top': False, 'bottom': False, 'left': False, 'right': False}
    
    if get_tile_at(x, y) == 'G' or get_tile_at(x, y + height - 1) == 'G':
        collision['left'] = True
    
    if get_tile_at(x + width - 1, y) == 'G' or get_tile_at(x + width - 1, y + height - 1) == 'G':
        collision['right'] = True
    
    if get_tile_at(x, y) == 'G' or get_tile_at(x + width - 1, y) == 'G':
        collision['top'] = True
    
    if get_tile_at(x, y + height) == 'G' or get_tile_at(x + width - 1, y + height) == 'G':
        collision['bottom'] = True
    
    return collision


def draw_world(screen: pygame.Surface, ground_sprite: pygame.Surface, camera_x: int) -> None:
    """Dibuja el mundo con offset de cámara."""
    for row_i, row in enumerate(WORLD_MAP):
        for col_i, cell in enumerate(row):
            if cell == "G":
                world_x = col_i * TILE
                world_y = row_i * TILE
                screen_x = world_x - camera_x
                screen_y = world_y
                
                if -TILE < screen_x < WIDTH:
                    screen.blit(ground_sprite, (screen_x, screen_y))


def check_rect_collision(x1: int, y1: int, w1: int, h1: int, 
                         x2: int, y2: int, w2: int, h2: int) -> bool:
    """Verifica si dos rectángulos se están superponiendo."""
    return (x1 < x2 + w2 and
            x1 + w1 > x2 and
            y1 < y2 + h2 and
            y1 + h1 > y2)


# -----------------------------
# FUNCIÓN PRINCIPAL
# -----------------------------

async def main() -> None:
    pygame.init()
    pygame.mixer.init()  # Inicializar el sistema de audio
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pixel Quest: The Jumping Hero - VERSIÓN FINAL")
    clock = pygame.time.Clock()

    # Cargar sprites del juego
    hero_sprite   = load_image("hero.png")
    ground_sprite = load_image("ground.png")
    coin_sprite   = load_image("coin.png")
    enemy_sprite  = load_image("enemy.png")

    # Iconos del HUD  (24 × 24 px)
    HUD_SIZE = 24
    hud_heart  = pygame.transform.scale(load_image("heart.png"),  (HUD_SIZE, HUD_SIZE))
    hud_coin   = pygame.transform.scale(coin_sprite,               (HUD_SIZE, HUD_SIZE))
    hud_enemy  = pygame.transform.scale(enemy_sprite,              (HUD_SIZE, HUD_SIZE))

    # Fuentes
    font = pygame.font.SysFont("Arial", 18)
    font_large = pygame.font.SysFont("Arial", 48, bold=True)
    font_score = pygame.font.SysFont("Arial", 32, bold=True)

    # =====================================
    # TODO 1: CARGAR SONIDOS
    # =====================================
    # INSTRUCCIONES:
    # Carga los archivos de sonido usando la función load_sound()
    # 
    # ARCHIVOS NECESARIOS (debes buscarlos en internet y ponerlos en assets/sounds/):
    # - jump.wav: Sonido al saltar
    # - coin.wav: Sonido al recolectar moneda
    # - enemy_defeat.wav: Sonido al derrotar enemigo
    # - hurt.wav: Sonido al recibir daño
    # - victory.wav: Sonido al ganar
    # - gameover.wav: Sonido al perder
    # - background.ogg: Música de fondo (opcional)
    #
    # SITIOS RECOMENDADOS PARA BUSCAR SONIDOS:
    # - freesound.org
    # - opengameart.org
    # - jfxr.frozenfractal.com (generador de sonidos retro)
    #
    # TAREA:
    # Carga cada sonido usando: load_sound("nombre_archivo.wav")
    #
    # PISTA: jump_sound = load_sound("jump.wav")
    #
    # ESCRIBE TU CÓDIGO AQUÍ:
    jump_sound = load_sound("jump.mp3")  # Reemplaza con: load_sound("jump.wav")
    coin_sound = load_sound("coin.mp3")  # Reemplaza con: load_sound("coin.wav")
    enemy_defeat_sound = load_sound("enemy_defeat.mp3")  # Reemplaza con: load_sound("enemy_defeat.wav")
    hurt_sound = load_sound("hurt.mp3")  # Reemplaza con: load_sound("hurt.wav")
    victory_sound = load_sound("victory.mp3")  # Reemplaza con: load_sound("victory.wav")
    gameover_sound = load_sound("game_over.mp3")  # archivo correcto en assets/sounds/
    
    # =====================================
    # TODO 2: CARGAR Y REPRODUCIR MÚSICA DE FONDO
    # =====================================
    # INSTRUCCIONES:
    # La música de fondo se carga y reproduce de forma diferente a los efectos de sonido.
    # Usa pygame.mixer.music para música continua.
    #
    # TAREA:
    # 1. Intenta cargar la música de fondo
    # 2. Si existe, reprodúcela en bucle
    # 3. Si no existe, el juego continúa sin música
    #
    # PISTA: 
    # try:
    #     pygame.mixer.music.load(os.path.join(SOUNDS_DIR, "background.ogg"))
    #     pygame.mixer.music.set_volume(0.3)  # Volumen al 30%
    #     pygame.mixer.music.play(-1)  # -1 = bucle infinito
    # except:
    #     print("No se encontró música de fondo")
    #
    # ESCRIBE TU CÓDIGO AQUÍ:

    try:
        pygame.mixer.music.load(os.path.join(SOUNDS_DIR, "background.ogg"))
        pygame.mixer.music.set_volume(0.4) 
        pygame.mixer.music.play(-1)
    except:
        print("Archivo no encontrado: No se encontró música de fondo!")

    # Variables del juego
    lives = 3
    score = 0
    game_over = False
    victory = False
    victory_sound_played = False
    gameover_sound_played = False
    
    # Checkpoint: respawn where last enemy was killed
    last_kill_x = None
    last_kill_y = None
    
    # Posición inicial del héroe
    SPAWN_X = 5 * TILE
    SPAWN_Y = 9 * TILE - TILE
    
    hero_x = SPAWN_X
    hero_y = SPAWN_Y
    
    hero_width = hero_sprite.get_width()
    hero_height = hero_sprite.get_height()

    # Variables de física
    velocity_y = 0
    on_ground = False
    
    # Sistema de invulnerabilidad
    invulnerable = False
    invulnerable_timer = 0
    INVULNERABLE_DURATION = 90  # 1.5 seconds — fair window
    
    # =========================================================
    # ENEMIGOS — TODOS con gravedad
    # Nacen en y = -TILE (sobre la pantalla) y caen al suelo real
    # gracias a la física, eliminando cualquier problema de posición.
    # Solo se necesita definir x, direction y speed.
    # vy=0 se inicializa para cada uno.
    # =========================================================
    SPAWN_Y_ENEMY = -TILE  # debajo del borde superior, cae por gravedad

    # Enemies on wide ground segments, slower speeds, better distribution
    INITIAL_ENEMIES = [
        # Z1 (cols 0-36) — 2 slow enemies
        {"x": 12*TILE, "y": SPAWN_Y_ENEMY, "vy": 0, "direction":  1, "speed": 2},
        {"x": 28*TILE, "y": SPAWN_Y_ENEMY, "vy": 0, "direction": -1, "speed": 2},
        # Z2 (cols 41-62) — 2 medium enemies
        {"x": 48*TILE, "y": SPAWN_Y_ENEMY, "vy": 0, "direction":  1, "speed": 3},
        {"x": 58*TILE, "y": SPAWN_Y_ENEMY, "vy": 0, "direction": -1, "speed": 3},
        # Z3 (cols 67-88) — 2 enemies
        {"x": 73*TILE, "y": SPAWN_Y_ENEMY, "vy": 0, "direction":  1, "speed": 3},
        {"x": 85*TILE, "y": SPAWN_Y_ENEMY, "vy": 0, "direction": -1, "speed": 3},
        # Z4 (cols 94-110) — 2 enemies
        {"x":100*TILE, "y": SPAWN_Y_ENEMY, "vy": 0, "direction":  1, "speed": 4},
        {"x":108*TILE, "y": SPAWN_Y_ENEMY, "vy": 0, "direction": -1, "speed": 4},
        # Z6 (cols 126-149) — 2 enemies
        {"x":133*TILE, "y": SPAWN_Y_ENEMY, "vy": 0, "direction": -1, "speed": 4},
        {"x":145*TILE, "y": SPAWN_Y_ENEMY, "vy": 0, "direction":  1, "speed": 4},
    ]

    enemies = [e.copy() for e in INITIAL_ENEMIES]

    enemy_width  = enemy_sprite.get_width()
    enemy_height = enemy_sprite.get_height()

    NUM_ENEMIES = len(INITIAL_ENEMIES)

    # =========================================================
    # MONEDAS — y computed from map geometry via _top_of_ground()
    # =========================================================
    def _c(col, extra_up=0):
        """Coin at column `col`, TILE*(1+extra_up) above the ground."""
        gy = _top_of_ground(col)
        return {"x": col * TILE, "y": gy - TILE - extra_up * TILE}

    INITIAL_COINS = [
        # Z1: ground coins + tutorial platform coins
        _c( 3),  _c( 8),  _c(13),  _c(20),   # on row9 floor
        _c( 8, 1),  _c(17, 1),                # above tutorial steps (row8)
        # Z2: guide across gap
        _c(27),  _c(33),  _c(42),  _c(51),    # on row9 floor
        _c(46),                                # on row8 platform
        # Z3: staircase coins guide upward
        _c(58),  _c(68),  _c(74),  _c(80),    # on ground/platforms
        _c(58, 1),  _c(68, 1),                 # higher steps
        # Z4: gauntlet (between enemies)
        _c(96),  _c(100),  _c(105),  _c(108), # ground + platforms
        _c(87, 1),                              # high bonus
        # Z5: bridge rewards
        _c(115), _c(118), _c(120),             # bridge coins
        _c(107, 1),                             # high Z5
        # Z6: tower climb + finale
        _c(128), _c(132), _c(136), _c(140),   # ground
        _c(144), _c(148),                       # ground
        _c(131, 1), _c(141, 1),                # platform bonus
    ]

    coins = [c.copy() for c in INITIAL_COINS]

    coin_width  = coin_sprite.get_width()
    coin_height = coin_sprite.get_height()

    NUM_COINS = len(INITIAL_COINS)
    
    # Sistema de cámara
    camera_x = 0
    CAMERA_DEAD_ZONE_LEFT = WIDTH // 3
    CAMERA_DEAD_ZONE_RIGHT = WIDTH * 2 // 3

    running = True
    while running:
        await asyncio.sleep(0)  # Pygbag: let browser render each frame
        dt = clock.tick(FPS)

        # Pantalla de victoria
        if victory:
            # Reproducir sonido de victoria solo una vez
            if not victory_sound_played:
                if victory_sound:
                    victory_sound.play()
                victory_sound_played = True
                pygame.mixer.music.stop()  # Detener música de fondo
            
            screen.fill(SKY)
            
            victory_text = font_large.render("¡VICTORIA!", True, GOLD)
            score_text = font_score.render(f"Puntaje Final: {score}", True, WHITE)
            stats_text = font.render(
                f"Monedas: {NUM_COINS - len(coins)}/{NUM_COINS} | Enemigos: {NUM_ENEMIES - len(enemies)}/{NUM_ENEMIES}",
                True, WHITE
            )
            restart_text = font.render("Presiona R para jugar de nuevo o ESC para salir", True, WHITE)
            
            victory_rect = victory_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 70))
            score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10))
            stats_rect = stats_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
            restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 90))
            
            screen.blit(victory_text, victory_rect)
            screen.blit(score_text, score_rect)
            screen.blit(stats_text, stats_rect)
            screen.blit(restart_text, restart_rect)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Reiniciar todo
                        victory = False
                        game_over = False
                        victory_sound_played = False
                        gameover_sound_played = False
                        lives = 3
                        score = 0
                        hero_x = SPAWN_X
                        hero_y = SPAWN_Y
                        velocity_y = 0
                        invulnerable = False
                        invulnerable_timer = 0
                        enemies = [e.copy() for e in INITIAL_ENEMIES]
                        coins   = [c.copy() for c in INITIAL_COINS]
                        # Reiniciar música
                        try:
                            pygame.mixer.music.play(-1)
                        except:
                            pass
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            pygame.display.flip()
            continue

        # Pantalla de Game Over
        if game_over:
            # Reproducir sonido de game over solo una vez
            if not gameover_sound_played:
                if gameover_sound:
                    gameover_sound.play()
                gameover_sound_played = True
                pygame.mixer.music.stop()  # Detener música de fondo
            
            screen.fill(BLACK)
            game_over_text = font_large.render("GAME OVER", True, RED)
            score_text = font_score.render(f"Puntaje: {score}", True, WHITE)
            stats_text = font.render(
                f"Monedas: {NUM_COINS - len(coins)}/{NUM_COINS} | Enemigos: {NUM_ENEMIES - len(enemies)}/{NUM_ENEMIES}",
                True, WHITE
            )
            restart_text = font.render("Presiona R para reintentar o ESC para salir", True, WHITE)
            
            text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 70))
            score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10))
            stats_rect = stats_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
            restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 90))
            
            screen.blit(game_over_text, text_rect)
            screen.blit(score_text, score_rect)
            screen.blit(stats_text, stats_rect)
            screen.blit(restart_text, restart_rect)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game_over = False
                        victory = False
                        victory_sound_played = False
                        gameover_sound_played = False
                        lives = 3
                        score = 0
                        hero_x = SPAWN_X
                        hero_y = SPAWN_Y
                        velocity_y = 0
                        invulnerable = False
                        invulnerable_timer = 0
                        enemies = [e.copy() for e in INITIAL_ENEMIES]
                        coins   = [c.copy() for c in INITIAL_COINS]
                        # Reiniciar música
                        try:
                            pygame.mixer.music.play(-1)
                        except:
                            pass
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            pygame.display.flip()
            continue

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Lectura de teclado
        keys = pygame.key.get_pressed()

        # Movimiento horizontal con step-up
        new_hero_x = hero_x
        
        if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            new_hero_x = hero_x - HERO_SPEED
        elif keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            new_hero_x = hero_x + HERO_SPEED
        
        collision = check_collision_with_tiles(new_hero_x, hero_y, hero_width, hero_height)
        
        blocked = False
        if new_hero_x < hero_x and collision['left']:
            blocked = True
        elif new_hero_x > hero_x and collision['right']:
            blocked = True
        
        if blocked and on_ground:
            # Step-up: try moving up by 1 tile and see if that clears the wall
            step_y = hero_y - TILE
            step_col = check_collision_with_tiles(new_hero_x, step_y, hero_width, hero_height)
            if not step_col['left'] and not step_col['right'] and not step_col['top']:
                hero_x = new_hero_x
                hero_y = step_y
                velocity_y = 0
                blocked = False
        
        if not blocked:
            hero_x = new_hero_x
        
        if hero_x < 0:
            hero_x = 0
        if hero_x > WORLD_WIDTH - hero_width:
            hero_x = WORLD_WIDTH - hero_width

        # Salto
        if keys[pygame.K_SPACE] and on_ground:
            velocity_y = JUMP_POWER
            on_ground = False
            
            # =====================================
            # TODO 3: REPRODUCIR SONIDO DE SALTO
            # =====================================
            # INSTRUCCIONES:
            # Cuando el héroe salta, debe reproducirse un sonido.
            #
            # TAREA:
            # Verifica que jump_sound no sea None, luego reprodúcelo.
            #
            # PISTA:
            # if jump_sound:
            #     jump_sound.play()
            #
            # ESCRIBE TU CÓDIGO AQUÍ:

            if jump_sound:
                jump_sound.play()
            else:
                print("ERROR: No hay un sonido de salto")
            
            
            

        # Gravedad
        if not on_ground:
            velocity_y += GRAVITY

        # Movimiento vertical con colisiones
        new_hero_y = hero_y + velocity_y
        collision = check_collision_with_tiles(hero_x, new_hero_y, hero_width, hero_height)
        
        if velocity_y > 0 and collision['bottom']:
            tile_row = (new_hero_y + hero_height) // TILE
            hero_y = tile_row * TILE - hero_height
            velocity_y = 0
            on_ground = True
        elif velocity_y < 0 and collision['top']:
            tile_row = new_hero_y // TILE
            hero_y = (tile_row + 1) * TILE
            velocity_y = 0
        else:
            hero_y = new_hero_y
            if not collision['bottom']:
                on_ground = False

        # Recolectar monedas
        for coin in coins[:]:
            tocando_moneda = check_rect_collision(
                hero_x, hero_y, hero_width, hero_height,
                coin["x"], coin["y"], coin_width, coin_height
            )
            
            if tocando_moneda:
                coins.remove(coin)
                score += POINTS_COIN
                
                # =====================================
                # TODO 4: REPRODUCIR SONIDO DE MONEDA
                # =====================================
                # INSTRUCCIONES:
                # Cuando recolectas una moneda, reproduce el sonido correspondiente.
                #
                # TAREA:
                # Reproduce coin_sound si existe.
                #
                # PISTA: Similar al TODO 3
                #
                # ESCRIBE TU CÓDIGO AQUÍ:
                if coin_sound:
                    coin_sound.play()
                else:
                    print("ERROR: No hay un sonido de moneda")
                
                

        # Actualizar enemigos (horizontal + gravedad)
        for enemy in enemies:
            # 1. Movimiento horizontal
            enemy["x"] += enemy["direction"] * enemy["speed"]

            # Revertir si choca lateralmente con un tile
            col_h = check_collision_with_tiles(
                enemy["x"], enemy["y"], enemy_width, enemy_height
            )
            if col_h['left'] or col_h['right']:
                enemy["direction"] *= -1
                enemy["x"] += enemy["direction"] * enemy["speed"] * 2

            # 2. Gravedad
            enemy["vy"] += GRAVITY

            # 3. Movimiento vertical con detección de suelo
            new_ey = enemy["y"] + enemy["vy"]
            col_v = check_collision_with_tiles(
                enemy["x"], new_ey, enemy_width, enemy_height
            )
            if enemy["vy"] > 0 and col_v['bottom']:
                # Aterrizar encima del tile
                tile_row = int(new_ey + enemy_height) // TILE
                enemy["y"] = tile_row * TILE - enemy_height
                enemy["vy"] = 0
            elif enemy["vy"] < 0 and col_v['top']:
                tile_row = int(new_ey) // TILE
                enemy["y"] = (tile_row + 1) * TILE
                enemy["vy"] = 0
            else:
                enemy["y"] = new_ey

        # Colisiones con enemigos
        for enemy in enemies[:]:
            hay_colision = check_rect_collision(
                hero_x, hero_y, hero_width, hero_height,
                enemy["x"], enemy["y"], enemy_width, enemy_height
            )
            
            if hay_colision:
                # Stomp: hero is falling AND feet are above enemy's bottom half
                hero_feet = hero_y + hero_height
                enemy_bottom = enemy["y"] + enemy_height
                esta_arriba = hero_feet < enemy_bottom
                esta_cayendo = velocity_y > 0
                
                if esta_arriba and esta_cayendo:
                    enemies.remove(enemy)
                    score += POINTS_ENEMY
                    velocity_y = -10
                    
                    # Checkpoint: save kill location for respawn
                    last_kill_x = hero_x
                    last_kill_y = hero_y
                    
                    # =====================================
                    # TODO 5: REPRODUCIR SONIDO AL DERROTAR ENEMIGO
                    # =====================================
                    # INSTRUCCIONES:
                    # Cuando derrotas a un enemigo, reproduce el sonido.
                    #
                    # TAREA:
                    # Reproduce enemy_defeat_sound si existe.
                    #
                    # ESCRIBE TU CÓDIGO AQUÍ:
                    if enemy_defeat_sound:
                        enemy_defeat_sound.play()
                    else:
                        print("ERROR: No hay un sonido al derrotar a un enemigo")
                    
                    break  # stop checking enemies this frame
                elif not invulnerable:
                    lives -= 1
                    
                    if hurt_sound:
                        hurt_sound.play()
                    
                    if lives <= 0:
                        game_over = True
                    else:
                        # Respawn at last kill checkpoint, or start
                        if last_kill_x is not None:
                            hero_x = last_kill_x
                            hero_y = last_kill_y
                        else:
                            hero_x = SPAWN_X
                            hero_y = SPAWN_Y
                        velocity_y = 0
                        invulnerable = True
                        invulnerable_timer = 0
                    
                    break

        # Sistema de invulnerabilidad
        if invulnerable:
            invulnerable_timer += 1
            if invulnerable_timer >= INVULNERABLE_DURATION:
                invulnerable = False
                invulnerable_timer = 0

        # Verificar condiciones de victoria
        if len(coins) == 0 and len(enemies) == 0:
            victory = True

        # Caída al vacío (huecos en el suelo)
        if hero_y > HEIGHT + 100:
            lives -= 1
            if hurt_sound:
                hurt_sound.play()
            if lives <= 0:
                game_over = True
            else:
                # Respawn at last kill checkpoint, or start
                if last_kill_x is not None:
                    hero_x = last_kill_x
                    hero_y = last_kill_y
                else:
                    hero_x = SPAWN_X
                    hero_y = SPAWN_Y
                velocity_y = 0
                invulnerable = True
                invulnerable_timer = 0

        # Actualización de la cámara
        hero_screen_x = hero_x - camera_x
        
        if hero_screen_x > CAMERA_DEAD_ZONE_RIGHT:
            camera_x = hero_x - CAMERA_DEAD_ZONE_RIGHT
        
        if hero_screen_x < CAMERA_DEAD_ZONE_LEFT:
            camera_x = hero_x - CAMERA_DEAD_ZONE_LEFT
        
        if camera_x < 0:
            camera_x = 0
        if camera_x > WORLD_WIDTH - WIDTH:
            camera_x = WORLD_WIDTH - WIDTH

        # Dibujo
        screen.fill(SKY)
        
        draw_world(screen, ground_sprite, camera_x)
        
        # Dibujar monedas
        for coin in coins:
            coin_screen_x = coin["x"] - camera_x
            coin_screen_y = coin["y"]
            
            if -TILE < coin_screen_x < WIDTH:
                screen.blit(coin_sprite, (coin_screen_x, coin_screen_y))
        
        # Dibujar enemigos
        for enemy in enemies:
            enemy_screen_x = enemy["x"] - camera_x
            enemy_screen_y = enemy["y"]
            
            if -TILE < enemy_screen_x < WIDTH:
                screen.blit(enemy_sprite, (enemy_screen_x, enemy_screen_y))

        # Dibujar al héroe
        if not invulnerable or (invulnerable_timer // 10) % 2 == 0:
            hero_screen_x = hero_x - camera_x
            screen.blit(hero_sprite, (hero_screen_x, hero_y))

        # HUD: vidas con corazón sprite
        lives_color = WHITE
        if lives == 2:
            lives_color = YELLOW
        elif lives == 1:
            lives_color = RED

        hud_bg = pygame.Surface((200, 70))
        hud_bg.set_alpha(140)
        hud_bg.fill(BLACK)
        screen.blit(hud_bg, (10, 6))

        # Fila 1: corazones × vidas
        for i in range(lives):
            screen.blit(hud_heart, (16 + i * (HUD_SIZE + 4), 12))
        lives_text = font.render(f" × {lives}", True, lives_color)
        screen.blit(lives_text, (16 + lives * (HUD_SIZE + 4), 14))

        # Fila 2: monedas recolectadas
        screen.blit(hud_coin, (16, 42))
        coin_count_text = font.render(
            f"{NUM_COINS - len(coins)}/{NUM_COINS}", True, GOLD
        )
        screen.blit(coin_count_text, (16 + HUD_SIZE + 4, 46))

        # Fila 2 (derecha): enemigos derrotados
        screen.blit(hud_enemy, (110, 42))
        enemy_count_text = font.render(
            f"{NUM_ENEMIES - len(enemies)}/{NUM_ENEMIES}", True, RED
        )
        screen.blit(enemy_count_text, (110 + HUD_SIZE + 4, 46))

        # Score (esquina superior derecha)
        score_text = font_score.render(f"Score: {score}", True, GOLD)
        score_rect = score_text.get_rect()
        score_rect.topright = (WIDTH - 20, 10)
        score_bg = pygame.Surface((score_rect.width + 20, score_rect.height + 10))
        score_bg.set_alpha(150)
        score_bg.fill(BLACK)
        screen.blit(score_bg, (score_rect.x - 10, score_rect.y - 5))
        screen.blit(score_text, score_rect)

        if invulnerable:
            invuln_text = font.render("✨ INVULNERABLE ✨", True, YELLOW)
            invuln_rect = invuln_text.get_rect(center=(WIDTH // 2, 20))
            screen.blit(invuln_text, invuln_rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    asyncio.run(main())