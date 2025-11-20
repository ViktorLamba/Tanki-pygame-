# objects/enemy_tank.py
import pygame
import math
import random
from objects.tank import Tank


class EnemyTank(Tank):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/images/tank_player.png")  # пока используем картинку игрока
        self.angle = random.randint(0, 360)  # чтобы не все смотрели одинаково
        self.change_direction_timer = 0
        self.last_shot_time = 0

    def update(self, player, enemies_group):
        # каждый тик увеличиваем таймер
        self.change_direction_timer += 1

        # считаем расстояние до игрока
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)

        # если игрок близко — начинаем преследовать
        if distance < 300:
            # поворачиваемся в сторону игрока
            target_angle = math.degrees(math.atan2(dy, dx)) + 90
            angle_diff = (target_angle - self.angle + 180) % 360 - 180

            if angle_diff > 5:
                self.angle -= 3
            elif angle_diff < -5:
                self.angle += 3

            # едем вперёд
            self.move_forward()

            # стреляем, если смотрим почти прямо
            if abs(angle_diff) < 20 and pygame.time.get_ticks() - self.last_shot_time > 1000:
                print("ПЫЩ!")  # потом будет пуля
                self.last_shot_time = pygame.time.get_ticks()

        else:
            # если игрок далеко — просто катаемся
            if self.change_direction_timer > 80:  # меняем направление раз в ~1.5 сек
                self.angle += random.randint(-80, 80)
                self.change_direction_timer = 0
            self.move_forward()

        # поворачиваем картинку
        self.rotate()

        # если выехали за экран — разворачиваемся (чтобы не застревать)
        if (self.rect.left < 0 or self.rect.right > 800 or
            self.rect.top < 0 or self.rect.bottom > 600):
            self.angle += 180  # разворот