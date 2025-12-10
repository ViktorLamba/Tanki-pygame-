import pygame
import math
import settings

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, owner):
        super().__init__()
        self.owner = owner
        self.game_map = owner.game_map
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 200, 0), (6, 6), 6)
        pygame.draw.circle(self.image, (255, 100, 0), (6, 6), 4)
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = angle
        rad = math.radians(angle - 90)
        self.dx = -math.cos(rad) * settings.BULLET_SPEED
        self.dy = math.sin(rad) * settings.BULLET_SPEED
        self.x = x
        self.y = y

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.center = (round(self.x), round(self.y))

        # УБИВАЕМ ПУЛЮ, ЕСЛИ ВРЕЗАЛАСЬ В СТЕНУ
        if self.game_map and self.game_map.is_wall(self.x, self.y):
            self.kill()