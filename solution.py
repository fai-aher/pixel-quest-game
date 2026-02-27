"""
Pixel Quest: The Jumping Hero
Módulo 1 - Semana 6 (Versión Final Completa - SOLUCIÓN)

VERSIÓN FINAL CON TODOS LOS TODOS COMPLETADOS
"""

import os
import sys
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

# Rutas
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
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


# -----------------------------
# MAPA DEL MUNDO (MÁS LARGO Y DESAFIANTE)
# -----------------------------

WORLD_MAP = [
    "................................................................",
    "................................................................",
    "................................................................",
    "................................................................",
    "..............................................G.................",
    "..........................................G...G.................",
    ".............................G............G...G......G..........",
    "...G..........G........G.....G............G...G......G..........",
    "...G..........G........G..GG.G............G...GG.....G..........",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGG........GGGGGGGGGGGGGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGG........GGGGGGGGGGGGGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGG........GGGGGGGGGGGGGGGGGGGGGGGGG",
]

WORLD_WIDTH = len(WORLD_MAP[0]) * TILE


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

def main() -> None:
    pygame.init()
    pygame.mixer.init()
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pixel Quest: The Jumping Hero - VERSIÓN FINAL")
    clock = pygame.time.Clock()

    # Cargar sprites
    hero_sprite = load_image("hero.png")
    ground_sprite = load_image("ground.png")
    coin_sprite = load_image("coin.png")
    enemy_sprite = load_image("enemy.png")

    # Fuentes
    font = pygame.font.SysFont("Arial", 18)
    font_large = pygame.font.SysFont("Arial", 48, bold=True)
    font_score = pygame.font.SysFont("Arial", 32, bold=True)

    # TODO 1 - COMPLETADO: Cargar sonidos
    jump_sound = load_sound("jump.wav")
    coin_sound = load_sound("coin.wav")
    enemy_defeat_sound = load_sound("enemy_defeat.wav")
    hurt_sound = load_sound("hurt.wav")
    victory_sound = load_sound("victory.wav")
    gameover_sound = load_sound("gameover.wav")
    
    # TODO 2 - COMPLETADO: Cargar y reproducir música de fondo
    try:
        pygame.mixer.music.load(os.path.join(SOUNDS_DIR, "background.ogg"))
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
        print("✓ Música de fondo cargada")
    except:
        print("⚠️ No se encontró música de fondo (opcional)")

    # Variables del juego
    lives = 3
    score = 0
    game_over = False
    victory = False
    victory_sound_played = False
    gameover_sound_played = False
    
    # Posición inicial del héroe
    SPAWN_X = 120
    SPAWN_Y = 300
    
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
    INVULNERABLE_DURATION = 120
    
    # Enemigos (8 enemigos en el nivel)
    ENEMY_1 = {"x": 400, "y": 384, "direction": 1, "speed": 2}
    ENEMY_2 = {"x": 650, "y": 384, "direction": -1, "speed": 1}
    ENEMY_3 = {"x": 900, "y": 384, "direction": 1, "speed": 2}
    ENEMY_4 = {"x": 1200, "y": 384, "direction": -1, "speed": 3}
    ENEMY_5 = {"x": 1500, "y": 336, "direction": 1, "speed": 1}
    ENEMY_6 = {"x": 1800, "y": 384, "direction": -1, "speed": 2}
    ENEMY_7 = {"x": 2200, "y": 384, "direction": 1, "speed": 2}
    ENEMY_8 = {"x": 2600, "y": 384, "direction": -1, "speed": 1}
    
    enemies = [
        ENEMY_1.copy(), ENEMY_2.copy(), ENEMY_3.copy(), ENEMY_4.copy(),
        ENEMY_5.copy(), ENEMY_6.copy(), ENEMY_7.copy(), ENEMY_8.copy()
    ]
    
    enemy_width = enemy_sprite.get_width()
    enemy_height = enemy_sprite.get_height()
    
    # Monedas (18 monedas en el nivel)
    coins = [
        {"x": 250, "y": 350},
        {"x": 400, "y": 300},
        {"x": 550, "y": 250},
        {"x": 700, "y": 350},
        {"x": 850, "y": 300},
        {"x": 1000, "y": 200},
        {"x": 1150, "y": 350},
        {"x": 1300, "y": 300},
        {"x": 1450, "y": 250},
        {"x": 1600, "y": 200},
        {"x": 1750, "y": 350},
        {"x": 1900, "y": 300},
        {"x": 2050, "y": 250},
        {"x": 2200, "y": 350},
        {"x": 2350, "y": 200},
        {"x": 2500, "y": 300},
        {"x": 2650, "y": 350},
        {"x": 2800, "y": 250},
    ]
    
    coin_width = coin_sprite.get_width()
    coin_height = coin_sprite.get_height()
    
    # Sistema de cámara
    camera_x = 0
    CAMERA_DEAD_ZONE_LEFT = WIDTH // 3
    CAMERA_DEAD_ZONE_RIGHT = WIDTH * 2 // 3

    running = True
    while running:
        dt = clock.tick(FPS)

        # Pantalla de victoria
        if victory:
            if not victory_sound_played:
                if victory_sound:
                    victory_sound.play()
                victory_sound_played = True
                pygame.mixer.music.stop()
            
            screen.fill(SKY)
            
            victory_text = font_large.render("¡VICTORIA!", True, GOLD)
            score_text = font_score.render(f"Puntaje Final: {score}", True, WHITE)
            stats_text = font.render(
                f"Monedas: {18 - len(coins)}/18 | Enemigos: {8 - len(enemies)}/8", 
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
                        enemies = [
                            ENEMY_1.copy(), ENEMY_2.copy(), ENEMY_3.copy(), ENEMY_4.copy(),
                            ENEMY_5.copy(), ENEMY_6.copy(), ENEMY_7.copy(), ENEMY_8.copy()
                        ]
                        coins = [
                            {"x": 250, "y": 350}, {"x": 400, "y": 300}, {"x": 550, "y": 250},
                            {"x": 700, "y": 350}, {"x": 850, "y": 300}, {"x": 1000, "y": 200},
                            {"x": 1150, "y": 350}, {"x": 1300, "y": 300}, {"x": 1450, "y": 250},
                            {"x": 1600, "y": 200}, {"x": 1750, "y": 350}, {"x": 1900, "y": 300},
                            {"x": 2050, "y": 250}, {"x": 2200, "y": 350}, {"x": 2350, "y": 200},
                            {"x": 2500, "y": 300}, {"x": 2650, "y": 350}, {"x": 2800, "y": 250},
                        ]
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
            if not gameover_sound_played:
                if gameover_sound:
                    gameover_sound.play()
                gameover_sound_played = True
                pygame.mixer.music.stop()
            
            screen.fill(BLACK)
            game_over_text = font_large.render("GAME OVER", True, RED)
            score_text = font_score.render(f"Puntaje: {score}", True, WHITE)
            stats_text = font.render(
                f"Monedas: {18 - len(coins)}/18 | Enemigos: {8 - len(enemies)}/8", 
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
                        enemies = [
                            ENEMY_1.copy(), ENEMY_2.copy(), ENEMY_3.copy(), ENEMY_4.copy(),
                            ENEMY_5.copy(), ENEMY_6.copy(), ENEMY_7.copy(), ENEMY_8.copy()
                        ]
                        coins = [
                            {"x": 250, "y": 350}, {"x": 400, "y": 300}, {"x": 550, "y": 250},
                            {"x": 700, "y": 350}, {"x": 850, "y": 300}, {"x": 1000, "y": 200},
                            {"x": 1150, "y": 350}, {"x": 1300, "y": 300}, {"x": 1450, "y": 250},
                            {"x": 1600, "y": 200}, {"x": 1750, "y": 350}, {"x": 1900, "y": 300},
                            {"x": 2050, "y": 250}, {"x": 2200, "y": 350}, {"x": 2350, "y": 200},
                            {"x": 2500, "y": 300}, {"x": 2650, "y": 350}, {"x": 2800, "y": 250},
                        ]
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

        # Movimiento horizontal
        new_hero_x = hero_x
        
        if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            new_hero_x = hero_x - HERO_SPEED
        elif keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            new_hero_x = hero_x + HERO_SPEED
        
        collision = check_collision_with_tiles(new_hero_x, hero_y, hero_width, hero_height)
        
        if new_hero_x < hero_x and not collision['left']:
            hero_x = new_hero_x
        elif new_hero_x > hero_x and not collision['right']:
            hero_x = new_hero_x
        
        if hero_x < 0:
            hero_x = 0
        if hero_x > WORLD_WIDTH - hero_width:
            hero_x = WORLD_WIDTH - hero_width

        # Salto
        if keys[pygame.K_SPACE] and on_ground:
            velocity_y = JUMP_POWER
            on_ground = False
            
            # TODO 3 - COMPLETADO: Reproducir sonido de salto
            if jump_sound:
                jump_sound.play()

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
                
                # TODO 4 - COMPLETADO: Reproducir sonido de moneda
                if coin_sound:
                    coin_sound.play()

        # Actualizar enemigos
        for enemy in enemies:
            enemy["x"] += enemy["direction"] * enemy["speed"]
            
            collision = check_collision_with_tiles(
                enemy["x"], 
                enemy["y"], 
                enemy_width, 
                enemy_height
            )
            
            if collision['left'] or collision['right']:
                enemy["direction"] *= -1
                enemy["x"] += enemy["direction"] * enemy["speed"]

        # Colisiones con enemigos
        for enemy in enemies[:]:
            hay_colision = check_rect_collision(
                hero_x, hero_y, hero_width, hero_height,
                enemy["x"], enemy["y"], enemy_width, enemy_height
            )
            
            if hay_colision:
                esta_arriba = (hero_y + hero_height) <= (enemy["y"] + 10)
                esta_cayendo = velocity_y > 0
                
                if esta_arriba and esta_cayendo:
                    enemies.remove(enemy)
                    score += POINTS_ENEMY
                    velocity_y = -10
                    
                    # TODO 5 - COMPLETADO: Reproducir sonido al derrotar enemigo
                    if enemy_defeat_sound:
                        enemy_defeat_sound.play()
                    
                elif not invulnerable:
                    lives -= 1
                    
                    if hurt_sound:
                        hurt_sound.play()
                    
                    if lives <= 0:
                        game_over = True
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

        # HUD mejorado
        score_text = font_score.render(f"Score: {score}", True, GOLD)
        score_rect = score_text.get_rect()
        score_rect.topright = (WIDTH - 20, 10)
        
        score_bg = pygame.Surface((score_rect.width + 20, score_rect.height + 10))
        score_bg.set_alpha(150)
        score_bg.fill(BLACK)
        screen.blit(score_bg, (score_rect.x - 10, score_rect.y - 5))
        screen.blit(score_text, score_rect)
        
        lives_color = WHITE
        if lives == 2:
            lives_color = YELLOW
        elif lives == 1:
            lives_color = RED
        
        lives_text = font.render(f"Lives: {lives}", True, lives_color)
        screen.blit(lives_text, (20, 12))
        
        objectives_text = font.render(
            f"Monedas: {18 - len(coins)}/18 | Enemigos: {8 - len(enemies)}/8", 
            True, WHITE
        )
        screen.blit(objectives_text, (20, 40))
        
        if invulnerable:
            invuln_text = font.render("INVULNERABLE!", True, YELLOW)
            invuln_rect = invuln_text.get_rect(center=(WIDTH // 2, 20))
            screen.blit(invuln_text, invuln_rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()