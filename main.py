import pygame
from core.game import Game
import sys

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
        print("Создать мир")  # пока заглушка

    def join_world(self):
        print("Подключиться")  # пока заглушка

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                for button in self.current_buttons:
                    button.handle_event(event)

            # Отрисовка фона
            self.screen.blit(self.background, (0, 0))

            # Отрисовка кнопок поверх фона
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
