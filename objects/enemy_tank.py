import pygame
import math
import random
import settings
from .tank import Tank


def angle_between(a, b):
    """Разница углов [-180..180]"""
    return (b - a + 180) % 360 - 180


class EnemyTank(Tank):
    """Класс ботов."""
    def __init__(self, x, y):
        super().__init__(x, y, "assets/images/tank_enemy.png")

        self.angle = random.randint(0, 360)
        self.target_angle = self.angle

        self.vision_radius = 550
        self.stop_distance = 150

        self.rotate_speed = 2.4
        self.fire_interval = 900
        self.last_shot = 0

        self.state = "search"

    def angle_to_player(self, player):
        px, py = player.rect.center
        tx, ty = self.rect.center

        dx = px - tx
        dy = py - ty

        desired = math.degrees(math.atan2(dy, dx))
        return desired - 90

    def avoid_others(self, game):
        for enemy in game.enemies:
            if enemy is self or not enemy.alive:
                continue

            dist = math.hypot(
                enemy.rect.centerx - self.rect.centerx,
                enemy.rect.centery - self.rect.centery
            )

            if dist < 80:
                dx = self.rect.centerx - enemy.rect.centerx
                dy = self.rect.centery - enemy.rect.centery

                if dist != 0:
                    self.rect.centerx += dx / dist * 1.3
                    self.rect.centery += dy / dist * 1.3

    def update(self, player, game):
        if not self.alive:
            super().update()
            return

        px, py = player.rect.center
        tx, ty = self.rect.center

        dx = px - tx
        dy = py - ty
        distance = math.hypot(dx, dy)

        sees = distance < self.vision_radius and player.alive

        if sees:
            self.state = "combat"
            self.target_angle = self.angle_to_player(player)
        else:
            self.state = "search"
            if random.random() < 0.005:
                self.target_angle += random.randint(-80, 80)

        diff = angle_between(self.angle, self.target_angle)

        if abs(diff) > self.rotate_speed:
            self.angle += self.rotate_speed if diff > 0 else -self.rotate_speed
        else:
            self.angle = self.target_angle

        if self.state == "combat" and distance > self.stop_distance:
            old = self.rect.copy()
            self.move_forward()
            self.avoid_others(game)

            # границы
            if (self.rect.left < 30 or self.rect.right > settings.WIDTH - 30 or
                self.rect.top < 30 or self.rect.bottom > settings.HEIGHT - 30):

                self.rect = old
                self.target_angle += 180   # развернуть

        aim_dir = self.angle + 90
        desired_dir = math.degrees(math.atan2(dy, dx))

        aim_error = abs(angle_between(aim_dir, desired_dir))

        if (self.state == "combat" and
            aim_error < 6 and
            pygame.time.get_ticks() - self.last_shot > self.fire_interval and
            player.alive):

            self.shoot()
            self.last_shot = pygame.time.get_ticks()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        self.bullets.update()
        self.rotate()