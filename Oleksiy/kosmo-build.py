import pygame
import sys
import random
import math

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Конструктор космічних кораблів")
clock = pygame.time.Clock()

# Кольори
BACKGROUND = (10, 14, 22)
WHITE = (235, 235, 235)
BUTTON = (40, 50, 70)
BUTTON_HOVER = (60, 75, 100)
BUTTON_SELECTED = (75, 95, 125)
GRID_COLOR = (55, 65, 85)
GRID_HOVER = (80, 100, 130)
CELL_BACKGROUND = (18, 23, 34)
HULL_COLOR = (100, 115, 135)
HULL_HOVER = (130, 145, 165)

MENU = "menu"
CONSTRUCTOR = "constructor"
GAME = "game"
EXPLOSION = "explosion"
GAME_OVER = "game over"
VICTORY = "victory"
current_screen = MENU

# Шрифти
title_font = pygame.font.Font(None, int(HEIGHT * 0.07))
button_font = pygame.font.Font(None, int(HEIGHT * 0.035))
small_font = pygame.font.Font(None, int(HEIGHT * 0.025))

EVENT_NONE = None
EVENT_METEOR_SHOWER = "meteor_shower"
EVENT_ENEMY_SHIP = "enemy_ship"
EVENT_ELITE_ENEMY_SHIP = "elite_enemy_ship"
EVENT_COMET = "comet"
EVENT_SUN_FLYBY = "sun_flyby"
EVENT_STARDUST = "stardust"
EVENT_TURBULENCE = "turbulence"
EVENT_FINAL_BOSS = "final_boss"
EVENT_LIST = [
    EVENT_METEOR_SHOWER,
    EVENT_ENEMY_SHIP,
    EVENT_COMET,
    EVENT_SUN_FLYBY,
]
EVENT_LIST_STAGE_2 = [
    *EVENT_LIST,
    EVENT_ELITE_ENEMY_SHIP,
    EVENT_TURBULENCE,
]
EVENT_LIST_STAGE_3 = [
    *EVENT_LIST,
    EVENT_ELITE_ENEMY_SHIP,
    EVENT_STARDUST,
]
EVENT_LISTS = {
    1: EVENT_LIST,
    2: EVENT_LIST_STAGE_2,
    3: EVENT_LIST_STAGE_3,
}
EVENT_STAGE = 1
EVENTS_BEFORE_CONSTRUCTOR = {1: 10, 2: 15, 3: 20}
completed_events = 0
current_event = EVENT_NONE
event_start_time = 2
EVENT_DURATION = 20
STARDUST_DARKEN_DELAY = 4
STARDUST_EVENT_DURATION = 1
STARDUST_KEYS_TO_CLEAR = 6
STARDUST_KEY_LABELS = {
    pygame.K_z: "Z",
    pygame.K_x: "X",
    pygame.K_c: "C",
    pygame.K_v: "V",
}
EVENT_INTERVAL = 4
TURBULENCE_EVENT_DURATION = 1
TURBULENCE_EFFECT_DURATION = 15
TURBULENCE_SHAKE_AMPLITUDE = 4
FINAL_BOSS_METEOR_INTERVAL = 5
last_event_time = 0
# Таймер метеоритного дощу
meteor_spawn_timer = 0
meteor_spawn_delay = 1.5

# Поле
GRID_SIZE = 15
CELL_SIZE = int(HEIGHT * 0.055)
GRID_WIDTH = GRID_SIZE * CELL_SIZE
GRID_HEIGHT = GRID_SIZE * CELL_SIZE
GRID_X = WIDTH // 2 - GRID_WIDTH // 2 - 120
GRID_Y = HEIGHT // 2 - GRID_HEIGHT // 2
GAME_CELL_SIZE = CELL_SIZE // 2
MAX_MODULES = 25
# Інші налаштування
ship_x = 0
ship_y = 0
game_speed = 1.5
stars = []
bullets = []
rocket_projectiles = []
rocket_impacts = []
meteors = []
enemy_ship = None
comet = None
comet_sparks = []
stardust_particles = []
stardust_active = False
stardust_started_at = 0
stardust_blinded = False
stardust_key_sequence = []
stardust_key_index = 0
stardust_fog_alpha = 0
stardust_fog_started_at = 0
stardust_fog_fade_started_at = None
stardust_fog_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
turbulence_end_time = 0
gameplay_surface = pygame.Surface((WIDTH, HEIGHT))
final_boss_meteor_timer = 0
sun = None
ship_gravity_velocity_x = 0
explosion_particles = []
enemy_explosion_particles = []
explosion_start_time = 0
explosion_center = (0, 0)
EXPLOSION_DURATION = 2.3

# Класи модулів
class Module:
    def __init__(self, name, mass, barrier):
        self.name = name
        self.mass = mass
        self.barrier = barrier
class Hull(Module):
    def __init__(self):
        super().__init__("Корпус", 10, 15)
class Engine(Module):
    def __init__(self):
        super().__init__("Двигун", 25, 8)
        self.thrust = 100
class Armor(Module):
    def __init__(self):
        super().__init__("Броня", 40, 45)
class Reactor(Module):
    def __init__(self):
        super().__init__("Реактор", 50, 25)
class BrokenReactor(Module):
    def __init__(self):
        super().__init__("Зламаний реактор", 50, 120)
class Cannon(Module):
    def __init__(self):
        super().__init__("Пушка X-01", 25, 12)
        self.damage = 3
        self.coldown = 1.7
class RocketLauncher(Module):
    def __init__(self):
        super().__init__("Ракетниця", 70, 20)
        self.damage = 17
        self.coldown = 8.5
        self.last_shot = -8.5

class Bullet:
    def __init__(self, x, y, damage, velocity_x=0, velocity_y=-8, owner="player"):
        self.x = x
        self.y = y
        self.damage = damage
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.owner = owner

class RocketProjectile:
    def __init__(self, x, y, velocity_x=0, velocity_y=-4, owner="player"):
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.owner = owner
        self.width = 7
        self.height = 16

    def rect(self):
        return pygame.Rect(
            int(self.x - self.width / 2),
            int(self.y - self.height / 2),
            self.width,
            self.height,
        )

class RocketImpact:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frames_left = 9
class Meteor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 4
        self.damage = 20
        self.radius = 24

class Comet:
    def __init__(self):
        self.x = -100
        self.y = HEIGHT * 0.48
        self.speed = 8
        self.radius = 42
        self.last_spark_time = 0

class CometSpark:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # Іскри розлітаються переважно вбік від горизонтальної траєкторії комети.
        angle = random.choice((random.uniform(35, 145), random.uniform(215, 325)))
        angle = math.radians(angle)
        speed = random.uniform(2.5, 6)
        self.velocity_x = math.cos(angle) * speed
        self.velocity_y = math.sin(angle) * speed
        self.life = random.uniform(1.2, 2.0)
        self.radius = random.randint(2, 4)

class StardustParticle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.radius = random.randint(1, 4)
        self.speed_x = random.uniform(-0.8, 0.8)
        self.speed_y = random.uniform(0.4, 2.0)
        self.color = random.choice(((180, 205, 255), (225, 190, 255), (255, 220, 165)))

class ExplosionParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.tau)
        speed = random.uniform(2, 8)
        self.velocity_x = math.cos(angle) * speed
        self.velocity_y = math.sin(angle) * speed
        self.life = random.uniform(1.1, 2.3)
        self.max_life = self.life
        self.size = random.randint(3, 9)
        self.color = color

class EnemyExplosionParticle:
    def __init__(self, x, y, color):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(0.8, 3.2)
        self.x = x
        self.y = y
        self.velocity_x = math.cos(angle) * speed
        self.velocity_y = math.sin(angle) * speed
        self.life = random.uniform(0.4, 0.9)
        self.max_life = self.life
        self.size = random.randint(2, 5)
        self.color = color

class Sun:
    def __init__(self):
        self.radius = 2 * max(90, int(HEIGHT * 0.12))
        self.x = random.choice((self.radius * 0.6, WIDTH - self.radius * 0.6))
        self.y = -self.radius
        self.speed = 1.5
        self.damage_timer = 0

class EnemyShip:
    def __init__(self, name, grid, x, y, target_y, is_elite=False, is_final_boss=False):
        self.name = name
        self.is_elite = is_elite
        self.is_final_boss = is_final_boss
        self.grid = grid
        self.x = x
        self.y = y
        self.target_y = target_y
        self.width = len(grid[0]) * GAME_CELL_SIZE
        self.height = len(grid) * GAME_CELL_SIZE
        self.initial_block_count = sum(
            module is not None for row in grid for module in row
        )
        self.initial_health = sum(
            module.barrier for row in grid for module in row if module is not None
        )
        self.destroyed_blocks = 0
        self.reactor_destroyed = False
        self.speed = 0
        self.last_shot = {}
        self.exploding = False
        self.explosion_end_time = 0

    def alive_modules(self):
        return [module for row in self.grid for module in row if module is not None]


def get_module_info(module):
    if module is None:
        return []
    info = [
        f"Назва: {module.name}",
        f"Маса: {module.mass}",
        f"Прочність: {module.barrier}"
    ]
    if isinstance(module, Engine):
        info.append(f"Тяга: {module.thrust}")
    if isinstance(module, RocketLauncher):
        info.append(f"Кулдаун: {module.coldown} с")
    return info
def get_ship_stats():
    mass = 0
    thrust = 0
    for row in ship_grid:
        for module in row:
            if module is not None:
                mass += module.mass
                if isinstance(module, Engine):
                    thrust += module.thrust
    if reactor_active():
        thrust *= 2
    return mass, thrust

# Об'єкт корпусу
hull_module = Hull()
engine_module = Engine()
armor_module = Armor()
reactor_module = Reactor()
cannon_module = Cannon()
rocket_launcher_module = RocketLauncher()
# Поле корабля
ship_grid = [
    [None for _ in range(GRID_SIZE)]
    for _ in range(GRID_SIZE)
]

# Вибраний модуль
selected_module = None
selected_block = None
ship_error = ""
# Панель
PANEL_WIDTH = 280
MODULE_PANEL_HEIGHT = 600
SHIP_PANEL_HEIGHT = 170

PANEL_X = WIDTH - PANEL_WIDTH - 60
MODULE_PANEL_Y = 70
SHIP_PANEL_Y = MODULE_PANEL_Y + MODULE_PANEL_HEIGHT + 20

def has_reactor():
    for row in ship_grid:
        for module in row:
            if isinstance(module, Reactor):
                return True
    return False

def reactor_active():
    for row in ship_grid:
        for module in row:
            if isinstance(module, Reactor):
                return module.barrier > 0
    return False

def get_module_count():
    count = 0
    for row in ship_grid:
        for module in row:
            if module is not None:
                count += 1
    return count

def validate_ship():
    module_count = get_module_count()
    if module_count < 8:
        return False, "Корабель не надійний та не може існувати"
    for row in range(15):
        for col in range(15):
            if ship_grid[row][col] is not None:
                has_neighbor = False
                if row > 0 and ship_grid[row - 1][col] is not None:
                    has_neighbor = True
                if row < 14 and ship_grid[row + 1][col] is not None:
                    has_neighbor = True
                if col > 0 and ship_grid[row][col - 1] is not None:
                    has_neighbor = True
                if col < 14 and ship_grid[row][col + 1] is not None:
                    has_neighbor = True
                if not has_neighbor:
                    return False, "Кожна деталь повинна мати сусіда"
    return True, ""

def spawn_meteor():
    x = random.randint(50, WIDTH - 50)
    y = -50
    meteors.append(Meteor(x, y))

def shoot():
    reactor_active = has_reactor()
    for row in range(15):
        for col in range(15):
            module = ship_grid[row][col]
            if isinstance(module, Cannon):
                current_time = pygame.time.get_ticks() / 1000
                if current_time - getattr(module, "last_shot", 0) >= module.coldown:
                    x = ship_x + col * GAME_CELL_SIZE + GAME_CELL_SIZE // 2
                    y = ship_y + row * GAME_CELL_SIZE + GAME_CELL_SIZE // 2
                    damage = module.damage
                    if reactor_active:
                        damage *= 2
                    bullets.append(Bullet(x, y, damage))
                    module.last_shot = current_time

def shoot_rockets():
    current_time = pygame.time.get_ticks() / 1000
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            module = ship_grid[row][col]
            if not isinstance(module, RocketLauncher):
                continue
            if current_time - module.last_shot < module.coldown:
                continue
            x = ship_x + col * GAME_CELL_SIZE + GAME_CELL_SIZE // 2
            y = ship_y + row * GAME_CELL_SIZE + GAME_CELL_SIZE // 2
            rocket_projectiles.append(RocketProjectile(x, y))
            module.last_shot = current_time

def shoot_enemy_rockets(enemy):
    current_time = pygame.time.get_ticks() / 1000
    for row_index, row in enumerate(enemy.grid):
        for col_index, module in enumerate(row):
            if not isinstance(module, RocketLauncher):
                continue
            key = (row_index, col_index)
            if current_time - enemy.last_shot.get(key, -module.coldown) < module.coldown:
                continue
            x = enemy.x + col_index * GAME_CELL_SIZE + GAME_CELL_SIZE / 2
            y = enemy.y + row_index * GAME_CELL_SIZE + GAME_CELL_SIZE / 2
            speed = 4
            rocket_projectiles.append(RocketProjectile(
                x, y, 0, speed, owner="enemy"
            ))
            enemy.last_shot[key] = current_time

def draw_bullets():
    for bullet in bullets:
        pygame.draw.circle(
            screen,
            (255, 220, 80) if bullet.owner == "player" else (255, 90, 90),
            (int(bullet.x), int(bullet.y)),
            4
        )
def update_bullets():
    for bullet in bullets[:]:
        bullet.x += bullet.velocity_x
        bullet.y += bullet.velocity_y
        if bullet.y < 0 or bullet.y > HEIGHT or bullet.x < 0 or bullet.x > WIDTH:
            bullets.remove(bullet)
            continue

        if bullet.owner == "player" and enemy_ship is not None:
            hit = False
            for row_index, row in enumerate(enemy_ship.grid):
                for col_index, module in enumerate(row):
                    if module is None:
                        continue
                    rect = pygame.Rect(
                        enemy_ship.x + col_index * GAME_CELL_SIZE,
                        enemy_ship.y + row_index * GAME_CELL_SIZE,
                        GAME_CELL_SIZE,
                        GAME_CELL_SIZE,
                    )
                    if rect.collidepoint(bullet.x, bullet.y):
                        module.barrier -= bullet.damage
                        if module.barrier <= 0:
                            if isinstance(module, Reactor):
                                enemy_ship.reactor_destroyed = True
                            enemy_ship.grid[row_index][col_index] = None
                            enemy_ship.destroyed_blocks += 1
                        bullets.remove(bullet)
                        hit = True
                        break
                if hit:
                    break
            if hit:
                continue

        elif bullet.owner == "enemy":
            for row_index, row in enumerate(ship_grid):
                for col_index, module in enumerate(row):
                    if module is None:
                        continue
                    rect = pygame.Rect(
                        ship_x + col_index * GAME_CELL_SIZE,
                        ship_y + row_index * GAME_CELL_SIZE,
                        GAME_CELL_SIZE,
                        GAME_CELL_SIZE,
                    )
                    if rect.collidepoint(bullet.x, bullet.y):
                        module.barrier -= bullet.damage
                        bullets.remove(bullet)
                        break
                else:
                    continue
                break

def update_rockets():
    for rocket in rocket_projectiles[:]:
        rocket.x += rocket.velocity_x
        rocket.y += rocket.velocity_y
        if (rocket.y + rocket.height < 0 or rocket.y > HEIGHT or
                rocket.x + rocket.width < 0 or rocket.x > WIDTH):
            rocket_projectiles.remove(rocket)
            continue
        if rocket.owner == "player":
            target_grid = enemy_ship.grid if enemy_ship is not None else None
            target_x = enemy_ship.x if enemy_ship is not None else 0
            target_y = enemy_ship.y if enemy_ship is not None else 0
        else:
            target_grid = ship_grid
            target_x = ship_x
            target_y = ship_y
        if target_grid is None:
            continue

        rocket_rect = rocket.rect()
        hit = False
        for row_index, row in enumerate(target_grid):
            for col_index, module in enumerate(row):
                if module is None:
                    continue
                module_rect = pygame.Rect(
                    target_x + col_index * GAME_CELL_SIZE,
                    target_y + row_index * GAME_CELL_SIZE,
                    GAME_CELL_SIZE,
                    GAME_CELL_SIZE,
                )
                if not rocket_rect.colliderect(module_rect):
                    continue

                impact_x, impact_y = module_rect.center
                rocket_impacts.append(RocketImpact(impact_x, impact_y))
                for row_delta, col_delta, damage in (
                    (0, 0, 15),
                    (-1, 0, 4),
                    (1, 0, 4),
                    (0, -1, 4),
                    (0, 1, 4),
                ):
                    target_row = row_index + row_delta
                    target_col = col_index + col_delta
                    if not (0 <= target_row < len(target_grid)):
                        continue
                    if not (0 <= target_col < len(target_grid[target_row])):
                        continue
                    target = target_grid[target_row][target_col]
                    if target is None:
                        continue
                    target.barrier -= damage
                    if target.barrier <= 0:
                        if target_grid is not ship_grid:
                            if isinstance(target, Reactor):
                                enemy_ship.reactor_destroyed = True
                            enemy_ship.destroyed_blocks += 1
                        target_grid[target_row][target_col] = None
                rocket_projectiles.remove(rocket)
                hit = True
                break
            if hit:
                break

    for impact in rocket_impacts[:]:
        impact.frames_left -= 1
        if impact.frames_left <= 0:
            rocket_impacts.remove(impact)

def draw_rocket_effects():
    for rocket in rocket_projectiles:
        rocket_rect = rocket.rect()
        rocket_color = (240, 105, 35) if rocket.owner == "player" else (220, 65, 65)
        pygame.draw.rect(screen, rocket_color, rocket_rect, border_radius=2)
        pygame.draw.rect(
            screen,
            (255, 220, 130),
            pygame.Rect(rocket_rect.x + 2, rocket_rect.y + 2, max(1, rocket_rect.width - 4), 4),
            border_radius=1,
        )
    for impact in rocket_impacts:
        radius = round(2.3 * max(2, 10 - impact.frames_left))
        pygame.draw.circle(screen, (235, 95, 35), (int(impact.x), int(impact.y)), radius)
        pygame.draw.circle(screen, (255, 205, 115), (int(impact.x), int(impact.y)), max(1, radius // 2))

def check_meteor_collision(meteor):
    nearest_module = None
    nearest_distance = float("inf")
    for row in range(15):
        for col in range(15):
            module = ship_grid[row][col]
            if module is None:
                continue
            block_x = ship_x + col * GAME_CELL_SIZE
            block_y = ship_y + row * GAME_CELL_SIZE
            block_rect = pygame.Rect(block_x, block_y, GAME_CELL_SIZE, GAME_CELL_SIZE)
            closest_x = max(block_rect.left, min(meteor.x, block_rect.right))
            closest_y = max(block_rect.top, min(meteor.y, block_rect.bottom))
            dx = meteor.x - closest_x
            dy = meteor.y - closest_y
            if dx * dx + dy * dy <= meteor.radius * meteor.radius:
                center_x = block_x + GAME_CELL_SIZE / 2
                center_y = block_y + GAME_CELL_SIZE / 2
                distance = (meteor.x - center_x) ** 2 + (meteor.y - center_y) ** 2
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_module = module
    if nearest_module is None:
        return
    nearest_module.barrier -= meteor.damage
    meteors.remove(meteor)


def update_meteors():
    for meteor in meteors[:]:
        meteor.y += meteor.speed
        if meteor.y > HEIGHT + 50:
            meteors.remove(meteor)
            continue
        check_meteor_collision(meteor)

def draw_meteors():
    for meteor in meteors:
        x = int(meteor.x)
        y = int(meteor.y)
        r = meteor.radius
        points = []
        for i in range(10):
            angle = math.radians(i * 36)
            radius = r * random.uniform(0.8, 1.15)
            px = x + math.cos(angle) * radius
            py = y + math.sin(angle) * radius
            points.append((int(px), int(py)))
        pygame.draw.polygon(screen, (85, 80, 75), points)
        pygame.draw.polygon(screen, (45, 42, 40), points, 2)
        # Кратери
        craters = [
            (-r * 0.35, -r * 0.25, r * 0.18),
            (r * 0.30, -r * 0.10, r * 0.13),
            (-r * 0.10, r * 0.30, r * 0.15),
            (r * 0.35, r * 0.30, r * 0.10)
        ]
        for ox, oy, cr in craters:
            pygame.draw.circle(screen,(55, 52, 50),(int(x + ox), int(y + oy)),int(cr))
            pygame.draw.circle(screen, (110, 105, 98),(int(x + ox - cr * 0.25), int(y + oy - cr * 0.25)),max(1, int(cr * 0.35)))

def draw_button(text, rect, selected=False):
    mouse_pos = pygame.mouse.get_pos()

    if selected:
        color = BUTTON_SELECTED
    elif rect.collidepoint(mouse_pos):
        color = BUTTON_HOVER
    else:
        color = BUTTON

    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, rect, width=2, border_radius=10)

    text_surface = button_font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)
def draw_launch_button():
    launch_button = pygame.Rect(WIDTH - 750, HEIGHT - 65, 270, 55)
    draw_button(
        "ЗАПУСТИТИ КОРАБЕЛЬ",
        launch_button,
        False
    )
    return launch_button

def draw_menu():
    screen.fill(BACKGROUND)

    title = title_font.render(
        "КОНСТРУКТОР КОСМІЧНИХ КОРАБЛІВ",
        True,
        WHITE
    )
    title_rect = title.get_rect(
        center=(WIDTH // 2, HEIGHT * 0.25)
    )
    screen.blit(title, title_rect)

    construct_button = pygame.Rect(
        WIDTH * 0.35,
        HEIGHT * 0.45,
        WIDTH * 0.30,
        HEIGHT * 0.09
    )
    draw_button("КОНСТРУЮВАТИ", construct_button)

    exit_button = pygame.Rect(
        WIDTH * 0.35,
        HEIGHT * 0.58,
        WIDTH * 0.30,
        HEIGHT * 0.09
    )
    draw_button("ВИХІД", exit_button)

    return construct_button, exit_button


def get_grid_cell(mouse_pos):
    mouse_x, mouse_y = mouse_pos

    if not (
        GRID_X <= mouse_x < GRID_X + GRID_WIDTH
        and GRID_Y <= mouse_y < GRID_Y + GRID_HEIGHT
    ):
        return None

    col = (mouse_x - GRID_X) // CELL_SIZE
    row = (mouse_y - GRID_Y) // CELL_SIZE

    return row, col

def draw_constructor_module_details(module, cell_rect):
    """Draws module-specific details for the constructor grid only."""
    body = cell_rect.inflate(-14, -14)
    cx, cy = body.center
    detail = (225, 230, 238)
    line_width = max(1, CELL_SIZE // 20)

    if isinstance(module, Reactor):
        pygame.draw.circle(screen, detail, (cx+1, cy), max(5, body.width // 3), width=line_width)
        pygame.draw.circle(screen, detail, (cx+1, cy), max(2, body.width // 8), width=line_width)
        for angle in (0, 90, 180, 270):
            radians = math.radians(angle)
            start = (int(cx + math.cos(radians) * body.width * 0.12), int(cy + math.sin(radians) * body.height * 0.24))
            end = (int(cx + math.cos(radians) * body.width * 0.28), int(cy + math.sin(radians) * body.height * 0.56))
            pygame.draw.line(screen, detail, start, end, line_width)


def draw_grid():
    mouse_cell = get_grid_cell(pygame.mouse.get_pos())

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = GRID_X + col * CELL_SIZE
            y = GRID_Y + row * CELL_SIZE
            cell_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            module = ship_grid[row][col]

            pygame.draw.rect(
                screen,
                CELL_BACKGROUND,
                cell_rect
            )

            if isinstance(module, Hull):
                hull_rect = pygame.Rect(
                    x + 4,
                    y + 4,
                    CELL_SIZE - 8,
                    CELL_SIZE - 8
                )

                color = HULL_HOVER if mouse_cell == (row, col) else HULL_COLOR

                pygame.draw.rect(
                    screen,
                    color,
                    hull_rect,
                    border_radius=4
                )

                pygame.draw.rect(
                    screen,
                    WHITE,
                    hull_rect,
                    width=1,
                    border_radius=4
                )
            elif isinstance(module, Engine):
                engine_rect = pygame.Rect(
                    x + 4,
                    y + 4,
                    CELL_SIZE - 8,
                    CELL_SIZE - 8
                )
                pygame.draw.rect(
                    screen,
                    (150, 80, 50),
                    engine_rect,
                    border_radius=4
                )
                pygame.draw.rect(
                    screen,
                    WHITE,
                    engine_rect,
                    width=1,
                    border_radius=4
                )
            elif isinstance(module, Armor):
                armor_rect = pygame.Rect(
                    x + 4,
                    y + 4,
                    CELL_SIZE - 8,
                    CELL_SIZE - 8
                )

                color = (90, 90, 100)

                if mouse_cell == (row, col):
                    color = (120, 120, 135)

                pygame.draw.rect(
                    screen,
                    color,
                    armor_rect,
                    border_radius=4
                )

                pygame.draw.rect(
                    screen,
                    WHITE,
                    armor_rect,
                    width=2,
                    border_radius=4
                )
            elif isinstance(module, Reactor):
                reactor_rect = pygame.Rect(
                    x + 4,
                    y + 4,
                    CELL_SIZE - 8,
                    CELL_SIZE - 8
                )

                color = (40, 100, 220)

                if mouse_cell == (row, col):
                    color = (60, 130, 255)

                pygame.draw.rect(
                    screen,
                    color,
                    reactor_rect,
                    border_radius=4
                )

                pygame.draw.rect(
                    screen,
                    WHITE,
                    reactor_rect,
                    width=2,
                    border_radius=4
                )
            elif isinstance(module, Cannon):
                cannon_rect = pygame.Rect(
                    x + 4,
                    y + 4,
                    CELL_SIZE - 8,
                    CELL_SIZE - 8
                )
                color = (170, 60, 60)
                if mouse_cell == (row, col):
                    color = (210, 80, 80)
                pygame.draw.rect(
                    screen,
                    color,
                    cannon_rect,
                    border_radius=4
                )
                pygame.draw.rect(
                    screen,
                    WHITE,
                    cannon_rect,
                    width=2,
                    border_radius=4
                )
            elif mouse_cell == (row, col):
                pygame.draw.rect(
                    screen,
                    GRID_HOVER,
                    cell_rect
                )

            if module is not None and not isinstance(module, RocketLauncher):
                draw_constructor_module_details(module, cell_rect)

            pygame.draw.rect(
                screen,
                GRID_COLOR,
                cell_rect,
                width=1
            )

def draw_modules_panel():
    reactor_exists = has_reactor()
    panel_rect = pygame.Rect(
        PANEL_X,
        MODULE_PANEL_Y,
        PANEL_WIDTH,
        MODULE_PANEL_HEIGHT
    )

    pygame.draw.rect(screen, (16, 21, 32), panel_rect, border_radius=15)
    pygame.draw.rect(screen, GRID_COLOR, panel_rect, width=2, border_radius=15)

    title = button_font.render("МОДУЛІ", True, WHITE)
    title_rect = title.get_rect(
        center=(PANEL_X + PANEL_WIDTH // 2, MODULE_PANEL_Y + 40)
    )
    screen.blit(title, title_rect)

    hull_button = pygame.Rect(
        PANEL_X + 30,
        MODULE_PANEL_Y + 80,
        PANEL_WIDTH - 60,
        60
    )

    engine_button = pygame.Rect(
        PANEL_X + 30,
        MODULE_PANEL_Y + 150,
        PANEL_WIDTH - 60,
        60
    )
    armor_button = pygame.Rect(
        PANEL_X + 30,
        MODULE_PANEL_Y + 220,
        PANEL_WIDTH - 60,
        60
    )
    reactor_button = pygame.Rect(
        PANEL_X + 30,
        MODULE_PANEL_Y + 290,
        PANEL_WIDTH - 60,
        60
    )
    cannon_button = pygame.Rect(
        PANEL_X + 30,
        MODULE_PANEL_Y + 360,
        PANEL_WIDTH - 60,
        60
    )

    draw_button(
        "КОРПУС",
        hull_button,
        selected_module is hull_module
    )

    draw_button(
        "ДВИГУН",
        engine_button,
        selected_module is engine_module
    )
    draw_button(
        "БРОНЯ",
        armor_button,
        selected_module is armor_module
    )
    draw_button(
        "РЕАКТОР",
        reactor_button,
        selected_module is reactor_module
    )
    draw_button(
        "ПУШКА X-01",
        cannon_button,
        selected_module is cannon_module
    )
    info_module = None

    if selected_block is not None:
        info_module = selected_block
    elif selected_module is not None:
        info_module = selected_module

    if info_module is not None:
        info = get_module_info(info_module)
        y = MODULE_PANEL_Y + 500

        for line in info:
            text = small_font.render(line, True, WHITE)
            screen.blit(text, (PANEL_X + 30, y))
            y += 26
def draw_ship_panel():
    panel_rect = pygame.Rect(
        PANEL_X,
        SHIP_PANEL_Y,
        PANEL_WIDTH,
        SHIP_PANEL_HEIGHT
    )

    pygame.draw.rect(
        screen,
        (16, 21, 32),
        panel_rect,
        border_radius=15
    )

    pygame.draw.rect(
        screen,
        GRID_COLOR,
        panel_rect,
        width=2,
        border_radius=15
    )

    title = button_font.render(
        "КОРАБЕЛЬ",
        True,
        WHITE
    )

    title_rect = title.get_rect(
        center=(
            PANEL_X + PANEL_WIDTH // 2,
            SHIP_PANEL_Y + 40
        )
    )

    screen.blit(title, title_rect)

    mass, thrust = get_ship_stats()

    mass_text = small_font.render(
        f"Маса: {mass}",
        True,
        WHITE
    )

    screen.blit(
        mass_text,
        (PANEL_X + 30, SHIP_PANEL_Y + 80)
    )

    thrust_text = small_font.render(
        f"Тяга: {thrust}",
        True,
        WHITE
    )

    screen.blit(
        thrust_text,
        (PANEL_X + 30, SHIP_PANEL_Y + 110)
    )
    module_count = get_module_count()
    modules_text = small_font.render(
        f"Блоки: {module_count} / {MAX_MODULES}",
        True,
        WHITE
    )
    screen.blit(
        modules_text,
        (PANEL_X + 30, SHIP_PANEL_Y + 140)
    )

def draw_rocket_launcher_modules(in_game=False):
    for row_index, row in enumerate(ship_grid):
        for col_index, module in enumerate(row):
            if not isinstance(module, RocketLauncher):
                continue
            cell_size = GAME_CELL_SIZE if in_game else CELL_SIZE
            if in_game:
                x = ship_x + col_index * cell_size
                y = ship_y + row_index * cell_size
            else:
                x = GRID_X + col_index * cell_size
                y = GRID_Y + row_index * cell_size
            padding = max(1, cell_size // 10)
            body = pygame.Rect(
                x + padding,
                y + padding,
                cell_size - 2 * padding,
                cell_size - 2 * padding,
            )
            pygame.draw.rect(screen, (115, 145, 65), body, border_radius=4)
            pygame.draw.rect(screen, WHITE, body, width=2, border_radius=4)
            tube_width = max(5, CELL_SIZE // 6)
            pygame.draw.rect(
                screen,
                (220, 205, 150),
                pygame.Rect(body.centerx - tube_width // 2, body.top + 3, tube_width, body.height // 2),
                border_radius=2,
            )

def draw_constructor():
    screen.fill(BACKGROUND)

    title = title_font.render(
        "КОНСТРУКТОР",
        True,
        WHITE
    )

    title_rect = title.get_rect(
        center=(WIDTH // 2, HEIGHT * 0.07)
    )

    screen.blit(title, title_rect)

    draw_grid()
    draw_rocket_launcher_modules()
    draw_modules_panel()
    draw_button(
        "РАКЕТНИЦЯ",
        pygame.Rect(PANEL_X + 30, MODULE_PANEL_Y + 430, PANEL_WIDTH - 60, 60),
        selected_module is rocket_launcher_module,
    )
    draw_ship_panel()

    info = small_font.render(
        "ПОЛЕ 15 × 15",
        True,
        WHITE
    )

    info_rect = info.get_rect(
        center=(
            GRID_X + GRID_WIDTH // 2,
            GRID_Y + GRID_HEIGHT + 35
        )
    )

    screen.blit(info, info_rect)

    hint = small_font.render(
        "ЛКМ — встановити   ПКМ — видалити   ESC — меню",
        True,
        WHITE
    )

    screen.blit(
        hint,
        (30, HEIGHT - 45)
    )
    if ship_error != "":
        error_text = small_font.render(
            ship_error,
            True,
            (220, 60, 60)
        )

        screen.blit(
            error_text,
            (WIDTH - 1560, HEIGHT - 70)
        )
    draw_launch_button()


def draw_game():
    draw_space()
    draw_sun_event()
    draw_game_ship()
    draw_enemy_ship()
    draw_enemy_explosion()
    draw_comet_event()
    draw_stardust_event()
    draw_bullets()
    draw_meteors()
    draw_rocket_launcher_modules(in_game=True)
    draw_rocket_effects()

def draw_stardust_blindness():
    if stardust_fog_alpha <= 0:
        return
    current_time = pygame.time.get_ticks() / 1000
    covered = min(1.0, max(0.0, (current_time - stardust_fog_started_at) / 1.6))
    alpha = stardust_fog_alpha
    if stardust_fog_fade_started_at is not None:
        fade_start = max(stardust_fog_fade_started_at, stardust_fog_started_at + 1.6)
        fade_progress = min(1.0, max(0.0, (current_time - fade_start) / 1.2))
        alpha = round(alpha * (1 - fade_progress))
    if alpha > 0 and covered > 0:
        fog_height = int(HEIGHT * covered)
        edge_height = min(fog_height, max(50, int(HEIGHT * 0.12)))
        fog = stardust_fog_surface
        fog.fill((0, 0, 0, 0))
        solid_height = max(0, fog_height - edge_height)
        if solid_height:
            pygame.draw.rect(fog, (3, 7, 18, alpha), (0, 0, WIDTH, solid_height))
        for band in range(edge_height):
            edge_alpha = int(alpha * (1 - band / edge_height))
            pygame.draw.line(
                fog,
                (8, 15, 32, edge_alpha),
                (0, solid_height + band),
                (WIDTH, solid_height + band),
            )
        screen.blit(fog, (0, 0), (0, 0, WIDTH, fog_height))
    if stardust_blinded and stardust_key_index < len(stardust_key_sequence):
        prompt = title_font.render(
            f"НАТИСНИ КЛАВІШУ: {STARDUST_KEY_LABELS[stardust_key_sequence[stardust_key_index]]}",
            True,
            WHITE,
        )
        screen.blit(prompt, prompt.get_rect(midtop=(WIDTH // 2, 24)))

def handle_stardust_keypress(key):
    global stardust_blinded, stardust_key_index, stardust_fog_alpha
    global stardust_fog_fade_started_at
    if not stardust_blinded:
        return
    required_key = stardust_key_sequence[stardust_key_index]
    if key != required_key:
        return
    stardust_key_index += 1
    stardust_fog_alpha = round(235 * max(0, 1 - stardust_key_index * 0.1))
    if stardust_key_index >= len(stardust_key_sequence):
        stardust_blinded = False
        stardust_fog_fade_started_at = pygame.time.get_ticks() / 1000

def draw_game_over():
    screen.fill((10, 10, 15))
    title = title_font.render("КОРАБЕЛЬ ЗНИЩЕНО", True, (220, 60, 60))
    text = title_font.render("Ваш корабель більше не може продовжувати бій.", True, (220, 220, 220))
    button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 80, 300, 60)
    pygame.draw.rect(screen, (70, 70, 80), button)
    button_text = button_font.render("У МЕНЮ", True, (255, 255, 255))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 100))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 40))
    screen.blit(
        button_text,
        (
            button.centerx - button_text.get_width() // 2,
            button.centery - button_text.get_height() // 2
        )
    )

def draw_victory():
    screen.fill((8, 18, 28))
    title = title_font.render("ПЕРЕМОГА!", True, (255, 220, 105))
    text = button_font.render("Фінального боса знищено.", True, WHITE)
    button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 80, 300, 60)
    pygame.draw.rect(screen, BUTTON, button, border_radius=10)
    pygame.draw.rect(screen, WHITE, button, width=2, border_radius=10)
    button_text = button_font.render("У МЕНЮ", True, WHITE)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100)))
    screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 35)))
    screen.blit(button_text, button_text.get_rect(center=button.center))

def create_stars():
    stars = []
    for i in range(100):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.randint(1, 3)
        speed = random.randint(1, 3)
        stars.append([x, y, size, speed])
    return stars

def draw_space():
    screen.fill((5, 8, 18))

    for star in stars:
        x, y, size, speed = star

        pygame.draw.circle(
            screen,
            (180, 180, 200),
            (int(x), int(y)),
            size
        )

def update_stars():
    for star in stars:
        star[1] += star[3]
        if star[1] > HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, WIDTH)
def start_game():
    global ship_x, ship_y, enemy_ship, last_event_time, comet, comet_sparks, sun
    global ship_gravity_velocity_x, stardust_blinded, stardust_key_sequence, stardust_key_index
    global stardust_fog_alpha, stardust_fog_started_at, stardust_fog_fade_started_at
    global stardust_active, stardust_started_at
    ship_width = 15 * GAME_CELL_SIZE
    ship_height = 15 * GAME_CELL_SIZE
    ship_x = WIDTH // 2 - ship_width // 2
    ship_y = HEIGHT // 1.2 - ship_height // 2 - GAME_CELL_SIZE
    enemy_ship = None
    comet = None
    comet_sparks.clear()
    stardust_blinded = False
    stardust_active = False
    stardust_started_at = 0
    stardust_particles.clear()
    stardust_key_sequence = []
    stardust_key_index = 0
    stardust_fog_alpha = 0
    stardust_fog_started_at = 0
    stardust_fog_fade_started_at = None
    sun = None
    ship_gravity_velocity_x = 0
    explosion_particles.clear()
    enemy_explosion_particles.clear()
    bullets.clear()
    rocket_projectiles.clear()
    rocket_impacts.clear()
    meteors.clear()
    current_time = pygame.time.get_ticks() / 1000
    last_event_time = current_time
    spawn_meteor()
def draw_game_ship():
    for row in range(15):
        for col in range(15):
            module = ship_grid[row][col]
            if module is None:
                continue
            x = ship_x + col * GAME_CELL_SIZE
            y = ship_y + row * GAME_CELL_SIZE
            rect = pygame.Rect(
                x + 1,
                y + 1,
                GAME_CELL_SIZE - 2,
                GAME_CELL_SIZE - 2
            )
            if isinstance(module, Hull):
                color = (100, 100, 100)
            elif isinstance(module, Engine):
                color = (150, 90, 50)
            elif isinstance(module, Armor):
                color = (90, 90, 100)
            elif isinstance(module, Reactor):
                color = (40, 100, 220)
            elif isinstance(module, BrokenReactor):
                color = (160, 160, 190)
            elif isinstance(module, Cannon):
                color = (170, 60, 60)
            else:
                color = WHITE
            pygame.draw.rect(screen,color,rect)
def get_ship_mass():
    mass = 0
    for row in range(15):
        for col in range(15):
            module = ship_grid[row][col]
            if module is not None:
                mass += module.mass
    return mass
def get_ship_thrust():
    thrust = 0
    reactor_active1 = reactor_active()
    for row in range(15):
        for col in range(15):
            module = ship_grid[row][col]
            if isinstance(module, Engine):
                if reactor_active1:
                    thrust += module.thrust * 2
                else:
                    thrust += module.thrust
    return thrust
def get_ship_speed():
    mass = get_ship_mass()
    thrust = get_ship_thrust()
    if thrust <= 0:
        return 0.5
    speed = game_speed * (thrust / mass)
    if speed < 0.3:
        speed = 0.3
    if speed > 3:
        speed = 3
    return speed

def create_enemy_ship(is_elite=False):
    """Створює звичайний або посилений корабель із модулів конструктора."""
    regular_blueprints = [
        ("Розвідник", [
            "..H..",
            ".EHE.",
            "HC.RH",
            "..C..",
            ".....",
        ]),
        ("Штурмовик", [
            ".H.H.",
            "EAARE",
            "HCCCH",
            ".HHH.",
            "..H..",
        ]),
        ("Броньований", [
            ".HLH.",
            "EARAE",
            "HH.HH",
            "H.L.H",
            ".AHA.",
        ]),
        ("Гарматний", [
            "H.C.H",
            "EHRHE",
            "CCACC",
            ".A.A.",
            "..H..",
        ]),
    ]
    elite_blueprints = [
        ("Лінкор", [
            "....H....",
            "..AAAAA..",
            "EAH.RHAE.",
            "H.C.C.C.H",
            "HCCCHHCCC",
            "H.C.C.C.H",
            "EAH.RHAE.",
            "..AAAAA..",
            "....A....",
        ]),
        ("Крейсер", [
            "..HHHHH..",
            ".EAAHAAE.",
            "H.C.C.C.H",
            "HAACRCAAH",
            "H.C.C.C.H",
            ".EAAHAAE.",
            "..HHHHH..",
        ]),
        ("Гармата-носій", [
            "...HHH...",
            ".EAAHAAE.",
            "H.C.C.C.H",
            "HAACRCAAH",
            "HCCCCCCCH",
            "HAACCCAAH",
            "H.C.L.C.H",
            ".EAAHAAE.",
            "...HHH...",
        ]),
    ]
    module_types = {
        "H": Hull,
        "E": Engine,
        "A": Armor,
        "R": Reactor,
        "C": Cannon,
        "L": RocketLauncher,
    }
    blueprints = elite_blueprints if is_elite else regular_blueprints
    name, blueprint = random.choice(blueprints)
    layout = [
        [module_types[code]() if code in module_types else None for code in row]
        for row in blueprint
    ]
    ship_width = len(layout[0]) * GAME_CELL_SIZE
    x = max(0, min(WIDTH - ship_width, WIDTH // 2 - ship_width // 2))
    y = -len(layout) * GAME_CELL_SIZE
    return EnemyShip(name, layout, x, y, HEIGHT * 0.12 + GAME_CELL_SIZE, is_elite)

def create_final_boss():
    blueprint = [
        ".....EEE.....",
        "....LHEHL....",
        "...AEAAAEA...",
        "..EAAH.HAAE..",
        "...A.C.C.H...",
        "HAHCСRRRCCHAH",
        "A.C.C.C.C.C.A",
        "HAHCCCACCCHAH",
        "...H.CCC.A...",
        "..EAAH.HAAE..",
        "...AAAAAAA...",
        ".....HHH.....",
    ]
    module_types = {"H": Hull, "E": Engine, "A": Armor, "R": Reactor, "C": Cannon, "L": RocketLauncher}
    layout = [
        [module_types[code]() if code in module_types else None for code in row]
        for row in blueprint
    ]
    ship_width = len(layout[0]) * GAME_CELL_SIZE
    x = max(0, min(WIDTH - ship_width, WIDTH // 2 - ship_width // 2))
    y = -len(layout) * GAME_CELL_SIZE
    boss = EnemyShip(
        "ФІНАЛЬНИЙ БОС",
        layout,
        x,
        y,
        HEIGHT * 0.12,
        is_elite=True,
        is_final_boss=True,
    )
    for module in boss.alive_modules():
        module.barrier *= 2
    boss.initial_health = sum(module.barrier for module in boss.alive_modules())
    return boss

def spawn_comet():
    global comet, comet_sparks
    comet = Comet()
    comet_sparks = []

def spawn_stardust():
    global stardust_particles, stardust_active, stardust_started_at
    global stardust_blinded, stardust_key_sequence, stardust_key_index
    global stardust_fog_alpha, stardust_fog_fade_started_at
    stardust_particles = [StardustParticle() for _ in range(100)]
    stardust_active = True
    stardust_started_at = pygame.time.get_ticks() / 1000
    stardust_blinded = False
    stardust_key_sequence = []
    stardust_key_index = 0
    stardust_fog_alpha = 0
    stardust_fog_fade_started_at = None

def update_stardust_event():
    if not stardust_active:
        return
    for particle in stardust_particles:
        particle.x += particle.speed_x
        particle.y += particle.speed_y
        if particle.y > HEIGHT:
            particle.y = -particle.radius
            particle.x = random.randint(0, WIDTH)
        if particle.x < 0:
            particle.x = WIDTH
        elif particle.x > WIDTH:
            particle.x = 0

def update_stardust_effect(current_time):
    global stardust_active, stardust_blinded, stardust_key_sequence, stardust_key_index
    global stardust_fog_alpha, stardust_fog_started_at, stardust_fog_fade_started_at
    if not stardust_active:
        return

    update_stardust_event()
    if current_time - stardust_started_at >= STARDUST_DARKEN_DELAY and not stardust_key_sequence:
        stardust_blinded = True
        stardust_key_index = 0
        stardust_fog_alpha = 235
        stardust_fog_started_at = current_time
        stardust_fog_fade_started_at = None
        available_keys = tuple(STARDUST_KEY_LABELS)
        stardust_key_sequence = [
            random.choice(available_keys)
            for _ in range(STARDUST_KEYS_TO_CLEAR)
        ]

    if (stardust_key_sequence and not stardust_blinded and
            stardust_fog_fade_started_at is not None):
        fade_start = max(stardust_fog_fade_started_at, stardust_fog_started_at + 1.6)
        if current_time - fade_start >= 1.2:
            stardust_active = False
            stardust_particles.clear()
            stardust_key_sequence = []
            stardust_key_index = 0
            stardust_fog_alpha = 0
            stardust_fog_fade_started_at = None

def draw_stardust_event():
    if not stardust_active:
        return
    for particle in stardust_particles:
        pygame.draw.circle(
            screen,
            particle.color,
            (int(particle.x), int(particle.y)),
            particle.radius,
        )

def draw_comet_event():
    if comet is not None:
        x, y, radius = int(comet.x), int(comet.y), comet.radius
        # Яскравий хвіст і кілька шарів світіння навколо ядра комети.
        pygame.draw.line(screen, (105, 110, 155), (x - radius * 3, y), (x, y), 12)
        pygame.draw.line(screen, (185, 190, 225), (x - radius * 2, y), (x, y), 5)
        pygame.draw.circle(screen, (105, 115, 165), (x, y), radius + 12)
        pygame.draw.circle(screen, (235, 170, 95), (x, y), radius)
        pygame.draw.circle(screen, (255, 220, 145), (x + 5, y - 4), radius - 12)
        pygame.draw.circle(screen, (255, 250, 220), (x + 8, y - 7), radius // 2)
    for spark in comet_sparks:
        pygame.draw.circle(screen, (255, 170, 70), (int(spark.x), int(spark.y)), spark.radius + 2)
        pygame.draw.circle(screen, (255, 245, 175), (int(spark.x), int(spark.y)), spark.radius)

def draw_sun_event():
    if sun is None:
        return
    x, y, radius = int(sun.x), int(sun.y), sun.radius
    pygame.draw.circle(screen, (65, 29, 18), (x, y), radius + 130)
    pygame.draw.circle(screen, (120, 48, 20), (x, y), radius + 84)
    pygame.draw.circle(screen, (190, 78, 24), (x, y), radius + 44)
    pygame.draw.circle(screen, (245, 139, 42), (x, y), radius)
    pygame.draw.circle(screen, (255, 190, 76), (x - radius // 5, y - radius // 6), radius * 3 // 4)
    pygame.draw.circle(screen, (255, 226, 135), (x - radius // 4, y - radius // 4), radius // 2)

def spawn_sun():
    global sun, ship_gravity_velocity_x
    sun = Sun()
    ship_gravity_velocity_x = 0

def update_sun_event():
    global sun, ship_gravity_velocity_x, ship_x
    if current_event != EVENT_SUN_FLYBY or sun is None:
        return

    sun.y += sun.speed
    ship_center_x = ship_x + 15 * GAME_CELL_SIZE / 2
    ship_center_y = ship_y + 15 * GAME_CELL_SIZE / 2
    dx = sun.x - ship_center_x
    dy = sun.y - ship_center_y
    distance = math.hypot(dx, dy) or 1
    influence_radius = WIDTH * 0.7
    if distance < influence_radius:
        closeness = 1 - distance / influence_radius
        acceleration = 0.35 * closeness * closeness
        ship_gravity_velocity_x += (1 if dx > 0 else -1) * acceleration
        ship_gravity_velocity_x = max(-6, min(6, ship_gravity_velocity_x))

    ship_gravity_velocity_x *= 0.985
    ship_x += ship_gravity_velocity_x
    ship_width = 15 * GAME_CELL_SIZE
    ship_x = max(0, min(WIDTH - ship_width, ship_x))

    sun.damage_timer += clock.get_time() / 1000
    while sun.damage_timer >= 1:
        sun.damage_timer -= 1
        for row_index, row in enumerate(ship_grid):
            for col_index, module in enumerate(row):
                if module is None:
                    continue
                block = pygame.Rect(
                    ship_x + col_index * GAME_CELL_SIZE,
                    ship_y + row_index * GAME_CELL_SIZE,
                    GAME_CELL_SIZE,
                    GAME_CELL_SIZE,
                )
                closest_x = max(block.left, min(sun.x, block.right))
                closest_y = max(block.top, min(sun.y, block.bottom))
                if math.hypot(sun.x - closest_x, sun.y - closest_y) <= sun.radius + 80:
                    module.barrier -= 1

    for row_index, row in enumerate(ship_grid):
        for col_index, module in enumerate(row):
            if module is None:
                continue
            block = pygame.Rect(
                ship_x + col_index * GAME_CELL_SIZE,
                ship_y + row_index * GAME_CELL_SIZE,
                GAME_CELL_SIZE,
                GAME_CELL_SIZE,
            )
            closest_x = max(block.left, min(sun.x, block.right))
            closest_y = max(block.top, min(sun.y, block.bottom))
            if math.hypot(sun.x - closest_x, sun.y - closest_y) <= sun.radius:
                module.barrier -= 1_000_000

    if sun.y - sun.radius > HEIGHT:
        finish_event()

def update_comet_event():
    global comet
    if current_event != EVENT_COMET:
        return

    current_time = pygame.time.get_ticks() / 1000
    if comet is not None:
        comet.x += comet.speed
        if current_time - comet.last_spark_time >= 0.12:
            for _ in range(2):
                comet_sparks.append(CometSpark(comet.x, comet.y + random.uniform(-18, 18)))
            comet.last_spark_time = current_time
        if comet.x - comet.radius > WIDTH:
            comet = None

    for spark in comet_sparks[:]:
        spark.x += spark.velocity_x
        spark.y += spark.velocity_y
        spark.life -= 1 / 60

        hit = False
        for row_index, row in enumerate(ship_grid):
            for col_index, module in enumerate(row):
                if module is None:
                    continue
                rect = pygame.Rect(
                    ship_x + col_index * GAME_CELL_SIZE,
                    ship_y + row_index * GAME_CELL_SIZE,
                    GAME_CELL_SIZE,
                    GAME_CELL_SIZE,
                )
                if rect.collidepoint(spark.x, spark.y):
                    module.barrier -= 16
                    hit = True
                    break
            if hit:
                break
        if hit or spark.life <= 0 or spark.x < -10 or spark.x > WIDTH + 10 or spark.y < -10 or spark.y > HEIGHT + 10:
            comet_sparks.remove(spark)

    if comet is None and not comet_sparks:
        finish_event()

def get_enemy_ship_speed(enemy):
    mass = sum(
        module.mass
        for row in enemy.grid
        for module in row
        if module is not None
    )
    thrust = sum(
        module.thrust
        for row in enemy.grid
        for module in row
        if isinstance(module, Engine)
    )
    if any(isinstance(module, Reactor) for module in enemy.alive_modules()):
        thrust *= 2
    if mass <= 0 or thrust <= 0:
        return 0.5
    return max(0.3, min(3, game_speed * thrust / mass))

def draw_enemy_ship():
    if enemy_ship is None or enemy_ship.exploding:
        return
    label = small_font.render(enemy_ship.name, True, WHITE)
    screen.blit(label, label.get_rect(center=(int(enemy_ship.x + enemy_ship.width / 2), int(enemy_ship.y - 22))))
    for row_index, row in enumerate(enemy_ship.grid):
        for col_index, module in enumerate(row):
            if module is None:
                continue
            rect = pygame.Rect(
                int(enemy_ship.x + col_index * GAME_CELL_SIZE + 1),
                int(enemy_ship.y + row_index * GAME_CELL_SIZE + 1),
                GAME_CELL_SIZE - 2,
                GAME_CELL_SIZE - 2,
            )
            if isinstance(module, Hull):
                color = (120, 125, 140)
            elif isinstance(module, Engine):
                color = (220, 120, 55)
            elif isinstance(module, Armor):
                color = (90, 105, 125)
            elif isinstance(module, Reactor):
                color = (180, 65, 200)
            elif isinstance(module, Cannon):
                color = (210, 65, 65)
            elif isinstance(module, RocketLauncher):
                color = (115, 145, 65)
            else:
                color = WHITE
            pygame.draw.rect(screen, color, rect)
            if isinstance(module, RocketLauncher):
                tube_width = max(5, GAME_CELL_SIZE // 6)
                tube = pygame.Rect(
                    rect.centerx - tube_width // 2,
                    rect.top + 2,
                    tube_width,
                    rect.height // 2,
                )
                pygame.draw.rect(screen, (220, 205, 150), tube, border_radius=2)

    remaining_health = sum(
        module.barrier
        for row in enemy_ship.grid
        for module in row
        if module is not None
    )
    bar_rect = pygame.Rect(int(enemy_ship.x), int(enemy_ship.y - 12), enemy_ship.width, 7)
    pygame.draw.rect(screen, (80, 35, 40), bar_rect)
    health_width = int(enemy_ship.width * max(0, remaining_health) / enemy_ship.initial_health)
    if health_width > 0:
        pygame.draw.rect(screen, (220, 65, 65), (bar_rect.x, bar_rect.y, health_width, bar_rect.height))

def start_enemy_ship_explosion(enemy):
    global enemy_explosion_particles
    enemy.exploding = True
    enemy.explosion_end_time = pygame.time.get_ticks() / 1000 + 0.9
    color_by_module = (
        (Hull, (165, 175, 190)),
        (Engine, (225, 135, 75)),
        (Armor, (130, 145, 165)),
        (Reactor, (205, 105, 215)),
        (Cannon, (225, 100, 90)),
        (RocketLauncher, (155, 175, 100)),
    )
    for row_index, row in enumerate(enemy.grid):
        for col_index, module in enumerate(row):
            if module is None:
                continue
            color = next((shade for module_type, shade in color_by_module if isinstance(module, module_type)), (210, 210, 220))
            x = enemy.x + col_index * GAME_CELL_SIZE + GAME_CELL_SIZE / 2
            y = enemy.y + row_index * GAME_CELL_SIZE + GAME_CELL_SIZE / 2
            for _ in range(2):
                enemy_explosion_particles.append(EnemyExplosionParticle(x, y, color))

    center_x = enemy.x + enemy.width / 2
    center_y = enemy.y + enemy.height / 2
    for index in range(12):
        color = (255, 185, 95) if index % 2 else (255, 225, 160)
        enemy_explosion_particles.append(EnemyExplosionParticle(center_x, center_y, color))

def update_enemy_explosion():
    for particle in enemy_explosion_particles[:]:
        particle.x += particle.velocity_x
        particle.y += particle.velocity_y
        particle.life -= 1 / 60
        if particle.life <= 0:
            enemy_explosion_particles.remove(particle)

def draw_enemy_explosion():
    for particle in enemy_explosion_particles:
        intensity = max(0, particle.life / particle.max_life)
        color = tuple(int(channel * intensity) for channel in particle.color)
        pygame.draw.circle(
            screen,
            color,
            (int(particle.x), int(particle.y)),
            max(1, int(particle.size * intensity)),
        )

def shoot_from_enemy(enemy):
    player_x = ship_x + 15 * GAME_CELL_SIZE / 2
    player_y = ship_y + 15 * GAME_CELL_SIZE / 2
    current_time = pygame.time.get_ticks() / 1000
    for row_index, row in enumerate(enemy.grid):
        for col_index, module in enumerate(row):
            if not isinstance(module, Cannon):
                continue
            key = (row_index, col_index)
            if current_time - enemy.last_shot.get(key, 0) < module.coldown:
                continue
            x = enemy.x + col_index * GAME_CELL_SIZE + GAME_CELL_SIZE / 2
            y = enemy.y + row_index * GAME_CELL_SIZE + GAME_CELL_SIZE / 2
            dx, dy = player_x - x, player_y - y
            angle = math.atan2(dy, dx) + math.radians(random.uniform(-7, 7))
            bullet_speed = 7
            enemy_damage = module.damage + 2 + int(enemy.is_elite)
            if enemy.is_final_boss:
                enemy_damage += 3
            bullets.append(Bullet(
                x, y, enemy_damage,
                math.cos(angle) * bullet_speed,
                math.sin(angle) * bullet_speed,
                owner="enemy",
            ))
            enemy.last_shot[key] = current_time
    shoot_enemy_rockets(enemy)

def update_enemy_ship():
    if enemy_ship is None:
        return
    if enemy_ship.exploding:
        if pygame.time.get_ticks() / 1000 >= enemy_ship.explosion_end_time:
            finish_event()
        return
    enemy_ship.speed = get_enemy_ship_speed(enemy_ship)
    if enemy_ship.y < enemy_ship.target_y:
        enemy_ship.y = min(enemy_ship.target_y, enemy_ship.y + 2)
    else:
        enemy_center = enemy_ship.x + enemy_ship.width / 2
        player_center = ship_x + 15 * GAME_CELL_SIZE / 2
        if abs(player_center - enemy_center) > enemy_ship.speed:
            enemy_ship.x += enemy_ship.speed if player_center > enemy_center else -enemy_ship.speed
        enemy_ship.x = max(0, min(WIDTH - enemy_ship.width, enemy_ship.x))
        shoot_from_enemy(enemy_ship)

    if (enemy_ship.reactor_destroyed or
            enemy_ship.destroyed_blocks > enemy_ship.initial_block_count / 2):
        print("Ворожий корабель знищено")
        start_enemy_ship_explosion(enemy_ship)

def move_ship(keys):
    global ship_x
    speed = get_ship_speed()
    inverted = pygame.time.get_ticks() / 1000 < turbulence_end_time
    move_left = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) if inverted else (keys[pygame.K_LEFT] or keys[pygame.K_a])
    move_right = (keys[pygame.K_LEFT] or keys[pygame.K_a]) if inverted else (keys[pygame.K_RIGHT] or keys[pygame.K_d])
    if move_left:
        ship_x -= speed
    if move_right:
        ship_x += speed
    ship_width = 15 * GAME_CELL_SIZE
    if ship_x < 0:
        ship_x = 0
    if ship_x + ship_width > WIDTH:
        ship_x = WIDTH - ship_width

def start_ship_explosion():
    global current_screen, explosion_particles, explosion_start_time, explosion_center
    if current_screen != GAME:
        return
    explosion_particles = []
    for row_index, row in enumerate(ship_grid):
        for col_index, module in enumerate(row):
            if module is None:
                continue
            if isinstance(module, (Reactor, BrokenReactor)):
                color = (90, 160, 255)
            elif isinstance(module, Cannon):
                color = (255, 90, 75)
            elif isinstance(module, Engine):
                color = (255, 155, 65)
            elif isinstance(module, Armor):
                color = (155, 170, 190)
            else:
                color = (205, 210, 220)
            x = ship_x + col_index * GAME_CELL_SIZE + GAME_CELL_SIZE / 2
            y = ship_y + row_index * GAME_CELL_SIZE + GAME_CELL_SIZE / 2
            for _ in range(random.randint(4, 7)):
                explosion_particles.append(ExplosionParticle(x, y, color))

    explosion_center = (
        int(ship_x + 15 * GAME_CELL_SIZE / 2),
        int(ship_y + 15 * GAME_CELL_SIZE / 2),
    )
    explosion_start_time = pygame.time.get_ticks() / 1000
    current_screen = EXPLOSION
    bullets.clear()

def update_ship_explosion():
    global current_screen
    delta_time = min(clock.get_time() / 1000, 0.05)
    for particle in explosion_particles:
        particle.x += particle.velocity_x
        particle.y += particle.velocity_y
        particle.velocity_y += 0.12
        particle.life -= delta_time
    explosion_particles[:] = [particle for particle in explosion_particles if particle.life > 0]

    elapsed = pygame.time.get_ticks() / 1000 - explosion_start_time
    if elapsed >= EXPLOSION_DURATION:
        current_screen = GAME_OVER

def draw_ship_explosion():
    draw_space()
    elapsed = pygame.time.get_ticks() / 1000 - explosion_start_time

    if elapsed < 0.35:
        flash_radius = int(130 * (1 - elapsed / 0.35))
        pygame.draw.circle(screen, (255, 190, 95), explosion_center, flash_radius)
        pygame.draw.circle(screen, (255, 245, 205), explosion_center, flash_radius // 2)

    ring_radius = int(elapsed * max(WIDTH, HEIGHT) * 0.65)
    if elapsed < 1.1:
        pygame.draw.circle(screen, (255, 145, 70), explosion_center, ring_radius, width=5)

    for particle in explosion_particles:
        intensity = max(0.15, particle.life / particle.max_life)
        color = tuple(int(channel * intensity) for channel in particle.color)
        pygame.draw.circle(
            screen,
            color,
            (int(particle.x), int(particle.y)),
            max(1, int(particle.size * intensity)),
        )

def check_destroyed_modules():
    global current_screen
    for row in range(15):
        for col in range(15):
            module = ship_grid[row][col]
            if module is None:
                continue
            if isinstance(module, BrokenReactor):
                if module.barrier <= 0:
                    start_ship_explosion()
                    print("GAME OVER: зламаний реактор знищено")
                    return
            elif isinstance(module, Reactor):
                if module.barrier <= 0:
                    ship_grid[row][col] = BrokenReactor()
                    print("Реактор зламано!")
            elif module.barrier <= 0:
                ship_grid[row][col] = None
    block_count = get_module_count()
    if block_count <= 5:
        start_ship_explosion()
        print("GAME OVER: залишилося мало блоків")
def clear_ship():
    for row in range(15):
        for col in range(15):
            ship_grid[row][col] = None

def start_event(event):
    global current_event, event_start_time, final_boss_meteor_timer, turbulence_end_time
    current_event = event
    event_start_time = pygame.time.get_ticks() / 1000
    if event == EVENT_FINAL_BOSS:
        final_boss_meteor_timer = event_start_time
    elif event == EVENT_TURBULENCE:
        turbulence_end_time = event_start_time + TURBULENCE_EFFECT_DURATION

def finish_event():
    """Завершує активний івент і запускає відлік паузи до наступного."""
    global current_event, last_event_time, enemy_ship, comet, sun
    global ship_gravity_velocity_x
    global completed_events, EVENT_STAGE, MAX_MODULES, current_screen
    global stardust_blinded, stardust_fog_alpha, stardust_fog_fade_started_at
    if current_event == EVENT_NONE:
        return
    finished_event = current_event
    if finished_event in (EVENT_ENEMY_SHIP, EVENT_ELITE_ENEMY_SHIP, EVENT_FINAL_BOSS):
        enemy_ship = None
        bullets[:] = [bullet for bullet in bullets if bullet.owner != "enemy"]
        rocket_projectiles.clear()
        rocket_impacts.clear()
    elif finished_event == EVENT_COMET:
        comet = None
        comet_sparks.clear()
    elif finished_event == EVENT_SUN_FLYBY:
        sun = None
        ship_gravity_velocity_x = 0
    print("Івент завершився:", finished_event)
    current_event = EVENT_NONE
    last_event_time = pygame.time.get_ticks() / 1000
    if finished_event == EVENT_FINAL_BOSS:
        current_screen = VICTORY
        print("Фінального боса переможено!")
        return
    if EVENT_STAGE in EVENTS_BEFORE_CONSTRUCTOR:
        completed_events += 1
        stage_event_limit = EVENTS_BEFORE_CONSTRUCTOR[EVENT_STAGE]
        print(f"Завершено івентів етапу {EVENT_STAGE}: {completed_events}/{stage_event_limit}")
        if completed_events >= stage_event_limit:
            finished_stage = EVENT_STAGE
            EVENT_STAGE += 1
            completed_events = 0
            if finished_stage == 3:
                start_event(EVENT_FINAL_BOSS)
                enemy_ship = create_final_boss()
                print("Почався фінальний бій:", enemy_ship.name)
            else:
                MAX_MODULES += 5
                current_screen = CONSTRUCTOR
                print(f"Етап {finished_stage} завершено. Ліміт збільшено до", MAX_MODULES, "блоків")

def update_event_meteors():
    global meteor_spawn_timer
    if current_event != EVENT_METEOR_SHOWER:
        return
    current_time = pygame.time.get_ticks() / 1000
    if current_time - meteor_spawn_timer >= 0.25:
        spawn_meteor()
        meteor_spawn_timer = current_time

def start_random_event():
    available_events = EVENT_LISTS.get(EVENT_STAGE, [])
    if not available_events:
        return
    event = random.choice(available_events)
    start_event(event)
    if event in (EVENT_ENEMY_SHIP, EVENT_ELITE_ENEMY_SHIP):
        global enemy_ship
        enemy_ship = create_enemy_ship(is_elite=event == EVENT_ELITE_ENEMY_SHIP)
        print("Атакує ворожий корабель:", enemy_ship.name)
    elif event == EVENT_COMET:
        spawn_comet()
        print("Почався івент: велика комета")
    elif event == EVENT_SUN_FLYBY:
        spawn_sun()
        print("Почався івент: проліт біля Сонця")
    elif event == EVENT_STARDUST:
        spawn_stardust()
        print("Почався івент: зоряний пил")
    elif event == EVENT_TURBULENCE:
        print("Почався івент: турбулентність")
    else:
        print("Почався івент:", event)

def update_event():
    global final_boss_meteor_timer
    current_time = pygame.time.get_ticks() / 1000
    update_stardust_effect(current_time)

    if current_event == EVENT_NONE:
        if EVENT_LISTS.get(EVENT_STAGE) and current_time - last_event_time >= EVENT_INTERVAL:
            start_random_event()
    elif current_event == EVENT_METEOR_SHOWER:
        # Метеоритний дощ має визначену тривалість.
        if current_time - event_start_time >= EVENT_DURATION:
            finish_event()
    elif current_event == EVENT_STARDUST:
        if current_time - event_start_time >= STARDUST_EVENT_DURATION:
            finish_event()
    elif current_event == EVENT_TURBULENCE:
        if current_time - event_start_time >= TURBULENCE_EVENT_DURATION:
            finish_event()
    elif current_event == EVENT_FINAL_BOSS:
        if current_time - final_boss_meteor_timer >= FINAL_BOSS_METEOR_INTERVAL:
            spawn_meteor()
            final_boss_meteor_timer = current_time
    # Інші івенти завершуються власною умовою. Наприклад, івент із ворогом
    # має викликати finish_event() лише після знищення ворога.

stars = create_stars()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if current_screen == CONSTRUCTOR:
                    current_screen = MENU
                else:
                    running = False

            handle_stardust_keypress(event.key)

            if event.key == pygame.K_RETURN:
                selected_module = None
                selected_block = None

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if current_screen in (GAME_OVER, VICTORY):
                    menu_button = pygame.Rect(
                        WIDTH // 2 - 150,
                        HEIGHT // 2 + 80,
                        300,
                        60,
                    )
                    if menu_button.collidepoint(event.pos):
                        if current_screen == VICTORY or EVENT_STAGE > 3:
                            EVENT_STAGE = 1
                            completed_events = 0
                        clear_ship()
                        current_screen = MENU
                        current_event = EVENT_NONE
                        print("Повернення в меню")

                elif current_screen == MENU:
                    construct_button, exit_button = draw_menu()

                    if construct_button.collidepoint(event.pos):
                        current_screen = CONSTRUCTOR

                    elif exit_button.collidepoint(event.pos):
                        running = False

                elif current_screen == CONSTRUCTOR:
                    hull_button = pygame.Rect(
                        PANEL_X + 30,
                        MODULE_PANEL_Y + 80,
                        PANEL_WIDTH - 60,
                        60
                    )

                    engine_button = pygame.Rect(
                        PANEL_X + 30,
                        MODULE_PANEL_Y + 150,
                        PANEL_WIDTH - 60,
                        60
                    )

                    armor_button = pygame.Rect(
                        PANEL_X + 30,
                        MODULE_PANEL_Y + 220,
                        PANEL_WIDTH - 60,
                        60
                    )

                    reactor_button = pygame.Rect(
                        PANEL_X + 30,
                        MODULE_PANEL_Y + 290,
                        PANEL_WIDTH - 60,
                        60
                    )

                    cannon_button = pygame.Rect(
                        PANEL_X + 30,
                        MODULE_PANEL_Y + 360,
                        PANEL_WIDTH - 60,
                        60
                    )

                    rocket_launcher_button = pygame.Rect(
                        PANEL_X + 30,
                        MODULE_PANEL_Y + 430,
                        PANEL_WIDTH - 60,
                        60
                    )

                    launch_button = pygame.Rect(
                        WIDTH - 750,
                        HEIGHT - 65,
                        270,
                        55
                    )

                    if hull_button.collidepoint(event.pos):
                        selected_module = hull_module
                        selected_block = None

                    elif engine_button.collidepoint(event.pos):
                        selected_module = engine_module
                        selected_block = None

                    elif armor_button.collidepoint(event.pos):
                        selected_module = armor_module
                        selected_block = None

                    elif reactor_button.collidepoint(event.pos):
                        selected_module = reactor_module
                        selected_block = None

                    elif cannon_button.collidepoint(event.pos):
                        selected_module = cannon_module
                        selected_block = None

                    elif rocket_launcher_button.collidepoint(event.pos):
                        selected_module = rocket_launcher_module
                        selected_block = None

                    elif launch_button.collidepoint(event.pos):
                        valid, error = validate_ship()

                        if valid:
                            start_game()
                            current_screen = GAME
                            selected_module = None
                            selected_block = None
                            ship_error = ""
                        else:
                            ship_error = error

                    else:
                        cell = get_grid_cell(event.pos)

                        if cell is not None:
                            row, col = cell

                            if selected_module is not None:
                                if isinstance(selected_module, Reactor) and has_reactor():
                                    pass

                                elif ship_grid[row][col] is None and get_module_count() >= MAX_MODULES:
                                    pass

                                else:
                                    ship_grid[row][col] = type(selected_module)()
                                    selected_block = None

                            else:
                                selected_block = ship_grid[row][col]
                elif current_screen == GAME:
                    shoot()
                    shoot_rockets()

            elif event.button == 3:
                if current_screen == CONSTRUCTOR:
                    cell = get_grid_cell(event.pos)

                    if cell is not None:
                        row, col = cell
                        if isinstance(ship_grid[row][col], BrokenReactor):
                            pass
                        else:
                            ship_grid[row][col] = None
                        selected_block = None
    keys = pygame.key.get_pressed()
    if current_screen == GAME:
        update_stars()
        move_ship(keys)

        update_event()
        update_event_meteors()
        if current_event in (EVENT_ENEMY_SHIP, EVENT_ELITE_ENEMY_SHIP, EVENT_FINAL_BOSS):
            shoot()

        update_bullets()
        update_rockets()
        update_enemy_ship()
        update_enemy_explosion()
        update_comet_event()
        update_sun_event()
        update_meteors()
        if current_screen == GAME:
            check_destroyed_modules()
    elif current_screen == EXPLOSION:
        update_stars()
        update_ship_explosion()

    if current_screen == MENU:
        draw_menu()

    elif current_screen == CONSTRUCTOR:
        draw_constructor()

    elif current_screen == GAME:
        current_time = pygame.time.get_ticks() / 1000
        if current_time < turbulence_end_time:
            display_screen = screen
            screen = gameplay_surface
            draw_game()
            draw_stardust_blindness()
            screen = display_screen
            screen.fill((5, 8, 18))
            shake_offset = round(math.sin(current_time * 17) * TURBULENCE_SHAKE_AMPLITUDE)
            screen.blit(gameplay_surface, (shake_offset, 0))
        else:
            draw_game()
            draw_stardust_blindness()

    elif current_screen == EXPLOSION:
        draw_ship_explosion()

    elif current_screen == GAME_OVER:
        draw_game_over()

    elif current_screen == VICTORY:
        draw_victory()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
