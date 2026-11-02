
import pygame
import json
import urllib.request
import urllib.error


class GameClient:

    def __init__(self, server_url="http://127.0.0.1:8000"):

        self.server_url = server_url
        self.player_id = None
        self.nickname = None

    #Send request to server
    def send_request(self, endpoint, method="GET", data=None):

        url = self.server_url + endpoint

        headers = {
            "Content-Type": "application/json"
        }

        body = None

        if data is not None:
            body = json.dumps(data).encode("utf-8")

        request = urllib.request.Request(
            url,
            data=body,
            headers=headers,
            method=method
        )

        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return json.loads(response.read().decode("utf-8"))

        except urllib.error.URLError:
            print("Cannot connect to server.")
            return None

        except json.JSONDecodeError:
            print("Invalid server response.")
            return None

    #Register player
    def register_player(self, nickname):

        data = {"nickname": nickname}
        response = self.send_request("/players/register", "POST", data)

        if response:
            self.player_id = response.get("player_id")
            self.nickname = nickname
            return True

        return False

    #Submit player score
    def submit_score(self, score):

        if self.player_id is None:
            print("Player is not registered.")
            return False

        data = {
            "player_id": self.player_id,
            "score": score
        }

        response = self.send_request("/scores", "POST", data)
        return response is not None

    #Get leaderboard
    def get_leaderboard(self):

        response = self.send_request("/leaderboard", "GET")

        if response:
            return response.get("leaderboard", [])

        return []


class klient:

    def __init__(self, Screen):

        self.Screen = Screen
        self.width, self.height = Screen.get_size()

        self.network = GameClient()

        self.font = pygame.font.SysFont("Arial", 32)
        self.small_font = pygame.font.SysFont("Arial", 22)
        self.title_font = pygame.font.SysFont("Arial", 65, bold=True)

        self.nickname = ""
        self.selected_ship = 1

        self.active_input = False
        self.current_screen = "menu"

        self.start_requested = False
        self.quit_requested = False

        self.leaderboard = []

        self.colors = {
            "background": (10, 12, 30),
            "white": (240, 240, 255),
            "blue": (40, 100, 220),
            "light_blue": (70, 150, 255),
            "gray": (80, 85, 110),
            "red": (200, 60, 60)
        }

        self.start_button = pygame.Rect(350, 350, 300, 65)
        self.leaderboard_button = pygame.Rect(350, 440, 300, 65)
        self.exit_button = pygame.Rect(350, 530, 300, 65)

        self.nickname_box = pygame.Rect(350, 250, 300, 50)

        self.left_button = pygame.Rect(350, 610, 60, 50)
        self.right_button = pygame.Rect(590, 610, 60, 50)

        self.back_button = pygame.Rect(30, 30, 150, 50)

    def draw_text(self, text, font, color, center):

        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=center)

        self.Screen.blit(text_surface, text_rect)

    def draw_button(self, rect, text):

        mouse_pos = pygame.mouse.get_pos()

        if rect.collidepoint(mouse_pos):
            color = self.colors["light_blue"]
        else:
            color = self.colors["blue"]

        pygame.draw.rect(self.Screen, color, rect, border_radius=10)

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

    def draw_menu(self):

        self.Screen.fill(self.colors["background"])

        self.draw_text(
            "LL UNIVERSE",
            self.title_font,
            self.colors["white"],
            (self.width // 2, 120)
        )

        self.draw_text(
            "Enter your nickname:",
            self.small_font,
            self.colors["white"],
            (self.width // 2, 220)
        )

        pygame.draw.rect(
            self.Screen,
            self.colors["white"],
            self.nickname_box,
            2,
            border_radius=8
        )

        self.draw_text(
            self.nickname if self.nickname else "Nickname",
            self.small_font,
            self.colors["white"] if self.nickname else self.colors["gray"],
            self.nickname_box.center
        )

        self.draw_button(self.start_button, "START GAME")
        self.draw_button(self.leaderboard_button, "LEADERBOARD")
        self.draw_button(self.exit_button, "EXIT")

        self.draw_text(
            f"Selected ship: {self.selected_ship}",
            self.small_font,
            self.colors["white"],
            (self.width // 2, 590)
        )

        self.draw_button(self.left_button, "<")
        self.draw_button(self.right_button, ">")

    def draw_leaderboard(self):

        self.Screen.fill(self.colors["background"])

        self.draw_text(
            "LEADERBOARD",
            self.title_font,
            self.colors["white"],
            (self.width // 2, 120)
        )

        self.draw_button(self.back_button, "BACK")

        if not self.leaderboard:
            self.draw_text(
                "No leaderboard data available.",
                self.small_font,
                self.colors["white"],
                (self.width // 2, 300)
            )

        else:
            for i, player in enumerate(self.leaderboard[:10]):

                nickname = player.get("nickname", "Unknown")
                score = player.get("score", 0)

                self.draw_text(
                    f"{i + 1}. {nickname} - {score}",
                    self.small_font,
                    self.colors["white"],
                    (self.width // 2, 230 + i * 45)
                )

    def handle_event(self, event):

        if event.type == pygame.QUIT:
            self.quit_requested = True

        if self.current_screen == "menu":
            self.handle_menu_event(event)

        elif self.current_screen == "leaderboard":
            self.handle_leaderboard_event(event)

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

                self.leaderboard = self.network.get_leaderboard()
                self.current_screen = "leaderboard"

            elif self.exit_button.collidepoint(event.pos):
                self.quit_requested = True

            elif self.left_button.collidepoint(event.pos):
                self.selected_ship = max(1, self.selected_ship - 1)

            elif self.right_button.collidepoint(event.pos):
                self.selected_ship = min(3, self.selected_ship + 1)

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

    def reset_start_request(self):
        self.start_requested = False

    def submit_score(self, score):
        return self.network.submit_score(score)
