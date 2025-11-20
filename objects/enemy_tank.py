import pygame
import math
import random
from objects.tank import Tank
from objects.bullet import Bullet


class EnemyTank(Tank):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/images/tank_player.png")

        self.angle = random.randint(0, 360)
        self.target_angle = self.angle

        self.state = "search"
        self.last_shshot = 0

        self.vision_radius = 400
        self.stop_distance = 140

        self.fire_interval = 1300
        self.rotate_speed = 2


    def avoid_others(self, game):
        for enemy in game.enemies:
            if enemy is self:
                continue

            dist = math.hypot(
                enemy.rect.centerx - self.rect.centerx,
                enemy.rect.centery - self.rect.centery
            )

            if dist < 85:  # дистанция сближения
                dx = self.rect.centerx - enemy.rect.centerx
                dy = self.rect.centery - enemy.rect.centery

                if dx == 0 and dy == 0:
                    dx = 1

                # нормализуем
                nx = dx / dist
                ny = dy / dist

                self.rect.x += nx * 1.3
                self.rect.y += ny * 1.3


    def update(self, player, game):

        px, py = player.rect.center
        tx, ty = self.rect.center

        dx = px - tx
        dy = py - ty
        distance = math.hypot(dx, dy)

        if distance < self.vision_radius:
            self.state = "combat"
            self.target_angle = math.degrees(math.atan2(dy, dx))
        else:
            self.state = "search"
            if random.random() < 0.008:
                self.target_angle += random.randint(-80, 80)


        diff = (self.target_angle - self.angle + 180) % 360 - 180

        if diff > self.rotate_speed:
            self.angle += self.rotate_speed
        elif diff < -self.rotate_speed:
            self.angle -= self.rotate_speed
        else:
            self.angle = self.target_angle


        if distance > self.stop_distance:
            old_rect = self.rect.copy()
            self.move_forward()

            # избегаем друг друга (плавно)
            self.avoid_others(game)

            # границы
            if (self.rect.left < 30 or self.rect.right > 770 or
                self.rect.top < 30 or self.rect.bottom > 570):
                self.rect = old_rect
                self.target_angle += 180

        if (self.state == "combat"
            and abs(diff) < 10
            and pygame.time.get_ticks() - self.last_shshot > self.fire_interval):

            rad = math.radians(self.angle - 90)
            muzzle_x = self.rect.centerx - math.cos(rad) * 40
            muzzle_y = self.rect.centery + math.sin(rad) * 40

            bullet = Bullet(muzzle_x, muzzle_y, self.angle)
            self.bullets.add(bullet)
            game.all_sprites.add(bullet)
            self.last_shshot = pygame.time.get_ticks()

        self.bullets.update()
        self.rotate()
