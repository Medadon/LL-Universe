
import pygame
import os

pygame.init()

# Window
W, H = 1000, 800

Screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("LL Universe!")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Times New Roman", 30)


# First Sprite
sprite_path = os.path.join(
    os.path.dirname(__file__),
    "Assets",
    "Sprites",
    "Player1.png"
)

# Bullet Sprite
bullet_sprite_path = os.path.join(
    os.path.dirname(__file__),
    "Assets",
    "Sprites",
    "Bullet.png"
)

player_sprite = pygame.image.load(sprite_path).convert_alpha()
bullet_sprite = pygame.image.load(bullet_sprite_path).convert_alpha()


# Player Sprite Settings
player_width = 70
player_height = int(
    player_sprite.get_height() *
    (player_width / player_sprite.get_width())
)

player_image = pygame.transform.scale(
    player_sprite,
    (player_width, player_height)
)


# Bullet Sprite Settings
bullet_width = 12
bullet_height = 25

bullet_image = pygame.transform.smoothscale(
    bullet_sprite,
    (bullet_width, bullet_height)
)


# Player Settings
x = 100
y = 100
player_speed = 5


# Bullet Settings
bullets = []
bullet_speed = 16

shoot_cooldown = 250
last_shot_time = 0


# Game Settings
run = True
game_started = False


while run:

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                game_started = True

    # Background
    Screen.fill((5, 5, 25))

    if not game_started:

        # Menu
        text = font.render(
            "PRESS ENTER TO START",
            True,
            (255, 255, 255)
        )

        Screen.blit(text, (100, 270))

    else:

        # Movement
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            y -= player_speed

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            y += player_speed

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            x -= player_speed

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            x += player_speed

        # Keep Player Inside Screen
        x = max(0, min(x, W - player_width))
        y = max(0, min(y, H - player_height))

        # Shooting
        current_time = pygame.time.get_ticks()

        if keys[pygame.K_SPACE]:
            if current_time - last_shot_time >= shoot_cooldown:

                bullet_x = x + player_width // 2 - bullet_width // 2
                bullet_y = y

                bullets.append([bullet_x, bullet_y])

                last_shot_time = current_time

        # Bullet Movement
        for bullet in bullets:
            bullet[1] -= bullet_speed

        # Remove Bullets Outside Screen
        bullets = [
            bullet for bullet in bullets
            if bullet[1] > -bullet_height
        ]

        # Draw Bullets
        for bullet in bullets:
            Screen.blit(
                bullet_image,
                (bullet[0], bullet[1])
            )

        # Draw Player
        Screen.blit(player_image, (x, y))

    pygame.display.flip()
    clock.tick(60)


pygame.quit()
