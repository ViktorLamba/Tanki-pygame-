import pygame
import math
import settings

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        # Создаем красный кружок для пули
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 0, 0), (4, 4), 4)  # Красная пуля
        self.rect = self.image.get_rect(center=(x, y))
        
        self.speed = 10
        self.angle = angle
        self.lifetime = 60  # Пуля исчезнет через 60 кадров

    def update(self):
        # Движение пули
        rad = math.radians(self.angle - 90)
        dx = math.cos(rad) * self.speed
        dy = math.sin(rad) * self.speed
        self.rect.centerx -= dx
        self.rect.centery += dy
        
        # Уменьшаем время жизни
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()  # Удаляем пулю