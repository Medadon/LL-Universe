import pygame
import os
import random
import math
from client.main import GameMenu

pygame.init()

# Window
W, H = 1280, 900
Screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("LL Universe!")

main_menu = GameMenu(Screen)
game_state = "menu"

clock = pygame.time.Clock()
font = pygame.font.SysFont("Times New Roman", 30)
small_font = pygame.font.SysFont("Arial", 20)

# Assets Paths
assets_path = os.path.join(os.path.dirname(__file__), "Assets")
sprites_path = os.path.join(assets_path, "Sprites")


def load_sprite(name, size=None):
    path = os.path.join(sprites_path, name)

    if not os.path.exists(path):
        raise FileNotFoundError(f"Sprite not found: {path}")

    sprite = pygame.image.load(path).convert_alpha()

    if size:
        sprite = pygame.transform.smoothscale(sprite, size)

    return sprite


# Player Ships
ship_data = {
    "VovaShip": {
        "hp": 180, "speed": 5, "damage": 35,
        "fire_rate": 2000, "width": 70, "attack": "cone"
    },
    "DanShip": {
        "hp": 300, "speed": 2.5, "damage": 4,
        "fire_rate": 80, "width": 100, "attack": "normal"
    },
    "PlatShip": {
        "hp": 65, "speed": 8, "damage": 50,
        "fire_rate": 0, "width": 60, "attack": "beam"
    },
    "ArtShip": {
        "hp": 110, "speed": 5, "damage": 10,
        "fire_rate": 250, "width": 70, "attack": "normal"
    },
    "ZahShip": {
        "hp": 130, "speed": 5, "damage": 15,
        "fire_rate": 250, "width": 70, "attack": "laser"
    }
}


# Ship Sprites
ship_images = {}

for ship_name, data in ship_data.items():
    original_sprite = load_sprite(ship_name + ".png")

    width = data["width"]
    height = int(
        original_sprite.get_height() *
        (width / original_sprite.get_width())
    )

    ship_images[ship_name] = pygame.transform.smoothscale(
        original_sprite, (width, height)
    )


# Bullet Sprite
bullet_sprite = load_sprite("Bullet.png", (12, 25))
bullet_width = 12
bullet_height = 25
bullet_speed = 16
base_bullet_range = 550

# Special Attack Sprites
punch_image = load_sprite("Punch.png")
beam_image = load_sprite("Beam.png")

# Enemy Sprites
enemy_width = 50
enemy_images = {}

for enemy_name, enemy_size in {
    "Enemy1": 50,
    "Enemy2": 50,
    "Enemy3": 60,
    "MiniBoss": 95,
    "GuzaBoss": 160
}.items():

    sprite = load_sprite(enemy_name + ".png")
    sprite_height = int(
        sprite.get_height() * (enemy_size / sprite.get_width())
    )

    enemy_images[enemy_name] = pygame.transform.smoothscale(
        sprite, (enemy_size, sprite_height)
    )

enemy_image = enemy_images["Enemy1"]
enemy_height = enemy_image.get_height()

# Black Hole
black_hole_width = 640
black_hole_height = 450

black_hole_image = load_sprite(
    "BlackHole.png",
    (black_hole_width, black_hole_height)
)

warning_image = load_sprite("Warning.Png", (100, 100))

# Enemy Bullet
enemy_bullet_image = load_sprite("bullet_red.png", (20, 30))
enemy_bullet_width = 20
enemy_bullet_height = 30

# Bonus Sprites
bonus_types = [
    "Bomb", "Boost", "Heal", "Slow",
    "Mystery", "Shield", "Magnet", "DamageBoost"
]

ship_bonus_types = {
    "VovaShip": ["BoostPunch", "PunchRange"],
    "DanShip": ["AttackSpeed"],
    "PlatShip": ["BeamBoost"],
    "ArtShip": ["AtributeBoost"],
    "ZahShip": ["LaserBoost"]
}

all_bonus_types = bonus_types + [
    bonus_type
    for ship_bonuses in ship_bonus_types.values()
    for bonus_type in ship_bonuses
]

bonus_images = {
    bonus_type: load_sprite(bonus_type + ".png", (50, 50))
    for bonus_type in all_bonus_types
}

bonus_width = 50
bonus_height = 50

# Backgrounds
background_sprite_paths = [
    os.path.join(assets_path, "Backgrounds", "background.jpg"),
    os.path.join(assets_path, "Backgrounds", "background2.jpg"),
    os.path.join(assets_path, "Backgrounds", "background3.jpg")
]

background_images = []

for path in background_sprite_paths:

    if not os.path.exists(path):
        raise FileNotFoundError(f"Background file not found: {path}")

    background_sprite = pygame.image.load(path).convert()

    background_images.append(
        pygame.transform.scale(background_sprite, (W, H))
    )


# Player Settings
player_ship = None
player_image = None

player_width = 70
player_height = 70

x = 100
y = 650

player_speed = 5
max_hp = 110
hp = max_hp

# Player Bullets
bullets = []
shoot_cooldown = 250
last_shot_time = 0

# ZahShip Laser
laser_range = 900
laser_width = 5
laser_color = (80, 220, 255)
laser_damage = 15
laser_cooldown = 250
last_laser_time = 0
laser_active = False
laser_start = (0, 0)
laser_end = (0, 0)
laser_visual_duration = 100

# VovaShip Attack
cone_active = False
cone_start_time = 0
cone_duration = 250
cone_cooldown = 2000
last_cone_time = 0

cone_range = 250
cone_angle = 45
cone_visual_width = 360
cone_visual_height = 300
cone_hit_ids = set()

# PlatShip Beam
beam_charging = False
beam_charge_start = 0
beam_active = False
beam_start_time = 0
beam_duration = 1000
beam_max_charge = 3000
beam_width = 100
beam_damage = 50
beam_hit_timers = {}

# ArtShip
stolen_attribute = None
stolen_value = 0

art_stolen_base_caps = {
    "hp": 80,
    "speed": 3,
    "damage": 25,
    "fire_rate": 125,
    "range": 150
}
art_stolen_caps = dict(art_stolen_base_caps)
art_boss_cap_increase = {
    "hp": 10,
    "speed": 0.5,
    "damage": 3,
    "fire_rate": 15,
    "range": 20
}

stolen_stats = {
    "hp": 0,
    "speed": 0,
    "damage": 0,
    "fire_rate": 0,
    "range": 0
}

# Enemy Settings
enemies = []
enemy_speed = 2
enemy_direction = 1

enemy_rows = 3
enemy_columns = 10
enemy_spacing_x = 85
enemy_spacing_y = 75

enemy_shoot_delay = 900
last_enemy_shot_time = 0
enemy_bullets = []
enemy_bullet_speed = 6

# Wave Settings
wave = 1
wave_state = "active"
wave_break_start = 0
wave_break_duration = 3000
wave_message_duration = 1200
next_boss_wave = random.randint(5, 10)
boss_spawned_this_wave = False

# GuzaBoss Black Hole
black_hole_active = False
black_hole_warning = False
black_hole_x = 0
black_hole_y = 470
black_hole_start = 0
black_hole_warning_start = 0
black_hole_duration = 6000
black_hole_damage_timer = 0
black_hole_pull = 4.0
black_hole_next_attack = 0
boss_last_hp_phase = 0

# Score
score = 0
game_over = False
score_submitted = False

# Health Settings
damage_flash_start = 0
damage_flash_duration = 200

# Bonus Settings
bonuses = []
bonus_speed = 3
bonus_drop_base_chance = 0.04
bonus_drop_chance = bonus_drop_base_chance
bonus_drop_boss_increase = 0.03
bonus_drop_max_chance = 0.25
bonus_max_on_screen = 3

active_bonus = ""
double_shot_duration = 10000
double_shot_start_time = 0

bonus_durations = {
    "Boost": 10000,
    "Slow": 7000,
    "DamageBoost": 10000,
    "Shield": 5000,
    "Magnet": 10000,
    "BoostPunch": 8000,
    "PunchRange": 8000,
    "AttackSpeed": 8000,
    "BeamBoost": 8000,
    "AtributeBoost": 8000,
    "LaserBoost": 8000
}

active_effects = {
    effect: 0 for effect in bonus_durations
}

shield_active = False

# Invincibility
invincible = False
invincibility_duration = 2000
invincibility_start_time = 0

# QTE
qte_active = False
qte_sequence = []
qte_index = 0
qte_start_time = 0
qte_duration = 4000
qte_message = ""
pending_bonus = ""

qte_keys = [
    pygame.K_w,
    pygame.K_a,
    pygame.K_s,
    pygame.K_d
]

qte_key_names = {
    pygame.K_w: "W",
    pygame.K_a: "A",
    pygame.K_s: "S",
    pygame.K_d: "D"
}


# Spawn Enemies
def add_enemy(enemy_type, target_x, target_y):

    stats = {
        "Enemy1": {"hp": 15, "speed": 2.2, "damage": 12, "size": 50},
        "Enemy2": {"hp": 22, "speed": 3.8, "damage": 18, "size": 50},
        "Enemy3": {"hp": 50, "speed": 1.7, "damage": 30, "size": 60},
        "MiniBoss": {"hp": 350, "speed": 2.2, "damage": 36, "size": 95},
        "GuzaBoss": {"hp": 2500, "speed": 1.1, "damage": 60, "size": 160}
    }

    data = stats[enemy_type]
    image = enemy_images[enemy_type]

    wave_level = max(0, wave - 1)

    hp_multiplier = 1 + wave_level * 0.18
    damage_multiplier = 1 + wave_level * 0.10
    speed_multiplier = 1 + wave_level * 0.045

    enemies.append({
        "type": enemy_type,
        "image": image,
        "width": image.get_width(),
        "height": image.get_height(),
        "x": target_x,
        "y": -image.get_height() - random.randint(30, 180),
        "target_x": target_x,
        "target_y": target_y,
        "hp": int(data["hp"] * hp_multiplier),
        "max_hp": int(data["hp"] * hp_multiplier),
        "speed": data["speed"] * speed_multiplier,
        "damage": int(data["damage"] * damage_multiplier),
        "entering": True
    })


def spawn_enemies():
    global enemies, enemy_direction, boss_spawned_this_wave
    global black_hole_active, black_hole_warning, boss_last_hp_phase

    enemies = []
    enemy_direction = 1
    boss_spawned_this_wave = False

    black_hole_active = False
    black_hole_warning = False
    boss_last_hp_phase = 0

    if wave >= next_boss_wave:

        add_enemy("GuzaBoss", W // 2 - 80, 80)
        boss_spawned_this_wave = True

        for column in range(4):
            add_enemy("Enemy1", 180 + column * 210, 260)

        return

    if wave % 3 == 0:
        add_enemy("MiniBoss", W // 2 - 47, 70)

    start_y = 70

    formation_width = (enemy_columns - 1) * enemy_spacing_x + 60
    start_x = max(30, (W - formation_width) // 2)

    for row in range(enemy_rows):
        for column in range(enemy_columns):

            enemy_type = random.choices(
                ["Enemy1", "Enemy2", "Enemy3"],
                weights=[55, 30, 15],
                k=1
            )[0]

            target_x = start_x + column * 85
            target_y = start_y + row * 75

            add_enemy(enemy_type, target_x, target_y)


# Reset Player
def reset_player():
    global x, y, hp, max_hp, player_speed
    global player_ship, player_image, player_width, player_height
    global bullets, enemy_bullets, bonuses
    global score, game_over, enemy_speed, enemy_direction
    global last_shot_time, last_enemy_shot_time
    global cone_active, cone_start_time, last_cone_time
    global beam_charging, beam_charge_start
    global beam_active, beam_start_time, beam_hit_timers
    global stolen_attribute, stolen_value, stolen_stats, art_stolen_caps
    global active_bonus, shield_active, active_effects
    global invincible, invincibility_start_time
    global qte_active, pending_bonus, qte_message
    global wave, wave_state, wave_break_start, next_boss_wave
    global black_hole_active, black_hole_warning
    global bonus_drop_chance
    global black_hole_next_attack, last_laser_time, laser_active

    bonus_drop_chance = bonus_drop_base_chance

    wave = 1
    wave_state = "active"
    wave_break_start = 0
    next_boss_wave = random.randint(5, 10)

    black_hole_active = False
    black_hole_warning = False
    black_hole_next_attack = 0

    player_ship = main_menu.get_selected_ship()

    data = ship_data[player_ship]

    max_hp = data["hp"]
    hp = max_hp
    player_speed = data["speed"]

    player_image = ship_images[player_ship]

    player_width = player_image.get_width()
    player_height = player_image.get_height()

    x = (W - player_width) // 2
    y = H - player_height - 40

    bullets = []
    enemy_bullets = []
    bonuses = []

    score = 0
    game_over = False

    enemy_speed = 2
    enemy_direction = 1

    last_shot_time = 0
    last_enemy_shot_time = pygame.time.get_ticks()

    cone_active = False
    cone_start_time = 0
    last_cone_time = 0
    cone_hit_ids.clear()

    beam_charging = False
    beam_charge_start = 0
    beam_active = False
    beam_start_time = 0
    beam_hit_timers = {}

    stolen_attribute = None
    stolen_value = 0

    art_stolen_caps = dict(art_stolen_base_caps)

    stolen_stats = {
        "hp": 0,
        "speed": 0,
        "damage": 0,
        "fire_rate": 0,
        "range": 0
    }

    active_bonus = ""
    active_effects = {effect: 0 for effect in bonus_durations}
    shield_active = False

    invincible = False
    invincibility_start_time = 0

    qte_active = False
    pending_bonus = ""
    qte_message = ""

    last_laser_time = 0
    laser_active = False

    spawn_enemies()


# Player Damage
def take_damage(amount):
    global hp, game_over
    global invincible, invincibility_start_time, invincibility_duration
    global shield_active, damage_flash_start

    if invincible or game_over:
        return

    if shield_active:
        return

    hp -= amount
    damage_flash_start = pygame.time.get_ticks()

    if hp <= 0:
        hp = 0
        game_over = True
    else:
        invincible = True
        invincibility_start_time = pygame.time.get_ticks()
        invincibility_duration = 2000


def grant_invincibility(duration=1800):
    global invincible, invincibility_start_time, invincibility_duration

    invincible = True
    invincibility_start_time = pygame.time.get_ticks()
    invincibility_duration = duration


# Start QTE
def start_qte(bonus_type):
    global qte_active, qte_sequence, qte_index
    global qte_start_time, qte_duration, qte_message, pending_bonus

    qte_active = True
    qte_length = random.randint(3, 6)
    qte_sequence = random.choices(qte_keys, k=qte_length)
    qte_index = 0
    qte_start_time = pygame.time.get_ticks()
    qte_duration = qte_length * 1000
    qte_message = "Press the correct keys!"
    pending_bonus = bonus_type


# Apply Bonus
def apply_bonus():
    global active_bonus, double_shot_start_time
    global shield_active, hp

    bonus = pending_bonus

    if bonus == "Mystery":
        bonus = random.choice([
            "Bomb", "Boost", "Heal", "Slow",
            "Shield", "Magnet", "DamageBoost"
        ])

    current_time = pygame.time.get_ticks()

    if bonus == "Bomb":

        for enemy in enemies[:]:

            if enemy["type"] == "GuzaBoss":
                damage_enemy(
                    enemy,
                    min(150, int(enemy["max_hp"] * 0.05))
                )
            elif enemy["type"] == "MiniBoss":
                damage_enemy(enemy, 250)
            else:
                damage_enemy(enemy, 10000)

    elif bonus == "Boost":
        active_effects["Boost"] = current_time + bonus_durations["Boost"]

    elif bonus == "Heal":
        hp = min(max_hp, hp + int(max_hp * 0.30))

    elif bonus == "Slow":
        active_effects["Slow"] = current_time + bonus_durations["Slow"]

    elif bonus == "Shield":
        shield_active = True
        active_effects["Shield"] = current_time + bonus_durations["Shield"]

    elif bonus == "Magnet":
        active_effects["Magnet"] = current_time + bonus_durations["Magnet"]

    elif bonus == "DamageBoost":
        active_effects["DamageBoost"] = current_time + bonus_durations["DamageBoost"]

    elif bonus in ship_bonus_types.get(player_ship, []):
        active_effects[bonus] = current_time + bonus_durations[bonus]


# Health Bar
def draw_health_bar():
    bar_x = 38
    bar_y = 56
    bar_width = 330
    bar_height = 22

    hp_percentage = max(0, hp / max_hp)

    label = small_font.render("HULL INTEGRITY", True, (220, 235, 255))
    Screen.blit(label, (bar_x, 28))

    pygame.draw.rect(
        Screen, (70, 70, 70),
        (bar_x, bar_y, bar_width, bar_height),
        border_radius=5
    )

    pygame.draw.rect(
        Screen, (40, 220, 80),
        (
            bar_x, bar_y,
            int(bar_width * hp_percentage), bar_height
        ),
        border_radius=5
    )

    pygame.draw.rect(
        Screen, (255, 255, 255),
        (bar_x, bar_y, bar_width, bar_height),
        2,
        border_radius=5
    )

    hp_text = small_font.render(
        f"{hp}/{max_hp} HP",
        True,
        (255, 255, 255)
    )

    Screen.blit(hp_text, hp_text.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2)))


def draw_hud_panel(rect):
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    panel.fill((7, 15, 35, 220))
    Screen.blit(panel, rect.topleft)
    pygame.draw.rect(
        Screen,
        (55, 105, 155),
        rect,
        2,
        border_radius=14
    )


# Damage Enemy
def damage_enemy(enemy, damage):
    global score, stolen_attribute, stolen_value
    global stolen_stats, hp, max_hp
    global boss_last_hp_phase, next_boss_wave
    global black_hole_active, black_hole_warning, bonus_drop_chance

    if enemy not in enemies:
        return

    enemy.setdefault("hp", 10)
    enemy["hp"] -= damage

    if enemy.get("type") == "GuzaBoss":

        phase = int(
            (1 - max(0, enemy["hp"]) / enemy["max_hp"]) * 3
        )

        if phase > boss_last_hp_phase and phase <= 2:

            boss_last_hp_phase = phase

            for i in range(5):
                add_enemy(
                    random.choice(["Enemy1", "Enemy2", "Enemy3"]),
                    100 + i * 180,
                    220 + (i % 2) * 65
                )

    if enemy["hp"] <= 0:

        enemies.remove(enemy)

        if enemy.get("type") == "GuzaBoss":
            next_boss_wave = wave + random.randint(5, 10)
            black_hole_active = False
            black_hole_warning = False

            bonus_drop_chance = min(
                bonus_drop_max_chance,
                bonus_drop_chance + bonus_drop_boss_increase
            )

            if player_ship == "ArtShip":
                for attribute, increase in art_boss_cap_increase.items():
                    art_stolen_caps[attribute] += increase

        score += (
            100 if enemy.get("type") in ["MiniBoss", "GuzaBoss"]
            else 10
        )

        # ArtShip Attribute Theft
        if player_ship == "ArtShip" and random.random() < 0.15:

            stolen_values = {
                "hp": 20,
                "speed": 1,
                "damage": 5,
                "fire_rate": 50,
                "range": 30
            }
            available_attributes = [
                attribute for attribute in stolen_values
                if stolen_stats[attribute] < art_stolen_caps[attribute]
            ]

            if available_attributes:
                stolen_attribute = random.choice(available_attributes)
                stolen_value = min(
                    stolen_values[stolen_attribute],
                    art_stolen_caps[stolen_attribute]
                    - stolen_stats[stolen_attribute]
                )
                stolen_stats[stolen_attribute] += stolen_value

                if stolen_attribute == "hp":
                    max_hp += stolen_value
                    hp += stolen_value

        # Bonus Drop
        if (
            random.random() < bonus_drop_chance
            and len(bonuses) < bonus_max_on_screen
        ):

            available_bonuses = (
                bonus_types + ship_bonus_types.get(player_ship, [])
            )
            bonus_type = random.choice(available_bonuses)

            bonuses.append({
                "x": (
                    enemy["x"]
                    + enemy.get("width", enemy_width) // 2
                    - bonus_width // 2
                ),
                "y": enemy["y"],
                "type": bonus_type
            })


# Get Current Stats
def get_player_damage():
    damage = ship_data[player_ship]["damage"]
    current_time = pygame.time.get_ticks()

    if player_ship == "ArtShip":
        damage += stolen_stats["damage"]

    if active_effects["BoostPunch"] > current_time and player_ship == "VovaShip":
        damage = int(damage * 1.5)

    if active_effects["LaserBoost"] > current_time and player_ship == "ZahShip":
        damage = int(damage * 1.5)

    if active_effects["AtributeBoost"] > current_time and player_ship == "ArtShip":
        damage = int(damage * 1.25)

    if active_effects["DamageBoost"] > current_time:
        damage = int(damage * 1.5)

    return damage


def get_player_speed():
    speed = ship_data[player_ship]["speed"]

    if player_ship == "ArtShip":
        speed += stolen_stats["speed"]

    if active_effects["Boost"] > pygame.time.get_ticks():
        speed *= 1.3

    if active_effects["AtributeBoost"] > pygame.time.get_ticks() and player_ship == "ArtShip":
        speed *= 1.15

    return speed


def get_player_fire_rate():
    fire_rate = ship_data[player_ship]["fire_rate"]

    if player_ship == "ArtShip":
        fire_rate -= stolen_stats["fire_rate"]

    if active_effects["AttackSpeed"] > pygame.time.get_ticks() and player_ship == "DanShip":
        fire_rate *= 0.5

    if active_effects["AtributeBoost"] > pygame.time.get_ticks() and player_ship == "ArtShip":
        fire_rate *= 0.9

    return max(50, int(fire_rate))


def get_player_range():
    attack_range = base_bullet_range

    if player_ship == "ArtShip":
        attack_range += stolen_stats["range"]

    if active_effects["AtributeBoost"] > pygame.time.get_ticks() and player_ship == "ArtShip":
        attack_range += 60

    if player_ship == "DanShip":
        attack_range += 200

    if active_effects["LaserBoost"] > pygame.time.get_ticks() and player_ship == "ZahShip":
        attack_range += 200

    return attack_range


# ZahShip Laser Attack
def shoot_laser():
    global last_laser_time, laser_active
    global laser_start, laser_end

    current_time = pygame.time.get_ticks()

    if current_time - last_laser_time < laser_cooldown:
        return

    player_center = (
        x + player_width // 2,
        y + player_height // 2
    )

    mouse_x, mouse_y = pygame.mouse.get_pos()

    dx = mouse_x - player_center[0]
    dy = mouse_y - player_center[1]

    distance = math.hypot(dx, dy)

    if distance == 0:
        return

    direction_x = dx / distance
    direction_y = dy / distance

    effective_laser_range = laser_range
    if active_effects["LaserBoost"] > current_time:
        effective_laser_range += 200

    laser_start = player_center

    laser_end = (
        int(player_center[0] + direction_x * effective_laser_range),
        int(player_center[1] + direction_y * effective_laser_range)
    )

    laser_active = True
    last_laser_time = current_time

    laser_line = (laser_start, laser_end)

    for enemy in enemies[:]:

        enemy_rect = pygame.Rect(
            enemy["x"],
            enemy["y"],
            enemy["width"],
            enemy["height"]
        )

        if enemy_rect.clipline(laser_line):
            damage_enemy(enemy, get_player_damage())


# Start Game
spawn_enemies()

background_index = 0
previous_background_index = 0
background_change_delay = 20000
background_transition_duration = 2500
background_transition_start = 0
last_background_change_time = pygame.time.get_ticks()

run = True
game_started = False


# Main Game Loop
while run:

    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            run = False
            continue

        if game_state == "menu":

            main_menu.handle_event(event)

            if main_menu.start_requested:

                reset_player()

                game_state = "playing"
                game_started = True
                score_submitted = False

                main_menu.reset_start_request()

            if main_menu.quit_requested:
                run = False

        elif game_state == "playing" and not game_over:

            if qte_active:

                if event.type == pygame.KEYDOWN and event.key in qte_keys:

                    if (
                        qte_index < len(qte_sequence)
                        and event.key == qte_sequence[qte_index]
                    ):

                        qte_index += 1

                        if qte_index >= len(qte_sequence):

                            qte_active = False
                            apply_bonus()
                            qte_message = "Bonus activated!"
                            grant_invincibility()

                    else:

                        qte_active = False
                        qte_message = "Wrong key!"

                continue

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_SPACE
            ):

                if player_ship == "VovaShip":

                    if current_time - last_cone_time >= cone_cooldown:

                        cone_active = True
                        cone_start_time = current_time
                        cone_hit_ids.clear()
                        last_cone_time = current_time

                elif player_ship == "PlatShip":

                    if not beam_charging and not beam_active:

                        beam_charging = True
                        beam_charge_start = current_time

            elif (
                event.type == pygame.KEYUP
                and event.key == pygame.K_SPACE
            ):

                if player_ship == "PlatShip" and beam_charging:

                    charge_time = min(
                        beam_max_charge,
                        current_time - beam_charge_start
                    )

                    beam_charging = False
                    beam_active = True
                    beam_start_time = current_time

                    beam_duration = max(
                        500,
                        int(500 + charge_time * 1.0)
                    )

                    beam_damage = (
                        50 + int(100 * (charge_time / beam_max_charge))
                    )

    # Game Logic
    if (
        game_state == "playing"
        and not game_over
        and not qte_active
    ):

        # Background Change
        if current_time - last_background_change_time >= background_change_delay:

            previous_background_index = background_index
            background_index = (
                background_index + 1
            ) % len(background_images)

            last_background_change_time = current_time
            background_transition_start = current_time

        # Wave State
        if wave_state == "break":

            if current_time - wave_break_start >= wave_break_duration:

                wave += 1
                wave_state = "active"
                spawn_enemies()

        elif wave_state == "active" and len(enemies) == 0:

            wave_state = "break"
            wave_break_start = current_time
            enemy_bullets.clear()
            grant_invincibility()

        # Player Movement
        keys = pygame.key.get_pressed()

        if wave_state in ("active", "break"):

            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                x -= get_player_speed()

            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                x += get_player_speed()

            if keys[pygame.K_w] or keys[pygame.K_UP]:
                y -= get_player_speed()

            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                y += get_player_speed()

        x = max(0, min(W - player_width, x))
        y = max(0, min(H - player_height, y))

        # ZahShip Laser
        if player_ship == "ZahShip":

            mouse_buttons = pygame.mouse.get_pressed()

            if mouse_buttons[0] and wave_state == "active":
                shoot_laser()

        # Player Shooting
        if (
            keys[pygame.K_SPACE]
            and player_ship not in ["VovaShip", "PlatShip", "ZahShip"]
        ):

            if current_time - last_shot_time >= get_player_fire_rate():

                bullet_x = x + player_width // 2 - bullet_width // 2

                if player_ship == "DanShip":
                    for offset in (-14, 14):
                        bullets.append({
                            "x": bullet_x + offset,
                            "y": y,
                            "start_y": y
                        })
                else:
                    bullets.append({
                        "x": bullet_x,
                        "y": y,
                        "start_y": y
                    })

                if active_bonus == "Double Shot":

                    bullets.append({
                        "x": bullet_x - 25,
                        "y": y,
                        "start_y": y
                    })

                    bullets.append({
                        "x": bullet_x + 25,
                        "y": y,
                        "start_y": y
                    })

                last_shot_time = current_time

        # Bullet Movement
        for bullet in bullets[:]:

            bullet["y"] -= bullet_speed

            if bullet["start_y"] - bullet["y"] > get_player_range():
                bullets.remove(bullet)
                continue

            if bullet["y"] < -bullet_height:
                bullets.remove(bullet)
                continue

            bullet_rect = pygame.Rect(
                bullet["x"], bullet["y"],
                bullet_width, bullet_height
            )

            for enemy in enemies[:]:

                enemy_rect = pygame.Rect(
                    enemy["x"], enemy["y"],
                    enemy["width"], enemy["height"]
                )

                if bullet_rect.colliderect(enemy_rect):

                    damage_enemy(enemy, get_player_damage())

                    if bullet in bullets:
                        bullets.remove(bullet)

                    break

        # VovaShip Attack
        if cone_active:

            if current_time - cone_start_time >= cone_duration:
                cone_active = False

            else:

                player_center_x = x + player_width // 2
                player_top = y

                punch_range_multiplier = (
                    1.5
                    if active_effects["PunchRange"] > current_time
                    else 1.0
                )
                attack_width = int(cone_visual_width * punch_range_multiplier)
                attack_height = int(cone_visual_height * punch_range_multiplier)
                attack_rect = pygame.Rect(
                    player_center_x - attack_width // 2,
                    player_top - attack_height,
                    attack_width,
                    attack_height
                )

                for enemy in enemies[:]:

                    enemy_rect = pygame.Rect(
                        enemy["x"], enemy["y"],
                        enemy["width"], enemy["height"]
                    )

                    enemy_id = id(enemy)

                    if enemy_id in cone_hit_ids:
                        continue

                    dx = enemy_rect.centerx - player_center_x
                    dy = player_top - enemy_rect.centery

                    if (
                        attack_rect.colliderect(enemy_rect)
                        and 0 <= dy <= attack_height
                        and abs(dx) <= 45 + dy * 0.58 * punch_range_multiplier
                    ):

                        damage_enemy(enemy, get_player_damage() * 2)
                        cone_hit_ids.add(enemy_id)

        # PlatShip Beam
        if beam_active:

            if current_time - beam_start_time >= beam_duration:

                beam_active = False
                beam_hit_timers = {}

            else:

                beam_rect = pygame.Rect(
                    x + player_width // 2 - beam_width // 2,
                    0,
                    beam_width,
                    y
                )

                for enemy in enemies[:]:

                    enemy_rect = pygame.Rect(
                        enemy["x"], enemy["y"],
                        enemy["width"], enemy["height"]
                    )

                    if beam_rect.colliderect(enemy_rect):

                        last_hit = beam_hit_timers.get(id(enemy), 0)

                        if current_time - last_hit >= 300:

                            beam_hit_damage = beam_damage
                            if active_effects["BeamBoost"] > current_time:
                                beam_hit_damage = int(beam_hit_damage * 1.5)
                            damage_enemy(enemy, beam_hit_damage)
                            beam_hit_timers[id(enemy)] = current_time

        # Enemy Movement
        enemy_slow_multiplier = (
            0.5 if active_effects["Slow"] > current_time else 1.0
        )

        for enemy in enemies[:]:

            if enemy["entering"]:

                enemy["y"] += 2

                if enemy["y"] >= enemy["target_y"]:

                    enemy["y"] = enemy["target_y"]
                    enemy["entering"] = False

            else:

                enemy["x"] += (
                    enemy["speed"]
                    * enemy_direction
                    * enemy_slow_multiplier
                )

                if (
                    enemy["x"] <= 0
                    or enemy["x"] + enemy["width"] >= W
                ):
                    enemy_direction *= -1

            enemy_rect = pygame.Rect(
                enemy["x"], enemy["y"],
                enemy["width"], enemy["height"]
            )

            player_rect = pygame.Rect(
                x, y, player_width, player_height
            )

            if enemy_rect.colliderect(player_rect):
                take_damage(enemy["damage"])

        # Enemy Shooting
        if current_time - last_enemy_shot_time >= enemy_shoot_delay:

            shooters = [
                enemy for enemy in enemies
                if not enemy["entering"]
                and enemy["type"] != "GuzaBoss"
            ]

            if shooters:

                wave_shooters = min(
                    len(shooters),
                    1 + wave // 5
                )

                selected_shooters = random.sample(
                    shooters, wave_shooters
                )

                for enemy in selected_shooters:

                    enemy_bullets.append({
                        "x": (
                            enemy["x"]
                            + enemy["width"] // 2
                            - enemy_bullet_width // 2
                        ),
                        "y": enemy["y"] + enemy["height"],
                        "speed": enemy_bullet_speed + wave * 0.4,
                        "damage": enemy["damage"]
                    })

            last_enemy_shot_time = current_time

        # Enemy Bullet Movement
        for bullet in enemy_bullets[:]:

            bullet["y"] += bullet["speed"]

            if bullet["y"] > H:
                enemy_bullets.remove(bullet)
                continue

            bullet_rect = pygame.Rect(
                bullet["x"], bullet["y"],
                enemy_bullet_width, enemy_bullet_height
            )

            player_rect = pygame.Rect(
                x, y, player_width, player_height
            )

            if bullet_rect.colliderect(player_rect):

                take_damage(bullet["damage"])

                if bullet in enemy_bullets:
                    enemy_bullets.remove(bullet)

        # GuzaBoss Black Hole
        boss = next(
            (
                enemy for enemy in enemies
                if enemy["type"] == "GuzaBoss"
            ),
            None
        )

        if boss:

            if (
                not black_hole_active
                and not black_hole_warning
                and current_time >= black_hole_next_attack
            ):

                black_hole_warning = True
                black_hole_warning_start = current_time

                black_hole_x = random.choice([
                    100, W // 2, W - 100
                ])

                black_hole_next_attack = current_time + 9000

            if black_hole_warning:

                if current_time - black_hole_warning_start >= 1500:

                    black_hole_warning = False
                    black_hole_active = True
                    black_hole_start = current_time
                    black_hole_damage_timer = current_time

            if black_hole_active:

                if current_time - black_hole_start >= black_hole_duration:

                    black_hole_active = False

                else:

                    hole_center_x = black_hole_x
                    hole_center_y = black_hole_y

                    player_center_x = x + player_width // 2
                    player_center_y = y + player_height // 2

                    dx = hole_center_x - player_center_x
                    dy = hole_center_y - player_center_y

                    distance = math.sqrt(dx ** 2 + dy ** 2)

                    if distance > 0:

                        pull_strength = black_hole_pull * (
                            1 + max(0, 300 - distance) / 100
                        )

                        x += (dx / distance) * pull_strength
                        y += (dy / distance) * pull_strength

                    x = max(0, min(W - player_width, x))
                    y = max(0, min(H - player_height, y))

                    hole_rect = pygame.Rect(
                        hole_center_x - black_hole_width // 2,
                        hole_center_y - black_hole_height // 2,
                        black_hole_width,
                        black_hole_height
                    )

                    player_rect = pygame.Rect(
                        x, y, player_width, player_height
                    )

                    if (
                        hole_rect.colliderect(player_rect)
                        and current_time - black_hole_damage_timer >= 500
                    ):

                        take_damage(18)
                        black_hole_damage_timer = current_time

        # Bonus Movement
        for bonus in bonuses[:]:

            bonus["y"] += bonus_speed

            if active_effects["Magnet"] > current_time:

                player_center_x = x + player_width // 2
                player_center_y = y + player_height // 2

                bonus_center_x = bonus["x"] + bonus_width // 2
                bonus_center_y = bonus["y"] + bonus_height // 2

                dx = player_center_x - bonus_center_x
                dy = player_center_y - bonus_center_y

                distance = math.hypot(dx, dy)

                if distance > 0:

                    bonus["x"] += dx / distance * 7
                    bonus["y"] += dy / distance * 7

            if bonus["y"] > H:
                bonuses.remove(bonus)
                continue

            bonus_rect = pygame.Rect(
                bonus["x"], bonus["y"],
                bonus_width, bonus_height
            )

            player_rect = pygame.Rect(
                x, y, player_width, player_height
            )

            if bonus_rect.colliderect(player_rect):

                start_qte(bonus["type"])
                bonuses.remove(bonus)
                break

        # Bonus Effect Timers
        for effect in active_effects:

            if active_effects[effect] <= current_time:
                active_effects[effect] = 0

        shield_active = active_effects["Shield"] > current_time

        # Invincibility Timer
        if invincible:

            if (
                current_time - invincibility_start_time
                >= invincibility_duration
            ):
                invincible = False

    # QTE Timeout
    if (
        qte_active
        and current_time - qte_start_time >= qte_duration
    ):

        qte_active = False
        qte_message = "Time is up!"

    # Drawing
    if game_state == "menu":

        main_menu.draw()

    elif game_state == "playing":

        if (
            background_transition_start
            and current_time - background_transition_start
            < background_transition_duration
        ):
            Screen.blit(background_images[previous_background_index], (0, 0))
            fade_ratio = min(
                1.0,
                (current_time - background_transition_start)
                / background_transition_duration
            )
            next_background = background_images[background_index]
            next_background.set_alpha(int(255 * fade_ratio))
            Screen.blit(next_background, (0, 0))
            next_background.set_alpha(255)
        else:
            Screen.blit(background_images[background_index], (0, 0))

        draw_hud_panel(pygame.Rect(20, 16, W - 40, 88))

        # Player
        if not invincible or current_time // 100 % 2 == 0:
            Screen.blit(player_image, (x, y))

        draw_health_bar()

        # ART Stolen Attributes
        if player_ship == "ArtShip":
            art_attribute_names = {
                "hp": "HP",
                "speed": "Speed",
                "damage": "Damage",
                "fire_rate": "Fire rate",
                "range": "Range"
            }
            art_panel = pygame.Rect(W - 300, 112, 280, 150)
            draw_hud_panel(art_panel)
            art_title = small_font.render("STOLEN ATTRIBUTES", True, (255, 210, 120))
            Screen.blit(art_title, (art_panel.x + 16, art_panel.y + 8))
            art_caps = art_stolen_caps
            for index, attribute in enumerate(stolen_stats):
                amount = stolen_stats[attribute]
                if amount >= art_caps[attribute]:
                    value_text = f"MAX +{amount}"
                    value_color = (255, 205, 110)
                else:
                    value_text = f"+{amount}"
                    value_color = (180, 235, 255)
                row_y = art_panel.y + 34 + index * 22
                name_text = small_font.render(art_attribute_names[attribute], True, (220, 235, 255))
                amount_text = small_font.render(value_text, True, value_color)
                Screen.blit(name_text, (art_panel.x + 16, row_y))
                Screen.blit(amount_text, (art_panel.right - amount_text.get_width() - 16, row_y))
        # Active Effects
        effect_y = 115
        visible_effects = [
            (effect, end_time)
            for effect, end_time in active_effects.items()
            if end_time > current_time
        ]

        if visible_effects:
            effects_panel_height = 18 + len(visible_effects) * 27
            draw_hud_panel(
                pygame.Rect(20, 112, 300, effects_panel_height)
            )

        for effect, end_time in visible_effects:

            seconds_left = max(
                0,
                (end_time - current_time) / 1000
            )

            effect_text = small_font.render(
                f"{effect}: {seconds_left:.1f}s",
                True,
                (160, 230, 255)
            )

            Screen.blit(effect_text, (38, effect_y))
            effect_y += 27

        # Score
        score_text = font.render(
            f"Score: {score}",
            True,
            (255, 255, 255)
        )

        Screen.blit(score_text, (W - 225, 39))

        # Wave
        wave_text = font.render(
            f"Wave: {wave}",
            True,
            (255, 255, 255)
        )

        Screen.blit(wave_text, wave_text.get_rect(center=(W // 2, 59)))

        # Player Bullets
        for bullet in bullets:

            Screen.blit(
                bullet_sprite,
                (bullet["x"], bullet["y"])
            )

        # Enemy Bullets
        for bullet in enemy_bullets:

            Screen.blit(
                enemy_bullet_image,
                (bullet["x"], bullet["y"])
            )

        # Enemies
        for enemy in enemies:

            Screen.blit(
                enemy["image"],
                (enemy["x"], enemy["y"])
            )

            # Boss Health Bar
            if enemy["type"] in ["MiniBoss", "GuzaBoss"]:

                bar_width = (
                    250 if enemy["type"] == "GuzaBoss"
                    else 130
                )

                bar_height = 15

                bar_x = (
                    enemy["x"]
                    + enemy["width"] // 2
                    - bar_width // 2
                )

                bar_y = enemy["y"] - 25

                hp_percentage = max(
                    0,
                    enemy["hp"] / enemy["max_hp"]
                )

                pygame.draw.rect(
                    Screen,
                    (80, 80, 80),
                    (bar_x, bar_y, bar_width, bar_height)
                )

                pygame.draw.rect(
                    Screen,
                    (220, 40, 40),
                    (
                        bar_x, bar_y,
                        int(bar_width * hp_percentage),
                        bar_height
                    )
                )

        # Black Hole Warning
        if black_hole_warning:

            Screen.blit(
                warning_image,
                (
                    black_hole_x - 50,
                    black_hole_y - 50
                )
            )

        # Black Hole
        if black_hole_active:

            Screen.blit(
                black_hole_image,
                (
                    black_hole_x - black_hole_width // 2,
                    black_hole_y - black_hole_height // 2
                )
            )

        # Bonuses
        for bonus in bonuses:

            Screen.blit(
                bonus_images[bonus["type"]],
                (bonus["x"], bonus["y"])
            )

        # ZahShip Laser Visual
        if (
            player_ship == "ZahShip"
            and laser_active
            and current_time - last_laser_time <= laser_visual_duration
        ):

            pygame.draw.line(
                Screen,
                laser_color,
                laser_start,
                laser_end,
                laser_width
            )

            pygame.draw.line(
                Screen,
                (220, 255, 255),
                laser_start,
                laser_end,
                2
            )

        # VovaShip Punch
        if cone_active:

            punch_range_multiplier = (
                1.5
                if active_effects["PunchRange"] > current_time
                else 1.0
            )
            punch_width = int(360 * punch_range_multiplier)
            punch_height = int(300 * punch_range_multiplier)

            punch_scaled = pygame.transform.smoothscale(
                punch_image,
                (punch_width, punch_height)
            )

            Screen.blit(
                punch_scaled,
                (
                    x + player_width // 2 - punch_width // 2,
                    y - punch_height + 25
                )
            )

        # PlatShip Beam Charging
        if beam_charging:

            charge_panel = pygame.Rect(W // 2 - 165, H - 92, 330, 78)
            draw_hud_panel(charge_panel)

            charge_ratio = min(
                1.0,
                (current_time - beam_charge_start) / beam_max_charge
            )

            charge_text = small_font.render(
                f"BEAM CHARGE: {int(charge_ratio * 100)}%",
                True,
                (100, 220, 255)
            )

            Screen.blit(
                charge_text,
                (W // 2 - 90, H - 75)
            )

            pygame.draw.rect(
                Screen,
                (50, 50, 70),
                (W // 2 - 100, H - 45, 200, 14)
            )

            pygame.draw.rect(
                Screen,
                (80, 210, 255),
                (
                    W // 2 - 100,
                    H - 45,
                    int(200 * charge_ratio),
                    14
                )
            )

        # PlatShip Beam
        if beam_active:

            beam_height = max(1, y)

            beam_scaled = pygame.transform.smoothscale(
                beam_image,
                (beam_width, beam_height)
            )

            Screen.blit(
                beam_scaled,
                (
                    x + player_width // 2 - beam_width // 2,
                    0
                )
            )

        # QTE
        if qte_active:

            dim_overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            dim_overlay.fill((3, 8, 20, 150))
            Screen.blit(dim_overlay, (0, 0))
            qte_panel = pygame.Rect(W // 2 - 390, H // 2 - 145, 780, 290)
            draw_hud_panel(qte_panel)

            qte_labels = [
                font.render(
                    qte_key_names[key],
                    True,
                    (80, 255, 125) if index < qte_index else (255, 225, 55)
                )
                for index, key in enumerate(qte_sequence)
            ]
            qte_spacing = font.size(" ")[0]
            qte_total_width = (
                sum(label.get_width() for label in qte_labels)
                + qte_spacing * (len(qte_labels) - 1)
            )
            qte_x = W // 2 - qte_total_width // 2

            for label in qte_labels:
                Screen.blit(label, (qte_x, H // 2 - 15 - label.get_height() // 2))
                qte_x += label.get_width() + qte_spacing

            qte_hint = small_font.render(
                f"BONUS SEQUENCE  |  {qte_index}/{len(qte_sequence)}",
                True,
                (160, 220, 255)
            )
            Screen.blit(qte_hint, qte_hint.get_rect(center=(W // 2, H // 2 - 72)))

            qte_time_left = max(
                0,
                (qte_duration - (current_time - qte_start_time)) / 1000
            )

            timer_text = font.render(
                f"Time: {qte_time_left:.1f}s",
                True,
                (255, 255, 255)
            )

            Screen.blit(timer_text, timer_text.get_rect(center=(W // 2, H // 2 + 73)))

        # Wave Completed
        if wave_state == "break":

            if current_time - wave_break_start <= wave_message_duration:

                wave_panel = pygame.Rect(W // 2 - 235, H // 2 - 48, 470, 96)
                draw_hud_panel(wave_panel)

                wave_completed_text = font.render(
                    "WAVE COMPLETED",
                    True,
                    (255, 255, 255)
                )

                Screen.blit(
                    wave_completed_text,
                    wave_completed_text.get_rect(center=wave_panel.center)
                )

        # Bonus Message
        if qte_message:

            message_text = small_font.render(
                qte_message,
                True,
                (255, 255, 0)
            )

            message_panel = pygame.Rect(W // 2 - 220, H - 78, 440, 52)
            draw_hud_panel(message_panel)
            Screen.blit(message_text, message_text.get_rect(center=message_panel.center))

        # Game Over
        if game_over:

            dim_overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            dim_overlay.fill((3, 8, 20, 175))
            Screen.blit(dim_overlay, (0, 0))
            game_over_panel = pygame.Rect(W // 2 - 310, H // 2 - 165, 620, 330)
            draw_hud_panel(game_over_panel)

            game_over_text = font.render(
                "GAME OVER",
                True,
                (255, 0, 0)
            )

            Screen.blit(
                game_over_text,
                (W // 2 - 135, H // 2 - 95)
            )

            final_score_text = font.render(
                f"Final Score: {score}",
                True,
                (255, 255, 255)
            )

            Screen.blit(
                final_score_text,
                (W // 2 - 145, H // 2 - 25)
            )

            restart_text = small_font.render(
                "Press ENTER to return to menu",
                True,
                (255, 255, 255)
            )

            Screen.blit(
                restart_text,
                (W // 2 - 185, H // 2 + 65)
            )

    # Restart After Game Over
    if game_state == "playing" and game_over:

        keys = pygame.key.get_pressed()

        if keys[pygame.K_RETURN]:

            game_state = "menu"
            game_over = False

    # Submit Score
    if (
        game_state == "playing"
        and game_over
        and not score_submitted
    ):

        if main_menu.submit_score(score, player_ship):
            print("Score submitted successfully!")
        else:
            print("Failed to submit score.")

        score_submitted = True

    pygame.display.flip()
    clock.tick(60)


pygame.quit()
