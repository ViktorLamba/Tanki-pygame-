import pygame
import math
import settings

pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.mixer.init()

try:
    shoot_sound = pygame.mixer.Sound("assets/sounds/shoot.wav")
    explosion_sound = pygame.mixer.Sound("assets/sounds/explosion.wav")
    shoot_sound.set_volume(0.7)
    explosion_sound.set_volume(0.8)
except Exception as e:
    print("ОШИБКА ЗВУКА:", e)
    shoot_sound = explosion_sound = None

class Tank(pygame.sprite.Sprite):
    """Базовый класс танка (игрок + враги)"""
    def __init__(self, x, y, image_path):
        super().__init__()
        original_image = pygame.image.load(image_path).convert_alpha()
        self.original_image = pygame.transform.scale(original_image, (85, 115))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))

        self.speed = settings.TANK_SPEED
        self.angle = 0
        self.bullets = pygame.sprite.Group()
        self.shoot_cooldown = 0

        self.max_hp = settings.TANK_HP
        self.hp = self.max_hp
        self.alive = True

        self.explosion_frames = []
        try:
            for i in range(1, 9):
                img = pygame.image.load(f"assets/images/explosion/explosion_{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (140, 140))
                self.explosion_frames.append(img)
        except:
            pass

        self.game_map = None
        self.current_explosion_frame = 0
        self.explosion_timer = 0

    def can_move_to(self, x, y):
        if not self.game_map:
            return True
        # Проверяем только 4 угла танка + центр — теперь не застревает!
        offset = 34
        points = [
            (x - offset, y - offset),
            (x + offset, y - offset),
            (x - offset, y + offset),
            (x + offset, y + offset),
            (x, y)
        ]
        return all(not self.game_map.is_wall(px, py) for px, py in points)

    def move_forward(self):
        if not self.alive: return
        rad = math.radians(self.angle - 90)
        dx = math.cos(rad) * self.speed
        dy = math.sin(rad) * self.speed
        if self.can_move_to(self.rect.centerx - dx, self.rect.centery + dy):
            self.rect.centerx -= dx
            self.rect.centery += dy

    def move_backward(self):
        if not self.alive: return
        rad = math.radians(self.angle - 90)
        dx = math.cos(rad) * self.speed
        dy = math.sin(rad) * self.speed
        if self.can_move_to(self.rect.centerx + dx, self.rect.centery - dy):
            self.rect.centerx += dx
            self.rect.centery -= dy

    def rotate(self):
        old_center = self.rect.center
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=old_center)

    def shoot(self):
        if self.shoot_cooldown > 0 or not self.alive: return
        from objects.bullet import Bullet
        rad = math.radians(self.angle - 90)
        bullet = Bullet(
            self.rect.centerx - math.cos(rad) * 50,
            self.rect.centery + math.sin(rad) * 50,
            self.angle,
            owner=self
        )
        self.bullets.add(bullet)
        self.shoot_cooldown = 15
        if shoot_sound:
            shoot_sound.play()

    def update(self):
        if not self.alive:
            if self.explosion_frames:
                self.explosion_timer += 1
                if self.explosion_timer >= 5:
                    self.explosion_timer = 0
                    self.current_explosion_frame += 1
            return

        keys = pygame.key.get_pressed()
        rotated = False
        if keys[pygame.K_a]:
            self.angle += 5
            rotated = True
        if keys[pygame.K_d]:
            self.angle -= 5
            rotated = True
        if keys[pygame.K_w]:
            self.move_forward()
        if keys[pygame.K_s]:
            self.move_backward()
        if keys[pygame.K_SPACE]:
            self.shoot()

        if rotated:
            self.rotate()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        self.bullets.update()

    def draw(self, screen):
        if self.alive:
            screen.blit(self.image, self.rect)
            self.draw_hp_bar(screen)
        else:
            if self.explosion_frames and self.current_explosion_frame < len(self.explosion_frames):
                expl = self.explosion_frames[self.current_explosion_frame]
                screen.blit(expl, expl.get_rect(center=self.rect.center))

    def draw_hp_bar(self, screen):
        bar_w, bar_h = 80, 10
        x = self.rect.centerx - bar_w // 2
        y = self.rect.top - 20
        pygame.draw.rect(screen, (50,50,50), (x, y, bar_w, bar_h))
        fill = int(bar_w * self.hp / self.max_hp)
        color = (0,255,0) if self.hp > 60 else (255,255,0) if self.hp > 30 else (255,0,0)
        pygame.draw.rect(screen, color, (x, y, fill, bar_h))
        pygame.draw.rect(screen, (255,255,255), (x, y, bar_w, bar_h), 2)

    def draw_bullets(self, screen):
        self.bullets.draw(screen)

    def take_damage(self, amount):
        if not self.alive:
            return
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.die()

    def die(self):
        self.alive = False
        self.current_explosion_frame = 0
        self.explosion_timer = 0
        if explosion_sound:
            explosion_sound.play()
    def take_damage(self, amount):
        if not self.alive:
            return
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.die()

    def die(self):
        self.alive = False
        self.current_explosion_frame = 0
        self.explosion_timer = 0
        if explosion_sound:
            explosion_sound.play()