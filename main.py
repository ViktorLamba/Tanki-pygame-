import pygame
import sys
import os
from core.multiplayer import Client, Server
from core.game import Game, MultiplayerGame
import threading


# Основные цвета
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
LIGHT_GRAY = (100, 100, 100)

# Размер окна
WIDTH, HEIGHT = 800, 600


class Button:
    def __init__(self, text, x, y, w, h, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.color = GRAY
        self.hover_color = LIGHT_GRAY
        self.font = pygame.font.SysFont("arial", 30)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        

        # Основные кнопки
        self.buttons = [
            Button("Одиночная игра", 300, 150, 235, 50, self.start_singleplayer),
            Button("Мультиплеер", 300, 250, 235, 50, self.show_multiplayer_menu),
            Button("Настройки", 300, 350, 235, 50, self.show_settings)
        ]

        # Кнопки мультиплеера
        self.multiplayer_buttons = [
            Button("Создать мир", 300, 200, 200, 50, self.create_world),
            Button("Подключиться", 300, 300, 200, 50, self.join_world),
            Button("Назад", 300, 400, 200, 50, self.show_main_menu)
        ]

        # Фон меню
        self.background = pygame.image.load("assets/images/menu_bg.png").convert()
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))

        self.current_buttons = self.buttons

    def start_singleplayer(self):
        game = Game()
        game.run()

    def show_multiplayer_menu(self):
        self.current_buttons = self.multiplayer_buttons

    def show_main_menu(self):
        self.current_buttons = self.buttons

    def show_settings(self):
        # файл настроек рядом с main.py
        settings_path = os.path.join(os.path.dirname(__file__), 'settings.py')
        settings_path = os.path.normpath(settings_path)

        # пресеты разрешений
        presets = [
            (800, 600),
            (1024, 768),
            (1280, 720),
            (1366, 768),
            (1600, 900),
            (1920, 1080),
        ]

        # сложности (скорость танка)
        difficulties = [
            ("Easy", 5),
            ("Normal", 3),
            ("Hard", 1),
        ]

        # темы карт
        map_themes = ["summer", "winter", "desert"]

        # текущие значения
        try:
            import settings as game_settings_local
        except Exception:
            from core import game as game_settings_local  # fallback

        cur_w, cur_h = getattr(game_settings_local, 'WIDTH', WIDTH), getattr(game_settings_local, 'HEIGHT', HEIGHT)
        try:
            preset_index = presets.index((cur_w, cur_h))
        except ValueError:
            preset_index = 0

        cur_speed = getattr(game_settings_local, 'TANK_SPEED', 3)
        diff_index = 1
        for i, (_, sp) in enumerate(difficulties):
            if sp == cur_speed:
                diff_index = i
                break

        cur_map_theme = getattr(game_settings_local, 'CURRENT_MAP_THEME', 'summer')
        try:
            map_index = map_themes.index(cur_map_theme)
        except ValueError:
            map_index = 0

        font = pygame.font.SysFont("arial", 28)
        small = pygame.font.SysFont("arial", 22)

        running = True
        while running:
            self.screen.fill((30, 30, 30))

            title = font.render("Settings", True, (255, 255, 255))
            self.screen.blit(title, (40, 20))

            # Сложность
            screen_w, screen_h = self.screen.get_size()
            center_x = screen_w // 2
            d_y = int(screen_h * 0.18)
            selector_width = 320
            d_x = center_x - selector_width // 2
            d_label = small.render("Сложность", True, (200, 200, 200))
            d_label_rect = d_label.get_rect(center=(center_x, d_y - 20))
            self.screen.blit(d_label, d_label_rect.topleft)

            d_left = pygame.Rect(d_x, d_y, 40, 40)
            d_right = pygame.Rect(d_x + selector_width - 40, d_y, 40, 40)
            pygame.draw.rect(self.screen, (120, 120, 120), d_left)
            pygame.draw.rect(self.screen, (120, 120, 120), d_right)
            self.screen.blit(small.render("<", True, (255, 255, 255)), (d_left.x + 10,
                                d_left.y + 6))
            self.screen.blit(small.render(">", True, (255, 255, 255)), (d_right.x + 10,
                                d_right.y + 6))

            # распределяем варианты сложности равномерно по ширине селектора
            for i, (name, _) in enumerate(difficulties):
                text_surf = small.render(name, True, (255, 255, 0) if i == diff_index else (200,
                                                                                              200,
                                                                                              200))
                pos_x = d_x + int(selector_width * (i + 1) / (len(difficulties) + 1))
                self.screen.blit(text_surf, (pos_x - text_surf.get_width() // 2,
                                             d_y + 8))

            # Разрешение экрана
            r_y = d_y + 160
            r_selector_width = 360
            r_x = center_x - r_selector_width // 2

            r_label = small.render("Разрешение экрана", True, (200, 200, 200))
            r_label_rect = r_label.get_rect(center=(center_x, r_y - 20))
            self.screen.blit(r_label, r_label_rect.topleft)

            r_left = pygame.Rect(r_x, r_y, 40, 40)
            r_right = pygame.Rect(r_x + r_selector_width - 40, r_y, 40, 40)
            pygame.draw.rect(self.screen, (120, 120, 120), r_left)
            pygame.draw.rect(self.screen, (120, 120, 120), r_right)
            self.screen.blit(small.render("<", True, (255, 255, 255)), (r_left.x + 10, r_left.y + 6))
            self.screen.blit(small.render(">", True, (255, 255, 255)), (r_right.x + 10, r_right.y + 6))

            res_text = f"{presets[preset_index][0]} x {presets[preset_index][1]}"
            res_surf = small.render(res_text, True, (255, 255, 0))
            res_rect = res_surf.get_rect(center=(center_x, r_y + 14))
            self.screen.blit(res_surf, res_rect.topleft)

            # Выбор карты
            m_y = r_y + 160
            m_selector_width = 250
            m_x = center_x - m_selector_width // 2

            m_label = small.render("Карта", True, (200, 200, 200))
            m_label_rect = m_label.get_rect(center=(center_x, m_y - 20))
            self.screen.blit(m_label, m_label_rect.topleft)

            m_left = pygame.Rect(m_x, m_y, 40, 40)
            m_right = pygame.Rect(m_x + m_selector_width - 40, m_y, 40, 40)
            pygame.draw.rect(self.screen, (120, 120, 120), m_left)
            pygame.draw.rect(self.screen, (120, 120, 120), m_right)
            self.screen.blit(small.render("<", True, (255, 255, 255)), (m_left.x + 10, m_left.y + 6))
            self.screen.blit(small.render(">", True, (255, 255, 255)), (m_right.x + 10, m_right.y + 6))

            map_text = map_themes[map_index]
            map_surf = small.render(map_text, True, (255, 255, 0))
            map_rect = map_surf.get_rect(center=(center_x, m_y + 14))
            self.screen.blit(map_surf, map_rect.topleft)

            # Сохранить и Отмена кнопки
            buttons_left = center_x - 130
            save_rect = pygame.Rect(buttons_left, m_y + 100, 120, 40)
            cancel_rect = pygame.Rect(buttons_left + 140, m_y + 100, 120, 40)
            pygame.draw.rect(self.screen, (50, 150, 50), save_rect)
            pygame.draw.rect(self.screen, (150, 50, 50), cancel_rect)
            self.screen.blit(small.render("Save", True, (255, 255, 255)), (save_rect.x + 30, save_rect.y + 8))
            self.screen.blit(small.render("Cancel", True, (255, 255, 255)), (cancel_rect.x + 24, cancel_rect.y + 8))

            pygame.display.flip()
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        diff_index = max(0, diff_index - 1)
                    elif event.key == pygame.K_RIGHT:
                        diff_index = min(len(difficulties) - 1, diff_index + 1)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = event.pos
                    if d_left.collidepoint(pos):
                        diff_index = max(0, diff_index - 1)
                    if d_right.collidepoint(pos):
                        diff_index = min(len(difficulties) - 1, diff_index + 1)
                    if r_left.collidepoint(pos):
                        preset_index = max(0, preset_index - 1)
                    if r_right.collidepoint(pos):
                        preset_index = min(len(presets) - 1, preset_index + 1)
                    if m_left.collidepoint(pos):
                        map_index = max(0, map_index - 1)
                    if m_right.collidepoint(pos):
                        map_index = min(len(map_themes) - 1, map_index + 1)
                    if save_rect.collidepoint(pos):
                        new_w, new_h = presets[preset_index]
                        new_speed = difficulties[diff_index][1]
                        new_map = map_themes[map_index]
                        try:
                            content = (
                                f"WIDTH = {new_w}\n"
                                f"HEIGHT = {new_h}\n"
                                f"FPS = {getattr(game_settings_local, 'FPS', 60)}\n"
                                f"TANK_SPEED = {new_speed}\n"
                                f"BULLET_SPEED = {getattr(game_settings_local, 'BULLET_SPEED', 7)}\n"
                                f"TANK_HP = {getattr(game_settings_local, 'TANK_HP', 100)}\n"
                                f"CURRENT_MAP_THEME = \"{new_map}\"\n"
                            )
                            with open(settings_path, 'w') as f:
                                f.write(content)
                            # reload глобального модуля настроек если он импортирован
                            try:
                                import importlib, settings as s_mod
                                importlib.reload(s_mod)
                            except Exception:
                                pass
                            # обновляем экран и фон меню
                            self.screen = pygame.display.set_mode((new_w, new_h))
                            try:
                                bg = pygame.image.load("assets/images/menu_bg.png").convert()
                                self.background = pygame.transform.scale(bg, (new_w, new_h))
                            except Exception:
                                self.background = pygame.Surface((new_w, new_h))
                                self.background.fill((20, 20, 20))
                        except Exception as e:
                            print("Error saving settings:", e)
                        running = False
                    if cancel_rect.collidepoint(pos):
                        running = False

    def create_world(self):
        self.server = Server()
        threading.Thread(target=self.server.start, daemon=True).start()

        self.game = MultiplayerGame(is_host=True, server=self.server)
        self.game.run()

    def join_world(self):
        host_ip = self.enter_host_ip()
        try:
            self.client = Client(host_ip)
        except ConnectionRefusedError:
            print("Не удалось подключиться к серверу")
            return
        # Клиент сам запускает свой receive-loop в __init__, дополнительный
        # поток здесь не нужен и вызывает гонки при чтении сокета.

        self.game = MultiplayerGame(is_host=False, client=self.client)
        self.game.run()

    def run_multiplayer_game(self):
        running = True
        font = pygame.font.SysFont("arial", 24)
        input_text = ""

        while running:
            self.screen.fill((0, 0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if input_text.strip() != "":
                            self.client.client.send(input_text.encode())
                            input_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode

            text_surf = font.render("Мультиплеерный чат", True, (255, 255, 255))
            self.screen.blit(text_surf, (50, 50))

            input_surf = font.render("> " + input_text, True, (255, 255, 0))
            self.screen.blit(input_surf, (50, HEIGHT - 50))

            pygame.display.flip()
            self.clock.tick(60)

    def enter_host_ip(self):
        font = pygame.font.SysFont("arial", 30)
        input_text = ""
        entering = True

        input_rect = pygame.Rect(200, 250, 400, 40)
        input_color = (0, 0, 0)

        while entering:
            self.screen.fill((30, 30, 30)) 

            prompt_surf = font.render("Введите IP хоста:", True, (255, 255, 255))
            self.screen.blit(prompt_surf, (200, 200))

            pygame.draw.rect(self.screen, input_color, input_rect)

            input_surf = font.render(input_text, True, (255, 255, 0))
            self.screen.blit(input_surf, (input_rect.x + 5, input_rect.y + 5))

            pygame.display.flip()
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    entering = False
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        entering = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode

        return input_text

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                for button in self.current_buttons:
                    button.handle_event(event)

            # Центрирование кнопок по ширине
            screen_w, screen_h = self.screen.get_size()
            top_y = int(screen_h * 0.22)
            spacing = 100
            for idx, button in enumerate(self.current_buttons):
                b_w, b_h = button.rect.size
                center_x = screen_w // 2
                new_x = center_x - b_w // 2
                new_y = top_y + idx * spacing
                button.rect.topleft = (new_x, new_y)

            self.screen.blit(self.background, (0, 0))

            for button in self.current_buttons:
                button.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Главное меню")

    menu = MainMenu(screen)
    menu.run()

    pygame.quit()


if __name__ == "__main__":
    main()
