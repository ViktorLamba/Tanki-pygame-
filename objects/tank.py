import pygame
import math
import settings


class Tank(pygame.sprite.Sprite):
    """Класс танка."""
    def __init__(self, x, y, image):
        super().__init__()
        original_image = pygame.image.load(image).convert_alpha()
        self.original_image = pygame.transform.scale(original_image, (100, 100))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))

        self.speed = settings.TANK_SPEED
        self.angle = 0  # Угол поворота танка
        self.bullets = pygame.sprite.Group()  # Группа для пуль
        self.shoot_cooldown = 0  # Задержка между выстрелами

    def update(self):
        keys = pygame.key.get_pressed()  # Получаем клавиши
        if keys[pygame.K_a]:
            self.angle += 3
        if keys[pygame.K_d]:
            self.angle -= 3
        if keys[pygame.K_w]:
            self.move_forward()
        if keys[pygame.K_s]:
            self.move_backward()
                # Обработка стрельбы
        if keys[pygame.K_SPACE] and self.shoot_cooldown <= 0:
            self.shoot()
            self.shoot_cooldown = 20  # Задержка 20 кадров
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
        # Обновляем пули
        self.bullets.update()    
        self.rotate()

    def move_forward(self):
        rad = math.radians(self.angle - 90)  # отнимаем 90 градусов для корректного направления
        dx = math.cos(rad) * self.speed
        dy = math.sin(rad) * self.speed
        self.rect.centerx -= dx
        self.rect.centery += dy

    def move_backward(self):
        rad = math.radians(self.angle - 90)  # отнимаем 90 градусов для корректного направления
        dx = math.cos(rad) * self.speed
        dy = math.sin(rad) * self.speed
        self.rect.centerx += dx
        self.rect.centery -= dy

    def rotate(self):
        # Вращение изображения
        self.image = pygame.transform.rotate(self.original_image, self.angle)

        # Сохранение центра
        self.rect = self.image.get_rect(center=self.rect.center)

    def shoot(self):
        """Создание пули"""
        from objects.bullet import Bullet  # Импортируем здесь чтобы избежать циклического импорта
        
        # Вычисляем позицию дула (перед танком)
        rad = math.radians(self.angle - 90)
        muzzle_x = self.rect.centerx - math.cos(rad) * 40
        muzzle_y = self.rect.centery + math.sin(rad) * 40
        
        # Создаем пулю
        bullet = Bullet(muzzle_x, muzzle_y, self.angle)
        self.bullets.add(bullet)

    def draw_bullets(self, screen):
        """Отрисовка пуль"""
        self.bullets.draw(screen)
    
