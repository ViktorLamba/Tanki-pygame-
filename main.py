import pygame
import sys
from core.multiplayer import Client, Server
from core.game import Game
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
        self.game = Game()

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
        print("Открыть настройки")  # пока заглушка

    def create_world(self):
        # Запускаем сервер в отдельном потоке
        threading.Thread(target=Server().start, daemon=True).start()
        print("Сервер запущен!")

        # Создаем и запускаем игру
        game = Game()
        game.run()

    def join_world(self):
        host_ip = self.enter_host_ip()
        self.client = Client(host_ip, port=5555)
        threading.Thread(target=self.run_multiplayer_game, daemon=True).start()

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
