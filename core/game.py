import pygame
import settings
from objects.tank import Tank


class Game:
    """Основной класс игры."""
    def __init__(self):
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        pygame.display.set_caption("Tanki 2D")
        self.clock = pygame.time.Clock()
        self.running = True
        self.all_sprites = pygame.sprite.Group()

        self.player = Tank(
            200,
            200,
            "assets/images/tank_player.png"
        )

        self.all_sprites.add(self.player)

    def run(self):
        while self.running:
            self.clock.tick(settings.FPS)
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        pass

    def draw(self):
        self.screen.fill((30, 30, 30))
        self.all_sprites.draw(self.screen)

        pygame.display.flip()
