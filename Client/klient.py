
import pygame
import json
import urllib.request
import urllib.error
import os
import textwrap


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
        self.start_button = pygame.Rect(center_x - 420, 690, 190, 62)
        self.leaderboard_button = pygame.Rect(center_x - 210, 690, 190, 62)
        self.credits_button = pygame.Rect(center_x, 690, 190, 62)
        self.exit_button = pygame.Rect(center_x + 210, 690, 190, 62)

        self.nickname_box = pygame.Rect(center_x - 190, 190, 380, 54)

        self.left_button = pygame.Rect(center_x - 180, 455, 64, 56)
        self.right_button = pygame.Rect(center_x + 116, 455, 64, 56)

        self.back_button = pygame.Rect(30, 30, 150, 50)
        self.credits_scroll_offset = 0.0
        self.credits_last_update = pygame.time.get_ticks()
        self.credits_lines = self.build_credits_lines()

    #Get selected ship name
    def get_selected_ship(self):

        return self.ships[self.selected_ship - 1]

    def build_credits_lines(self):

        paragraphs = [
            ("title", "LL UNIVERSE!"),
            ("heading", "KARŠ PAR PĒDĒJO GALAKTIKU"),
            ("heading", "PROLOGS: REPUBLIKAS KRIŠANA"),
            ("body", "Sen senos laikos, tālā galaktikā, pastāvēja Lielā LL Republika. Tās planētas plauka, tehnoloģijas attīstījās, bet kosmiskos tirdzniecības ceļus aizsargāja elitāra pilotu vienība — Leģendārais četrinieks."),
            ("body", "Taču miers nevarēja pastāvēt mūžīgi."),
            ("body", "No nezināmām kosmosa dzīlēm parādījās nežēlīga un noslēpumaina civilizācija — Čučmeki. Sava valdnieka, Lielā Čučmeka Gūzas, vadībā viņi sāka iekarot planētas, iznīcināt stacijas un pārvērst veselas zvaigžņu sistēmas drupās."),
            ("body", "Viņu armija bija neskaitāma. Viņu tehnoloģijas — neparedzamas. Viņu vienīgais mērķis — pakļaut sev visu galaktiku."),
            ("body", "Kad Republikas galvaspilsēta krita, Pēdējās cerības padome sapulcināja atlikušos varoņus un nodeva viņiem senus kaujas kuģus."),
            ("body", "Tā sākās pēdējais karš par brīvību."),
            ("heading", "GALVENIE VAROŅI"),
            ("heading", "VOVASHIP — REPUBLIKAS DŪRE"),
            ("body", "Pilots: Vova. Cīņas stils: postošs trieciens."),
            ("body", "Vova ir viens no bīstamākajiem Republikas pilotiem. Viņa kuģis ir aprīkots ar eksperimentālu enerģijas trieciena sistēmu, kas ar vienu šāvienu spēj iznīcināt veselas pretinieku grupas."),
            ("body", "Viņam nepatīk ieilgušas kaujas. Viņa filozofija ir vienkārša: ja ienaidnieks vēl spēj kustēties, trieciens nebija pietiekami spēcīgs."),
            ("heading", "DANSHIP — DZELZS CIETOKSNIS"),
            ("body", "Pilots: Dans. Cīņas stils: aizsardzība un nepārtraukta uguns."),
            ("body", "Dans vada smagu kuģi, kas radīts, lai izdzīvotu pat bezcerīgākajās kaujās. Tā bruņas ir izturējušas uzbrukumus, kas iznīcinātu parastu iznīcinātāju."),
            ("body", "Viņš nav pats ātrākais, taču, tiklīdz Dans parādās kaujas laukā, Čučmeki saprot, ka vieglas uzvaras nebūs."),
            ("heading", "PLATSHIP — PĒDĒJAIS STARS"),
            ("body", "Pilots: Plats. Cīņas stils: uzlādējams enerģijas stars."),
            ("body", "PlatShip izmanto senu tehnoloģiju, kas atrasta aizmirstas civilizācijas drupās. Tā ierocis spēj koncentrēt zvaigznes enerģiju vienā iznīcinošā starā."),
            ("body", "Lai sasniegtu maksimālo jaudu, ierocis ir jāuzlādē. Tāpēc Plats gaida īsto brīdi, pirms noslauka pretinieku no galaktikas kartes."),
            ("heading", "ARTSHIP — TEHNOLOĢIJU APRĪTĀJS"),
            ("body", "Pilots: Arts. Cīņas stils: pielāgošanās un attīstība."),
            ("body", "Arts ir īsts murgs Čučmekiem. Viņa kuģim ir tehnoloģiju absorbcijas sistēma: katrs iznīcinātais pretinieks ļauj izanalizēt tā tehnoloģijas un uzlabot paša kuģa īpašības."),
            ("body", "Jo ilgāk turpinās kauja, jo bīstamāks kļūst ArtShip. Runā, ka kādu dienu tas pārspēs pat paša Gūzas tehnoloģijas."),
            ("heading", "ZAHSHIP — ATRIEBĪBAS ACS"),
            ("body", "Pilots: Zahs. Cīņas stils: manuāla lāzera tēmēšana."),
            ("body", "ZahShip ir jaunas paaudzes eksperimentāls kuģis. Atšķirībā no citiem iznīcinātājiem tas izmanto tiešas lāzera tēmēšanas sistēmu, kas ļauj pilotam pašam izvēlēties mērķi."),
            ("body", "Tā ierocim nav vajadzīgi parastie lādiņi. Viens precīzs stars spēj caururbt pat vissmagāko Čučmeku kuģu aizsardzību."),
            ("body", "Zahs nepaļaujas uz nejaušību. Viņš pats izvēlas, kurš nākamais pazudīs kosmosa tukšumā."),
            ("heading", "ČUČMEKU ARMIJA"),
            ("body", "Čučmeki ir agresīva kosmosa civilizācija, kas pazīstama ar savu skaitlisko pārsvaru un nežēlību. Viņu flotē ir vairāku klašu kaujas vienības."),
            ("body", "Čučmeku izlūks — ātrs iznīcinātājs ar nelielu izturību."),
            ("body", "Čučmeku trieciennieks — jaudīgāks kuģis, kas spēj nodarīt ievērojamus bojājumus."),
            ("body", "Čučmeku smagsvars — lēns, bet ārkārtīgi izturīgs kuģis ar spēcīgu bruņojumu."),
            ("body", "Mini-Gūza — nelielas Čučmeku vienības komandieris ar milzīgu izturību."),
            ("body", "Lielais Gūza — Čučmeku Impērijas augstākais valdnieks un galaktikas galvenais pretinieks."),
            ("heading", "LIELAIS GŪZA — ČUČMEKU IMPĒRIJAS IMPERATORS"),
            ("body", "Gūza nav parasts kosmosa tirāns. Viņš ir sena būtne, kas pārdzīvojusi vairāku galaktisku civilizāciju krišanu."),
            ("body", "Viņa kuģis ir tik milzīgs, ka spēj aizsegt veselas zvaigžņu sistēmas."),
            ("body", "Taču Gūzas baisākā īpašība ir viņa slepenais ierocis — Melnais caurums."),
            ("body", "Kaujas laikā viņš atver telpas anomāliju, kas sāk ievilkt visu sev apkārt. Neviens kuģis nespēj bezgalīgi pretoties tās gravitācijai."),
            ("body", "Leģenda vēsta, ka Gūza ieguva šo spēku, noslēdzot darījumu ar senu būtni, kas mīt ārpus zināmā Visuma."),
            ("heading", "KARA HRONOLOĢIJA"),
            ("heading", "I SĒRIJA — IEBRUKUMA SĀKUMS"),
            ("body", "Čučmeki uzbrūk attālām Republikas planētām. Varoņi saņem pavēli iznīcināt pirmos iebrucēju viļņus."),
            ("heading", "II SĒRIJA — PRIEKŠPOSTEŅU KRIŠANA"),
            ("body", "Čučmeku Impērija pastiprina spiedienu. Kaujas laukā parādās smagie kuģi un pirmie komandieri."),
            ("heading", "III SĒRIJA — MINI-GŪZAS ATGRIEŠANĀS"),
            ("body", "Čučmeki sūta elitārus komandierus, lai apturētu varoņu virzību."),
            ("heading", "IV SĒRIJA — LIELAIS PĀRGĀJIENS"),
            ("body", "Varoņi tuvojas Impērijas teritorijai. Ar katru jaunu kauju Čučmeku armija kļūst spēcīgāka."),
            ("heading", "V SĒRIJA — IMPERATORA DUSMAS"),
            ("body", "Lielais Gūza pats dodas kaujā. Viņa kuģis izmanto ieroci, kas spēj radīt Melnos caurumus."),
            ("heading", "VI SĒRIJA — PĒDĒJĀ CERĪBA"),
            ("body", "Pieci varoņi apvieno spēkus pēdējā kaujā. Visas galaktikas liktenis ir atkarīgs no tā, vai viņiem izdosies iznīcināt Lielo Gūzu.")
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

        self.credits_content_height = vertical_offset
        return lines

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

        elif self.current_screen == "credits":
            self.draw_credits()

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
        self.draw_button(self.credits_button, "CREDITS")
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

    def draw_credits(self):

        self.Screen.blit(self.menu_background, (0, 0))

        current_time = pygame.time.get_ticks()
        elapsed = max(0, current_time - self.credits_last_update) / 1000
        self.credits_last_update = current_time
        self.credits_scroll_offset += elapsed * 44

        horizon_y = 105
        visible_height = self.height - horizon_y
        for text, style, offset in self.credits_lines:
            raw_y = self.height + 50 + offset - self.credits_scroll_offset

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

        if self.credits_scroll_offset > self.credits_content_height + self.height:
            self.draw_text(
                "THE END",
                self.font,
                self.colors["cyan"],
                (self.width // 2, self.height - 100)
            )

        self.draw_button(self.back_button, "BACK")
        self.draw_text(
            "PRESS ESC TO RETURN",
            self.small_font,
            (160, 195, 225),
            (self.width - 190, 55)
        )

    def handle_event(self, event):

        if event.type == pygame.QUIT:
            self.quit_requested = True

        if self.current_screen == "menu":
            self.handle_menu_event(event)

        elif self.current_screen == "leaderboard":
            self.handle_leaderboard_event(event)

        elif self.current_screen == "credits":
            self.handle_credits_event(event)

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

            elif self.credits_button.collidepoint(event.pos):
                self.current_screen = "credits"
                self.credits_scroll_offset = 0.0
                self.credits_last_update = pygame.time.get_ticks()

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

    def handle_credits_event(self, event):

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

    def submit_score(self, score):
        return self.network.submit_score(score)
