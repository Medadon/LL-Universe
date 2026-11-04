
import pygame
import math
import os
import random
import textwrap
import threading


from .api_client import GameClient


class GameMenu:

    def __init__(self, Screen):

        self.Screen = Screen
        self.width, self.height = Screen.get_size()

        self.network = GameClient()

        self.font = pygame.font.SysFont("Arial", 34, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 22)
        self.title_font = pygame.font.SysFont("Arial", 72, bold=True)

        self.nickname = ""

        #Ship selection
        self.ships = [
            "VovaShip",
            "DanShip",
            "PlatShip",
            "ArtShip",
            "ZahShip"
        ]

        self.selected_ship = 1

        self.ship_images = {}

        sprite_folder = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "game",
            "Assets",
            "Sprites"
        )

        for ship in self.ships:

            path = os.path.join(
                sprite_folder,
                ship + ".png"
            )

            if os.path.exists(path):
                image = pygame.image.load(path).convert_alpha()

                image_width = 110
                image_height = int(
                    image.get_height() *
                    (image_width / image.get_width())
                )

                self.ship_images[ship] = pygame.transform.smoothscale(
                    image,
                    (image_width, image_height)
                )

            else:
                print(f"Ship sprite not found: {path}")

        self.bestiary_images = {}
        for sprite_name in self.ships + ["Enemy1", "Enemy2", "Enemy3", "MiniBoss", "GuzaBoss"]:
            if sprite_name in self.ship_images:
                source_image = self.ship_images[sprite_name]
            else:
                sprite_path = os.path.join(sprite_folder, sprite_name + ".png")
                if not os.path.exists(sprite_path):
                    continue
                source_image = pygame.image.load(sprite_path).convert_alpha()

            scale = min(72 / source_image.get_width(), 72 / source_image.get_height())
            image_size = (
                max(1, int(source_image.get_width() * scale)),
                max(1, int(source_image.get_height() * scale))
            )
            self.bestiary_images[sprite_name] = pygame.transform.smoothscale(
                source_image,
                image_size
            )
        self.active_input = False
        self.current_screen = "menu"

        self.start_requested = False
        self.quit_requested = False

        self.leaderboard = []
        self.leaderboard_loading = False
        self.leaderboard_status = ""

        self.colors = {
            "background": (10, 12, 30),
            "white": (240, 240, 255),
            "blue": (40, 100, 220),
            "light_blue": (70, 150, 255),
            "gray": (80, 85, 110),
            "red": (200, 60, 60),
            "cyan": (70, 220, 255),
            "panel": (13, 24, 52)
        }

        self.menu_background = pygame.Surface((self.width, self.height))
        for y in range(self.height):
            shade = int(12 + 25 * y / self.height)
            pygame.draw.line(
                self.menu_background,
                (7, 12 + shade // 3, shade + 15),
                (0, y),
                (self.width, y)
            )

        for index in range(55):
            star_x = (index * 193 + 41) % self.width
            star_y = (index * 127 + 29) % self.height
            pygame.draw.circle(
                self.menu_background,
                (110, 150, 205),
                (star_x, star_y),
                1
            )

        center_x = self.width // 2
        self.start_button = pygame.Rect(center_x - 415, 690, 150, 62)
        self.leaderboard_button = pygame.Rect(center_x - 245, 690, 150, 62)
        self.story_button = pygame.Rect(center_x - 75, 690, 150, 62)
        self.bestiary_button = pygame.Rect(center_x + 95, 690, 150, 62)
        self.exit_button = pygame.Rect(center_x + 265, 690, 150, 62)

        self.nickname_box = pygame.Rect(center_x - 190, 190, 380, 54)

        self.left_button = pygame.Rect(center_x - 180, 455, 64, 56)
        self.right_button = pygame.Rect(center_x + 116, 455, 64, 56)

        self.back_button = pygame.Rect(30, 30, 150, 50)
        self.story_scroll_offset = 0.0
        self.story_last_update = pygame.time.get_ticks()
        self.story_finale_started_at = None
        self.story_next_shot_at = 0
        self.story_active_shot = None
        self.story_lines = self.build_story_lines()
        self.story_ship_images = {}
        for ship_name, image in self.ship_images.items():
            width = 72
            height = max(1, int(image.get_height() * width / image.get_width()))
            self.story_ship_images[ship_name] = pygame.transform.smoothscale(
                image,
                (width, height),
            )
        self.bestiary_entries = self.build_bestiary_entries()
        self.bestiary_sprite_keys = {
            "Scout - Enemy1": "Enemy1",
            "Assault ship - Enemy2": "Enemy2",
            "Heavy ship - Enemy3": "Enemy3",
            "Mini-Guza - MiniBoss": "MiniBoss",
            "Guza - GuzaBoss": "GuzaBoss"
        }
        self.bestiary_scroll_offset = 0.0
        self.bestiary_max_scroll = 0

    #Get selected ship name
    def get_selected_ship(self):

        return self.ships[self.selected_ship - 1]

    def build_story_lines(self):
        paragraphs = [
            ("title", "LL UNIVERSE"),
            ("heading", "THE LAST WAR FOR THE GALAXY"),
            ("body", "The LL Republic once kept the trade routes and distant worlds safe. That peace ended when the Chuchmeki fleet arrived under the command of the ruthless Guza."),
            ("body", "With the capital fallen, the Republic gathered its last pilots and sent them into the fight in five very different ships. Their mission: push through the invading forces and reach Guza before the galaxy is lost."),
            ("heading", "FIVE PILOTS, FIVE WAYS TO FIGHT"),
            ("body", "Vova breaks enemy formations with a powerful close-range cone strike. Dan relies on a heavily armored ship and a steady stream of fire. Plat charges a beam and releases it when the moment is right."),
            ("body", "Art studies defeated enemies and steals upgrades, growing stronger over the course of a run. Zah aims a laser by hand, rewarding careful target selection."),
            ("heading", "THE INVASION"),
            ("body", "The Chuchmeki send scouts, assault ships and heavy units in waves. Their commanders appear every few waves, while Guza enters the battle at a changing interval. Enemy ships grow stronger as the waves advance."),
            ("heading", "GUZA'S BLACK HOLE"),
            ("body", "Guza's ship can open a spatial anomaly that pulls the pilot toward its center. Watch for the warning marker, move away from the chosen point, and keep steering out of the field while it is active."),
            ("heading", "THE FIGHT IS YOURS"),
            ("body", "Choose the ship that matches your style, collect bonuses between waves, and survive long enough to confront the commander of the Chuchmeki Empire.")
        ]

        lines = []
        vertical_offset = 0
        for style, paragraph in paragraphs:
            if style == "body":
                wrapped = textwrap.wrap(paragraph, width=58)
                for line in wrapped:
                    lines.append((line, style, vertical_offset))
                    vertical_offset += 34
            else:
                lines.append((paragraph, style, vertical_offset))
                vertical_offset += 72 if style == "title" else 52
            lines.append(("", "space", vertical_offset))
            vertical_offset += 20

        self.story_content_height = vertical_offset
        return lines

    def build_bestiary_entries(self):
        return [
            ("ENEMIES", "Enemy stats are their wave 1 base values. Each later wave adds 18% HP, 10% contact and bullet damage, and 4.5% movement speed per wave."),
            ("Scout - Enemy1", "HP 15 | Speed 2.2 | Contact damage 12 | Size 50. Basic unit. Scouts fire downward with the same 900 ms enemy firing cycle as other non-boss units."),
            ("Assault ship - Enemy2", "HP 22 | Speed 3.8 | Contact damage 18 | Size 50. The fastest regular enemy; track its quick lateral movement and avoid standing below it."),
            ("Heavy ship - Enemy3", "HP 50 | Speed 1.7 | Contact damage 30 | Size 60. Slow but durable, and its collisions hurt more. Prioritize it when it closes in."),
            ("Mini-Guza - MiniBoss", "HP 350 | Speed 2.2 | Contact damage 36 | Size 95. Appears on every third wave unless the Guza boss wave takes priority. It can shoot like regular enemies."),
            ("Guza - GuzaBoss", "HP 2500 | Speed 1.1 | Contact damage 60 | Size 160. Guza does not fire ordinary bullets. About every 9 seconds he marks a random point near the left, center, or right side. After a 1.5 second warning, a 640 x 450 black-hole field stays active for 6 seconds, pulls you toward its center, and deals 18 damage every 0.5 seconds while you overlap it. Dodge as soon as the warning appears: move away from the marked point, then keep moving toward the nearest edge and out of the field. Do not fight against the pull near its center."),
            ("PLAYER SHIPS", "Ship stats are base values. Fire interval is milliseconds; a lower number means faster regular shots. Temporary bonuses and Art's stolen upgrades can change these values."),
            ("VovaShip", "HP 180 | Speed 5 | Strike damage 70 | Cooldown 2 s. Press SPACE for a brief cone attack reaching roughly 300 px upward and 360 px across; it deals double the listed base damage to each enemy hit. Play aggressively near enemy groups. PunchRange bonus widens the strike."),
            ("DanShip", "HP 300 | Speed 2.5 | Damage 4 | Fire interval 80 ms | Bullet range 750. The toughest and slowest ship; hold SPACE to fire paired bolts and use its large health pool to stay in the fight. AttackSpeed bonus makes shots even faster."),
            ("PlatShip", "HP 65 | Speed 8 | Beam damage 50-150. The fastest but most fragile ship. Hold SPACE to charge for up to 3 seconds, then release to fire a vertical beam. Longer charge increases both beam damage and duration; line up enemies before releasing."),
            ("ArtShip", "HP 110 | Speed 5 | Damage 10 | Fire interval 250 ms | Bullet range 550. A flexible regular-shot ship that has room to grow: each defeated enemy gives a 15% chance to steal one available upgrade. Starting caps: +80 HP, +3 speed, +25 damage, 125 ms less fire interval, and +150 range. Each Guza kill as ArtShip raises these caps by +10 HP, +0.5 speed, +3 damage, 15 ms more fire-rate reduction, and +20 range."),
            ("ZahShip", "HP 130 | Speed 5 | Laser damage 15 | Laser cooldown 250 ms | Laser range 900. Aim with the mouse and hold the left button to fire directed lasers. Sweep across enemy groups; LaserBoost increases damage and range."),
            ("TACTICAL NOTES", "Regular enemies move side to side, collide with the player, and send downward bullets. Keep moving to avoid both. Boss and enemy stats scale with the wave, so the values above describe their starting strength rather than a fixed maximum.")
        ]
    def draw_text(self, text, font, color, center):

        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=center)

        shadow = font.render(text, True, (4, 8, 20))
        self.Screen.blit(shadow, text_rect.move(2, 3))
        self.Screen.blit(text_surface, text_rect)

    def draw_panel(self, rect, border_color=None):

        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        panel.fill((*self.colors["panel"], 224))
        self.Screen.blit(panel, rect.topleft)
        pygame.draw.rect(
            self.Screen,
            border_color or (50, 105, 170),
            rect,
            2,
            border_radius=18
        )

    def draw_button(self, rect, text):

        mouse_pos = pygame.mouse.get_pos()

        if rect.collidepoint(mouse_pos):
            color = (44, 130, 205)
        else:
            color = (27, 73, 133)

        pygame.draw.rect(self.Screen, color, rect, border_radius=10)
        pygame.draw.rect(
            self.Screen,
            (70, 220, 255) if rect.collidepoint(mouse_pos) else (75, 145, 210),
            rect,
            2,
            border_radius=10
        )

        self.draw_text(
            text,
            self.small_font,
            self.colors["white"],
            rect.center
        )

    def draw(self):

        if self.current_screen == "menu":
            self.draw_menu()

        elif self.current_screen == "leaderboard":
            self.draw_leaderboard()

        elif self.current_screen == "story":
            self.draw_story()

        elif self.current_screen == "bestiary":
            self.draw_bestiary()

    def draw_menu(self):

        self.Screen.blit(self.menu_background, (0, 0))

        card = pygame.Rect(self.width // 2 - 440, 145, 880, 590)
        self.draw_panel(card, (60, 120, 185))

        self.draw_text(
            "LL UNIVERSE",
            self.title_font,
            self.colors["cyan"],
            (self.width // 2, 82)
        )

        self.draw_text(
            "Enter your nickname:",
            self.small_font,
            self.colors["white"],
            (self.width // 2, 166)
        )

        pygame.draw.rect(
            self.Screen,
            (7, 13, 32),
            self.nickname_box,
            border_radius=10
        )
        pygame.draw.rect(
            self.Screen,
            (70, 145, 205) if self.active_input else (65, 85, 120),
            self.nickname_box,
            2,
            border_radius=10
        )

        self.draw_text(
            self.nickname if self.nickname else "Nickname",
            self.small_font,
            self.colors["white"] if self.nickname else self.colors["gray"],
            self.nickname_box.center
        )

        #Selected ship
        ship_name = self.get_selected_ship()

        self.draw_text(
            "CHOOSE YOUR SHIP",
            self.small_font,
            self.colors["cyan"],
            (self.width // 2, 290)
        )

        self.draw_text(
            ship_name,
            self.font,
            self.colors["white"],
            (self.width // 2, 340)
        )

        if ship_name in self.ship_images:

            ship_image = self.ship_images[ship_name]
            ship_rect = ship_image.get_rect(
                center=(self.width // 2, 475)
            )

            self.Screen.blit(ship_image, ship_rect)

        pygame.draw.circle(
            self.Screen,
            (23, 61, 105),
            (self.width // 2, 465),
            100,
            1
        )

        self.draw_button(self.left_button, "<")
        self.draw_button(self.right_button, ">")

        self.draw_button(self.start_button, "START GAME")
        self.draw_button(self.leaderboard_button, "LEADERBOARD")
        self.draw_button(self.story_button, "STORY")
        self.draw_button(self.bestiary_button, "BESTIARY")
        self.draw_button(self.exit_button, "EXIT")

    def draw_leaderboard(self):

        self.Screen.fill(self.colors["background"])
        self.draw_panel(pygame.Rect(self.width // 2 - 400, 70, 800, 760))

        self.draw_text(
            "LEADERBOARD",
            self.title_font,
            self.colors["white"],
            (self.width // 2, 120)
        )

        self.draw_button(self.back_button, "BACK")

        if not self.leaderboard:
            self.draw_text(
                self.leaderboard_status or "No leaderboard data available.",
                self.small_font,
                self.colors["white"],
                (self.width // 2, 300)
            )

        else:
            for i, player in enumerate(self.leaderboard[:10]):

                nickname = player.get("nickname", "Unknown")
                score = player.get("score", 0)
                ship_name = player.get("ship_name") or "Unknown ship"

                self.draw_text(
                    f"{i + 1}. {nickname} - {score} - {ship_name}",
                    self.small_font,
                    self.colors["white"],
                    (self.width // 2, 230 + i * 45)
                )

    def draw_story(self):

        self.Screen.blit(self.menu_background, (0, 0))

        current_time = pygame.time.get_ticks()
        if self.story_finale_started_at is not None:
            self.draw_story_finale(
                (current_time - self.story_finale_started_at) / 1000
            )
            self.draw_button(self.back_button, "BACK")
            self.draw_text(
                "PRESS ESC TO RETURN",
                self.small_font,
                (160, 195, 225),
                (self.width - 190, 55)
            )
            return

        elapsed = max(0, current_time - self.story_last_update) / 1000
        self.story_last_update = current_time
        self.story_scroll_offset += elapsed * 44

        horizon_y = 105
        visible_height = self.height - horizon_y
        visible_story_lines = []
        for text, style, offset in self.story_lines:
            raw_y = self.height + 50 + offset - self.story_scroll_offset

            if raw_y <= horizon_y or raw_y > self.height + 80:
                continue

            distance = raw_y - horizon_y
            screen_y = horizon_y + (
                distance ** 1.14
                / visible_height ** 0.14
            )
            perspective = min(1.0, distance / visible_height)

            if style == "space":
                continue

            base_size = {
                "title": 46,
                "heading": 32,
                "body": 27
            }[style]
            font_size = max(13, int(base_size * (0.45 + 0.55 * perspective)))
            text_font = pygame.font.SysFont(
                "Arial",
                font_size,
                bold=style != "body"
            )
            color = (255, 225, 135) if style != "body" else (255, 213, 85)
            text_surface = text_font.render(text, True, color)
            text_rect = text_surface.get_rect(center=(self.width // 2, int(screen_y)))

            if text_rect.top < horizon_y:
                continue

            shadow = text_font.render(text, True, (55, 35, 5))
            self.Screen.blit(shadow, text_rect.move(2, 3))
            self.Screen.blit(text_surface, text_rect)
            if (
                text_rect.top > horizon_y
                and text_rect.bottom < self.height - 80
                and any(character.isalpha() for character in text)
            ):
                visible_story_lines.append((text, text_font, text_rect))

        self.draw_story_random_shot(current_time, visible_story_lines)

        if self.story_scroll_offset > self.story_content_height + self.height:
            self.story_finale_started_at = current_time

        self.draw_button(self.back_button, "BACK")
        self.draw_text(
            "PRESS ESC TO RETURN",
            self.small_font,
            (160, 195, 225),
            (self.width - 190, 55)
        )

    def draw_story_random_shot(self, current_time, visible_lines):
        if self.story_active_shot is None and current_time >= self.story_next_shot_at:
            if not visible_lines:
                self.story_next_shot_at = current_time + 500
                return

            text, font, text_rect = random.choice(visible_lines)
            letter_indices = [
                index for index, character in enumerate(text)
                if character.isalpha()
            ]
            letter_index = random.choice(letter_indices)
            letter_x = font.size(text[:letter_index])[0]
            letter_width = font.size(text[letter_index])[0]
            target = (
                text_rect.left + letter_x + letter_width // 2,
                text_rect.centery,
            )
            from_left = random.choice((True, False))
            source_x = -45 if from_left else self.width + 45
            source_y = max(145, min(self.height - 110, target[1] + random.randint(-100, 100)))
            self.story_active_shot = {
                "ship": random.choice(self.ships),
                "source": (source_x, source_y),
                "target": target,
                "scroll_offset": self.story_scroll_offset,
                "started_at": current_time,
            }
            self.story_next_shot_at = current_time + random.randint(3500, 7000)

        shot = self.story_active_shot
        if shot is None:
            return

        elapsed = (current_time - shot["started_at"]) / 1000
        flight_time = 0.72
        source_x, source_y = shot["source"]
        target_x = shot["target"][0]
        scroll_delta = self.story_scroll_offset - shot["scroll_offset"]
        target_y = shot["target"][1] - int(scroll_delta * 1.08)
        target = (target_x, target_y)
        ship_image = self.story_ship_images.get(shot["ship"])

        if elapsed <= flight_time:
            progress = min(1.0, elapsed / flight_time)
            ship_progress = min(1.0, progress * 0.62)
            ship_x = int(source_x + (target_x - source_x) * ship_progress)
            ship_y = int(source_y + (target_y - source_y) * ship_progress)
            if ship_image:
                ship_rect = ship_image.get_rect(center=(ship_x, ship_y))
                self.Screen.blit(ship_image, ship_rect)

            bolt_x = int(source_x + (target_x - source_x) * progress)
            bolt_y = int(source_y + (target_y - source_y) * progress)
            pygame.draw.line(
                self.Screen,
                (75, 205, 255),
                (bolt_x, bolt_y),
                (bolt_x - (target_x - source_x) // 12, bolt_y - (target_y - source_y) // 12),
                4,
            )
            pygame.draw.circle(self.Screen, (225, 250, 255), (bolt_x, bolt_y), 5)
        elif elapsed <= flight_time + 0.24:
            impact_age = elapsed - flight_time
            pygame.draw.circle(
                self.Screen,
                (255, 210, 95),
                target,
                5 + int(impact_age * 70),
                3,
            )
            pygame.draw.circle(self.Screen, (255, 245, 195), target, 4)
        else:
            self.story_active_shot = None

    def draw_story_finale(self, elapsed):
        """Play a short hidden scene where the player ships destroy the credits."""
        center_x = self.width // 2
        credits_y = self.height // 2 - 80
        word = "CREDITS"
        credits_font = pygame.font.SysFont("Arial", 68, bold=True)
        letter_widths = [credits_font.size(letter)[0] for letter in word]
        word_width = sum(letter_widths) + 8 * (len(word) - 1)
        letter_x = center_x - word_width // 2

        ships = self.ships
        impact_times = sorted(
            0.45 + ship_index * 0.24 + volley * 1.25 + 0.8
            for volley in range(2)
            for ship_index in range(len(ships))
        )
        hit_count = sum(impact_time <= elapsed for impact_time in impact_times)

        self.draw_text(
            "A SECRET MESSAGE FROM THE PILOTS",
            self.small_font,
            self.colors["cyan"],
            (center_x, credits_y - 90)
        )

        # Each hit breaks one letter away from the credits title.
        x = letter_x
        for letter_index, (letter, width) in enumerate(zip(word, letter_widths)):
            intact_surface = credits_font.render(letter, True, (255, 225, 135))
            impact_time = impact_times[letter_index]
            if elapsed < impact_time:
                self.Screen.blit(intact_surface, (x, credits_y))
            else:
                fragment_age = elapsed - impact_time
                if fragment_age < 0.9:
                    fragment = credits_font.render(letter, True, (255, 130, 65))
                    fragment.set_alpha(max(0, int(255 * (1 - fragment_age / 0.9))))
                    direction = -1 if letter_index % 2 else 1
                    self.Screen.blit(
                        fragment,
                        (
                            x + direction * int(fragment_age * 105),
                            credits_y - int(fragment_age * 150),
                        ),
                    )
            x += width + 8

        ship_y = self.height - 155
        target = (center_x, credits_y + 45)
        travel_time = 0.8
        for ship_index, ship_name in enumerate(ships):
            ship_x = int(self.width * (ship_index + 1) / (len(ships) + 1))
            ship_image = self.story_ship_images.get(ship_name)
            if ship_image:
                bob = int(math.sin(elapsed * 3 + ship_index) * 5)
                ship_rect = ship_image.get_rect(
                    center=(ship_x, ship_y + bob)
                )
                self.Screen.blit(ship_image, ship_rect)

            for volley in range(2):
                fire_time = 0.45 + ship_index * 0.24 + volley * 1.25
                shot_age = elapsed - fire_time
                if 0 <= shot_age <= travel_time:
                    progress = shot_age / travel_time
                    shot_x = int(ship_x + (target[0] - ship_x) * progress)
                    shot_y = int(ship_y - 30 + (target[1] - (ship_y - 30)) * progress)
                    pygame.draw.line(
                        self.Screen,
                        (70, 210, 255),
                        (shot_x, shot_y + 22),
                        (shot_x, shot_y - 16),
                        4,
                    )
                    pygame.draw.circle(self.Screen, (205, 250, 255), (shot_x, shot_y - 18), 5)

        # A brief flash marks each hit on the scrolling credits.
        for impact_time in impact_times:
            impact_age = elapsed - impact_time
            if 0 <= impact_age < 0.22:
                radius = 8 + int(impact_age * 100)
                pygame.draw.circle(
                    self.Screen,
                    (255, 185, 80),
                    target,
                    radius,
                    3,
                )

        if hit_count >= len(word) and elapsed > impact_times[-1] + 1.1:
            self.draw_text(
                "THE END",
                self.title_font,
                self.colors["cyan"],
                (center_x, credits_y + 20)
            )

    def draw_bestiary(self):
        self.Screen.blit(self.menu_background, (0, 0))
        self.draw_panel(pygame.Rect(48, 105, self.width - 96, self.height - 155))
        self.draw_text(
            "BESTIARY",
            self.title_font,
            self.colors["cyan"],
            (self.width // 2, 56)
        )
        self.draw_button(self.back_button, "BACK")
        self.draw_text(
            "SCROLL TO READ  |  ESC TO RETURN",
            self.small_font,
            (160, 195, 225),
            (self.width - 235, 55)
        )

        viewport = pygame.Rect(76, 125, self.width - 152, self.height - 205)
        self.Screen.set_clip(viewport)
        y = viewport.y + 8 - self.bestiary_scroll_offset
        for heading, description in self.bestiary_entries:
            row_top = y
            sprite_name = self.bestiary_sprite_keys.get(heading)
            if heading in self.ships:
                sprite_name = heading
            sprite = self.bestiary_images.get(sprite_name)

            if sprite:
                self.Screen.blit(sprite, (viewport.x + 12, int(row_top)))
                text_x = viewport.x + 100
                body_x = text_x
                wrap_width = 100
            else:
                text_x = viewport.x + 12
                body_x = viewport.x + 28
                wrap_width = 116

            heading_font = pygame.font.SysFont("Arial", 25, bold=True)
            heading_surface = heading_font.render(heading, True, (100, 220, 255))
            if viewport.top - 40 <= row_top <= viewport.bottom:
                self.Screen.blit(heading_surface, (text_x, int(row_top)))

            body_font = pygame.font.SysFont("Arial", 18)
            wrapped_lines = textwrap.wrap(description, width=wrap_width)
            body_y = row_top + 34
            for line in wrapped_lines:
                if viewport.top - 24 <= body_y <= viewport.bottom:
                    body_surface = body_font.render(line, True, (225, 233, 248))
                    self.Screen.blit(body_surface, (body_x, int(body_y)))
                body_y += 24

            row_height = max(72 if sprite else 0, 34 + len(wrapped_lines) * 24)
            y = row_top + row_height + 17

        self.bestiary_content_height = y - viewport.y + self.bestiary_scroll_offset
        self.bestiary_max_scroll = max(
            0,
            self.bestiary_content_height - viewport.height + 16
        )
        self.bestiary_scroll_offset = min(
            self.bestiary_scroll_offset,
            self.bestiary_max_scroll
        )
        self.Screen.set_clip(None)

    def handle_bestiary_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.current_screen = "menu"
            elif event.key == pygame.K_DOWN:
                self.bestiary_scroll_offset += 60
            elif event.key == pygame.K_UP:
                self.bestiary_scroll_offset = max(
                    0,
                    self.bestiary_scroll_offset - 60
                )
            elif event.key == pygame.K_PAGEDOWN:
                self.bestiary_scroll_offset += self.height - 180
            elif event.key == pygame.K_PAGEUP:
                self.bestiary_scroll_offset = max(
                    0,
                    self.bestiary_scroll_offset - (self.height - 180)
                )
        elif event.type == pygame.MOUSEWHEEL:
            self.bestiary_scroll_offset -= event.y * 48
        elif (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.back_button.collidepoint(event.pos)
        ):
            self.current_screen = "menu"

        self.bestiary_scroll_offset = max(
            0,
            min(
                self.bestiary_scroll_offset,
                getattr(self, "bestiary_max_scroll", 10000)
            )
        )
    def handle_event(self, event):

        if event.type == pygame.QUIT:
            self.quit_requested = True

        if self.current_screen == "menu":
            self.handle_menu_event(event)

        elif self.current_screen == "leaderboard":
            self.handle_leaderboard_event(event)

        elif self.current_screen == "story":
            self.handle_story_event(event)

        elif self.current_screen == "bestiary":
            self.handle_bestiary_event(event)

    def load_leaderboard(self):
        try:
            response = self.network.send_request("/leaderboard", "GET")
            if response is None:
                self.leaderboard = []
                self.leaderboard_status = "Server unavailable. Start star_server.bat and try again."
            else:
                self.leaderboard = response.get("leaderboard", [])
                self.leaderboard_status = (
                    "No leaderboard data available."
                    if not self.leaderboard
                    else ""
                )
        except Exception as error:
            print(f"Could not load leaderboard: {error}")
            self.leaderboard = []
            self.leaderboard_status = "Could not load leaderboard. Try again."
        finally:
            self.leaderboard_loading = False

    def handle_menu_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            if self.nickname_box.collidepoint(event.pos):
                self.active_input = True

            else:
                self.active_input = False

            if self.start_button.collidepoint(event.pos):

                if not self.nickname.strip():
                    print("Enter your nickname first.")
                    return

                #Register player
                if self.network.register_player(self.nickname.strip()):
                    self.start_requested = True

                else:
                    print("Could not register player.")

            elif self.leaderboard_button.collidepoint(event.pos):

                self.leaderboard = []
                self.leaderboard_loading = True
                self.leaderboard_status = "Loading leaderboard..."
                self.current_screen = "leaderboard"
                threading.Thread(
                    target=self.load_leaderboard,
                    daemon=True,
                ).start()

            elif self.story_button.collidepoint(event.pos):
                self.current_screen = "story"
                self.story_scroll_offset = 0.0
                self.story_last_update = pygame.time.get_ticks()
                self.story_finale_started_at = None
                self.story_active_shot = None
                self.story_next_shot_at = self.story_last_update + random.randint(2500, 5000)

            elif self.bestiary_button.collidepoint(event.pos):
                self.current_screen = "bestiary"
                self.bestiary_scroll_offset = 0.0

            elif self.exit_button.collidepoint(event.pos):
                self.quit_requested = True

            elif self.left_button.collidepoint(event.pos):
                self.selected_ship = max(
                    1,
                    self.selected_ship - 1
                )

            elif self.right_button.collidepoint(event.pos):
                self.selected_ship = min(
                    len(self.ships),
                    self.selected_ship + 1
                )

        if event.type == pygame.KEYDOWN and self.active_input:

            if event.key == pygame.K_BACKSPACE:
                self.nickname = self.nickname[:-1]

            elif event.key == pygame.K_RETURN:
                self.active_input = False

            elif len(self.nickname) < 16 and event.unicode.isprintable():
                self.nickname += event.unicode

    def handle_leaderboard_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            if self.back_button.collidepoint(event.pos):
                self.current_screen = "menu"

    def handle_story_event(self, event):

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.current_screen = "menu"

        elif (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.back_button.collidepoint(event.pos)
        ):
            self.current_screen = "menu"

    def reset_start_request(self):
        self.start_requested = False

    def submit_score(self, score, ship_name=None):
        return self.network.submit_score(score, ship_name)
