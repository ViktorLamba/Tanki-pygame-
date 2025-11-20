import pygame
import settings


class Tank(pygame.sprite.Sprite):
    """Класс танка."""
    def __init__(self, x, y, image):
        super().__init__()
        original_image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(original_image, (100, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = settings.TANK_SPEED

    def update(self, keys):
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed
