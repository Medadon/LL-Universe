
import pygame
import os
import random
from Client.klient import klient

pygame.init()

#Window
W, H = 1000, 800

Screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("LL Universe!")

#Main Menu Settings
main_menu = klient(Screen)
game_state = "menu"

clock = pygame.time.Clock()
font = pygame.font.SysFont("Times New Roman", 30)


#First Sprite
sprite_path = os.path.join(
    os.path.dirname(__file__),
    "Assets",
    "Sprites",
    "PlatShip.png"
)

#Bullet Sprite
bullet_sprite_path = os.path.join(
    os.path.dirname(__file__),
    "Assets",
    "Sprites",
    "Bullet.png"
)

player_sprite = pygame.image.load(sprite_path).convert_alpha()
bullet_sprite = pygame.image.load(bullet_sprite_path).convert_alpha()


#Player Sprite Settings
player_width = 70
player_height = int(
    player_sprite.get_height() *
    (player_width / player_sprite.get_width())
)

player_image = pygame.transform.scale(
    player_sprite,
    (player_width, player_height)
)


#Bullet Sprite Settings
bullet_width = 12
bullet_height = 25

bullet_image = pygame.transform.smoothscale(
    bullet_sprite,
    (bullet_width, bullet_height)
)


#Enemies Sprite Settings
enemy_sprite_path = os.path.join(
    os.path.dirname(__file__),
    "Assets",
    "Sprites",
    "Enemy1.png"
)

enemy_sprite = pygame.image.load(enemy_sprite_path).convert_alpha()

enemy_width = 50
enemy_height = int(
    enemy_sprite.get_height() *
    (enemy_width / enemy_sprite.get_width())
)

enemy_image = pygame.transform.scale(
    enemy_sprite,
    (enemy_width, enemy_height)
)


#Enemy bullet Sprite Settings
enemy_bullet_red_sprite_path = os.path.join(
    os.path.dirname(__file__),
    "Assets",
    "Sprites",
    "bullet_red.png"
)

enemy_bullet_red_sprite = pygame.image.load(
    enemy_bullet_red_sprite_path
).convert_alpha()

enemy_bullet_width = 20
enemy_bullet_height = 30

enemy_bullet_image = pygame.transform.scale(
    enemy_bullet_red_sprite,
    (enemy_bullet_width, enemy_bullet_height)
)


#Bonus Sprite Settings
bonus1_sprite_path = os.path.join(
    os.path.dirname(__file__),
    "Assets",
    "Sprites",
    "bonus1.png"
)

bonus2_sprite_path = os.path.join(
    os.path.dirname(__file__),
    "Assets",
    "Sprites",
    "bonus2.png"
)

bonus1_sprite = pygame.image.load(
    bonus1_sprite_path
).convert_alpha()

bonus2_sprite = pygame.image.load(
    bonus2_sprite_path
).convert_alpha()

bonus_width = 40
bonus_height = 40

bonus1_image = pygame.transform.scale(
    bonus1_sprite,
    (bonus_width, bonus_height)
)

bonus2_image = pygame.transform.scale(
    bonus2_sprite,
    (bonus_width, bonus_height)
)


#Background Sprite Settings
background_sprite_paths = [
    os.path.join(
        os.path.dirname(__file__),
        "Assets",
        "Backgrounds",
        "background.jpg"
    ),
    os.path.join(
        os.path.dirname(__file__),
        "Assets",
        "Backgrounds",
        "background2.jpg"
    ),
    os.path.join(
        os.path.dirname(__file__),
        "Assets",
        "Backgrounds",
        "background3.jpg"
    )
]

background_images = []

for path in background_sprite_paths:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Background file not found: {path}")

    background_sprite = pygame.image.load(path).convert()

    background_image = pygame.transform.scale(
        background_sprite,
        (W, H)
    )

    background_images.append(background_image)


#Player Settings
x = 100
y = 650
player_speed = 5


#Bullet Settings
bullets = []
bullet_speed = 16

shoot_cooldown = 250
last_shot_time = 0


#Enemy Settings
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

score = 0
game_over = False


#Bonus Settings
bonuses = []
bonus_speed = 3
bonus_drop_chance = 0.2

active_bonus = ""
double_shot_duration = 10000
double_shot_start_time = 0

shield_active = False


#Invincibility Settings
invincible = False
invincibility_duration = 2000
invincibility_start_time = 0


#QTE Settings
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


#spawn enemies
def spawn_enemies():
    global enemies

    enemies = []

    start_x = (W - (enemy_columns - 1) * enemy_spacing_x - enemy_width) // 2
    start_y = 60

    for row in range(enemy_rows):
        for column in range(enemy_columns):
            enemy_x = start_x + column * enemy_spacing_x
            enemy_y = start_y + row * enemy_spacing_y

            enemies.append({
                "x": enemy_x,
                "y": enemy_y
            })


#Start QTE
def start_qte(bonus_type):
    global qte_active, qte_sequence, qte_index
    global qte_start_time, qte_message, pending_bonus

    qte_active = True
    qte_sequence = random.choices(qte_keys, k=4)
    qte_index = 0
    qte_start_time = pygame.time.get_ticks()
    qte_message = "Press the correct keys!"
    pending_bonus = bonus_type


#Apply Bonus
def apply_bonus():
    global active_bonus, double_shot_start_time
    global shield_active, invincible, invincibility_start_time

    if pending_bonus == "bonus1":
        active_bonus = "Double Shot"
        double_shot_start_time = pygame.time.get_ticks()

    elif pending_bonus == "bonus2":
        shield_active = True

    invincible = True
    invincibility_start_time = pygame.time.get_ticks()


spawn_enemies()


#Background Settings
background_index = 0
background_change_delay = 20000  # 20 seconds
last_background_change_time = pygame.time.get_ticks()


run = True
game_started = False
score_submitted = False


while run:

    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():

        if game_state == "menu":

            main_menu.handle_event(event)

            if main_menu.start_requested:
                game_state = "playing"
                game_started = True
                score_submitted = False
                main_menu.reset_start_request()

            if main_menu.quit_requested:
                run = False

        elif game_state == "playing":

            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN and qte_active:

                if event.key in qte_keys:

                    if event.key == qte_sequence[qte_index]:
                        qte_index += 1

                        if qte_index >= len(qte_sequence):
                            qte_active = False
                            qte_message = "SUCCESS!"
                            apply_bonus()

                    else:
                        qte_active = False
                        qte_message = "FAILED!"
                        pending_bonus = ""

    #Submit score after dying and only once
    if game_state == "playing" and game_over and not score_submitted:
        if main_menu.submit_score(score):
            print("Score submitted successfully!")
        else:
            print("Failed to submit score.")

        score_submitted = True

    #Background
    if not qte_active:
        if current_time - last_background_change_time >= background_change_delay:
            background_index = (background_index + 1) % len(background_images)
            last_background_change_time = current_time

    Screen.blit(
        background_images[background_index],
        (0, 0)
    )

    if game_state == "menu":
        main_menu.draw()

    elif game_over:

        text = font.render(
            "GAME OVER",
            True,
            (255, 60, 60)
        )

        score_text = font.render(
            f"Score: {score}",
            True,
            (255, 255, 255)
        )

        Screen.blit(text, (W // 2 - 90, H // 2 - 40))
        Screen.blit(score_text, (W // 2 - 70, H // 2 + 10))

    elif qte_active:

        #QTE
        qte_elapsed = pygame.time.get_ticks() - qte_start_time
        qte_remaining = max(0, qte_duration - qte_elapsed)

        if qte_remaining <= 0:
            qte_active = False
            qte_message = "TIME'S UP!"
            pending_bonus = ""

        qte_title = font.render(
            "QUICK TIME EVENT!",
            True,
            (255, 215, 0)
        )

        Screen.blit(
            qte_title,
            (W // 2 - qte_title.get_width() // 2, 250)
        )

        qte_timer_text = font.render(
            f"Time: {qte_remaining // 1000}.{(qte_remaining % 1000) // 100}",
            True,
            (255, 255, 255)
        )

        Screen.blit(
            qte_timer_text,
            (W // 2 - qte_timer_text.get_width() // 2, 310)
        )

        for i, key in enumerate(qte_sequence):

            color = (100, 255, 100) if i < qte_index else (255, 255, 255)

            key_text = pygame.font.SysFont(
                "Arial",
                45,
                bold=True
            ).render(
                qte_key_names[key],
                True,
                color
            )

            key_x = W // 2 - 110 + i * 60

            Screen.blit(
                key_text,
                (key_x, 390)
            )

        progress_text = font.render(
            f"{qte_index}/{len(qte_sequence)}",
            True,
            (255, 255, 255)
        )

        Screen.blit(
            progress_text,
            (W // 2 - 35, 470)
        )

    else:

        #Invincibility Timer
        if invincible:
            if current_time - invincibility_start_time >= invincibility_duration:
                invincible = False

        #Double Shot Timer
        if active_bonus == "Double Shot":
            if current_time - double_shot_start_time >= double_shot_duration:
                active_bonus = ""

        #Movement
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            y -= player_speed

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            y += player_speed

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            x -= player_speed

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            x += player_speed

        x = max(0, min(x, W - player_width))
        y = max(0, min(y, H - player_height))

        player_rect = pygame.Rect(
            x, y, player_width, player_height
        )

        #Shooting
        current_time = pygame.time.get_ticks()

        if keys[pygame.K_SPACE]:
            if current_time - last_shot_time >= shoot_cooldown:

                if active_bonus == "Double Shot":
                    bullets.append([
                        x + player_width // 2 - bullet_width // 2 - 15,
                        y
                    ])

                    bullets.append([
                        x + player_width // 2 - bullet_width // 2 + 15,
                        y
                    ])

                else:
                    bullet_x = x + player_width // 2 - bullet_width // 2
                    bullet_y = y

                    bullets.append([bullet_x, bullet_y])

                last_shot_time = current_time

        #Bullet Movement
        for bullet in bullets:
            bullet[1] -= bullet_speed

        #Remove Bullets
        bullets = [
            bullet for bullet in bullets
            if bullet[1] > -bullet_height
        ]

        #enemy movement
        if enemies:
            move_down = False

            for enemy in enemies:
                next_x = enemy["x"] + enemy_speed * enemy_direction

                if next_x < 0 or next_x + enemy_width > W:
                    move_down = True
                    break

            if move_down:
                enemy_direction *= -1

                for enemy in enemies:
                    enemy["y"] += 20
            else:
                for enemy in enemies:
                    enemy["x"] += enemy_speed * enemy_direction

        #spawn enemies
        if not enemies:
            spawn_enemies()
            enemy_speed += 0.5

        #Enemy Shooting
        if enemies and current_time - last_enemy_shot_time >= enemy_shoot_delay:
            shooting_enemy = random.choice(enemies)

            enemy_bullet_x = (
                shooting_enemy["x"] + enemy_width // 2 - enemy_bullet_width // 2
            )
            enemy_bullet_y = shooting_enemy["y"] + enemy_height

            enemy_bullets.append([
                enemy_bullet_x,
                enemy_bullet_y
            ])

            last_enemy_shot_time = current_time

        #Enemy Bullet Movement
        for bullet in enemy_bullets:
            bullet[1] += enemy_bullet_speed

        #Remove Enemy Bullets
        enemy_bullets = [
            bullet for bullet in enemy_bullets
            if bullet[1] < H
        ]

        #Bonus Movement
        for bonus in bonuses:
            bonus["y"] += bonus_speed

        bonuses = [
            bonus for bonus in bonuses
            if bonus["y"] < H
        ]

        #Bonus Collision
        for bonus in bonuses[:]:
            bonus_rect = pygame.Rect(
                bonus["x"], bonus["y"],
                bonus_width, bonus_height
            )

            if player_rect.colliderect(bonus_rect):
                bonuses.remove(bonus)
                start_qte(bonus["type"])
                break

        #Kill Enemies
        remaining_bullets = []

        for bullet in bullets:
            bullet_rect = pygame.Rect(
                bullet[0], bullet[1],
                bullet_width, bullet_height
            )

            hit = False

            for enemy in enemies[:]:
                enemy_rect = pygame.Rect(
                    enemy["x"], enemy["y"],
                    enemy_width, enemy_height
                )

                if bullet_rect.colliderect(enemy_rect):
                    enemies.remove(enemy)
                    score += 10

                    if random.random() < bonus_drop_chance:
                        bonus_type = random.choice(["bonus1", "bonus2"])

                        bonuses.append({
                            "x": enemy["x"] + enemy_width // 2 - bonus_width // 2,
                            "y": enemy["y"],
                            "type": bonus_type
                        })

                    hit = True
                    break

            if not hit:
                remaining_bullets.append(bullet)

        bullets = remaining_bullets

        #Player Collision
        for enemy in enemies:
            enemy_rect = pygame.Rect(
                enemy["x"], enemy["y"],
                enemy_width, enemy_height
            )

            if player_rect.colliderect(enemy_rect):
                if shield_active:
                    shield_active = False
                elif not invincible:
                    game_over = True

            if enemy["y"] + enemy_height >= H:
                game_over = True

        #Enemy Bullet Collision
        remaining_enemy_bullets = []

        for bullet in enemy_bullets:
            enemy_bullet_rect = pygame.Rect(
                bullet[0],
                bullet[1],
                enemy_bullet_width,
                enemy_bullet_height
            )

            if player_rect.colliderect(enemy_bullet_rect):
                if shield_active:
                    shield_active = False
                elif not invincible:
                    game_over = True
            else:
                remaining_enemy_bullets.append(bullet)

        enemy_bullets = remaining_enemy_bullets

        #Bullets
        for bullet in bullets:
            Screen.blit(
                bullet_image,
                (bullet[0], bullet[1])
            )

        #Enemy Bullets
        for bullet in enemy_bullets:
            Screen.blit(
                enemy_bullet_image,
                (bullet[0], bullet[1])
            )

        #Bonuses
        for bonus in bonuses:
            if bonus["type"] == "bonus1":
                Screen.blit(
                    bonus1_image,
                    (bonus["x"], bonus["y"])
                )
            else:
                Screen.blit(
                    bonus2_image,
                    (bonus["x"], bonus["y"])
                )

        #Enemies
        for enemy in enemies:
            Screen.blit(
                enemy_image,
                (enemy["x"], enemy["y"])
            )

        #Player
        if not invincible or (current_time // 100) % 2 == 0:
            Screen.blit(player_image, (x, y))

        #Score
        score_text = font.render(
            f"Score: {score}",
            True,
            (255, 255, 255)
        )

        Screen.blit(score_text, (10, 10))

        #Active Bonus
        if active_bonus:
            bonus_text = font.render(
                f"Bonus: {active_bonus}",
                True,
                (255, 215, 0)
            )

            Screen.blit(bonus_text, (10, 50))

        #Shield Status
        if shield_active:
            shield_text = font.render(
                "Shield: ACTIVE",
                True,
                (100, 200, 255)
            )

            Screen.blit(shield_text, (10, 90))

    pygame.display.flip()
    clock.tick(60)


pygame.quit()
