import pygame
import math
import random
import settings
from importlib import reload
from .tank import Tank


class EnemyTank(Tank):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/images/tank_enemy.png")
        self.angle = random.randint(0, 360)
        self.target_angle = self.angle
        self.state = "search"
        self.last_shot = 0
        self.vision_radius = 400
        self.stop_distance = 140
        self.fire_interval = 1300
        self.rotate_speed = 2

    def avoid_others(self, game):
        for enemy in game.enemies:
            if enemy is self or not enemy.alive:
                continue
            dist = math.hypot(enemy.rect.centerx - self.rect.centerx,
                            enemy.rect.centery - self.rect.centery)
            if dist < 85:
                dx = self.rect.centerx - enemy.rect.centerx
                dy = self.rect.centery - enemy.rect.centery
                if dist != 0:
                    nx, ny = dx / dist, dy / dist
                    self.rect.x += nx * 1.5
                    self.rect.y += ny * 1.5

    def update(self, player, game):
        if not self.alive:
            super().update()
            return

        px, py = player.rect.center
        tx, ty = self.rect.center
        dx = px - tx
        dy = py - ty
        distance = math.hypot(dx, dy)

        if distance < self.vision_radius and player.alive:
            self.state = "combat"
            self.target_angle = math.degrees(math.atan2(dy, dx))
        else:
            self.state = "search"
            if random.random() < 0.008:
                self.target_angle += random.randint(-90, 90)

        diff = (self.target_angle - self.angle + 180) % 360 - 180
        if abs(diff) > self.rotate_speed:
            self.angle += self.rotate_speed if diff > 0 else -self.rotate_speed
        else:
            self.angle = self.target_angle

        if distance > self.stop_distance and self.state == "combat":
            old_rect = self.rect.copy()
            self.move_forward()
            self.avoid_others(game)
            if (self.rect.left < 30 or self.rect.right > settings.WIDTH - 30 or
                self.rect.top < 30 or self.rect.bottom > settings.HEIGHT - 30):
                self.rect = old_rect
                self.target_angle += 180

        if (self.state == "combat" and abs(diff) < 12 and
            pygame.time.get_ticks() - self.last_shot > self.fire_interval and player.alive):
            self.shoot()
            self.last_shot = pygame.time.get_ticks()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        self.bullets.update()
        self.rotate()