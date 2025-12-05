# core/map.py
import pygame
import random

class GameMap:
    def __init__(self, theme="summer", tile_size=40):
        self.theme = theme.lower()
        self.tile_size = tile_size
        self.width = 800 // tile_size   # 20
        self.height = 600 // tile_size  # 15
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.spawn_points = []

        random.seed(hash(theme) + 12345)  # одинаковая карта при одной теме
        self.generate()
        self.calculate_spawn_points()

    def get_colors(self):
        if self.theme == "winter":
            return {
                "bg": (200, 230, 255),
                "ground": (240, 250, 255),
                "wall": (120, 160, 190),
                "wall_edge": (90, 130, 170),
                "decor": (255, 255, 255),
                "decor2": (220, 240, 255),
            }
        elif self.theme == "desert":
            return {
                "bg": (194, 154, 100),
                "ground": (220, 190, 140),
                "wall": (180, 120, 60),
                "wall_edge": (140, 90, 40),
                "decor": (210, 180, 100),
                "decor2": (160, 120, 70),
            }
        else:  # summer
            return {
                "bg": (40, 140, 40),
                "ground": (60, 180, 60),
                "wall": (139, 90, 19),
                "wall_edge": (100, 60, 10),
                "decor": (20, 100, 20),
                "decor2": (10, 80, 10),
            }

    def generate(self):
        # Бордюр
        for x in range(self.width):
            self.grid[0][x] = self.grid[self.height-1][x] = 1
        for y in range(self.height):
            self.grid[y][0] = self.grid[y][self.width-1] = 1

        # Классическая симметричная структура танчиков
        pattern = [
            (5,5), (5,9), (14,5), (14,9),
            (9,7), (10,7), (9,8), (10,8),
        ]
        for x, y in pattern:
            if 0 <= x < self.width and 0 <= y < self.height:
                self.grid[y][x] = 1

        # Случайные стены
        for _ in range(15):
            x = random.randint(3, 8)
            y = random.randint(3, 11)
            self.grid[y][x] = self.grid[y][19-x] = self.grid[14-y][x] = self.grid[14-y][19-x] = 1

        # Декор
        for _ in range(30):
            x = random.randint(2, 17)
            y = random.randint(2, 12)
            if self.grid[y][x] == 0:
                self.grid[y][x] = 2

    def calculate_spawn_points(self):
        margin = 2
        self.spawn_points = [
            (margin * self.tile_size + 20, margin * self.tile_size + 20),
            ((self.width - margin - 1) * self.tile_size - 20, margin * self.tile_size + 20),
            (margin * self.tile_size + 20, (self.height - margin - 1) * self.tile_size - 20),
            ((self.width - margin - 1) * self.tile_size - 20, (self.height - margin - 1) * self.tile_size - 20),
        ]

    def draw(self, screen):
        colors = self.get_colors()
        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                if self.grid[y][x] == 1:  # стена
                    pygame.draw.rect(screen, colors["wall_edge"], rect)
                    pygame.draw.rect(screen, colors["wall"], rect.inflate(-8, -8))
                elif self.grid[y][x] == 2:  # декор
                    pygame.draw.circle(screen, colors["decor"], rect.center, 12)
                    pygame.draw.circle(screen, colors["decor2"], rect.center, 7)
                else:
                    pygame.draw.rect(screen, colors["ground"], rect)

    def is_wall(self, x, y):
        """Для коллизий"""
        tx, ty = int(x // self.tile_size), int(y // self.tile_size)
        if not (0 <= tx < self.width and 0 <= ty < self.height):
            return True
        return self.grid[ty][tx] == 1