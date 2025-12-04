import pygame
import math
import settings

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, owner):
        super().__init__()
        self.owner = owner  # кто выстрелил (чтобы не попасть в себя)
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 200, 0), (6, 6), 6)
        pygame.draw.circle(self.image, (255, 100, 0), (6, 6), 4)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.speed = settings.BULLET_SPEED
        self.angle = angle
        self.lifetime = 80

        # Эффект попадания
        self.hit_effect = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(self.hit_effect, (255, 255, 100, 180), (20, 20), 20)
        pygame.draw.circle(self.hit_effect, (255, 200, 0, 100), (20, 20), 12)

    def update(self):
        rad = math.radians(self.angle - 90)
        self.rect.x -= math.cos(rad) * self.speed
        self.rect.y += math.sin(rad) * self.speed
        
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

    def draw_hit_effect(self, screen):
        screen.blit(self.hit_effect, self.hit_effect.get_rect(center=self.rect.center))