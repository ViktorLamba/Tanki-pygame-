import pygame
import settings


class GameMap:
    """Класс игровой карты."""
    MAPS = {
        "summer": [
            "11111111111111111111",
            "1                  1",
            "1                  1",
            "1   1111    1111   1",
            "1                  1",
            "1   1          1   1",
            "1   1   1111   1   1",
            "1       1  1       1",
            "111111  1  1  111111",
            "1       1  1       1",
            "1   1   1111   1   1",
            "1   1          1   1",
            "1                  1",
            "1                  1",
            "11111111111111111111",
        ],
        "winter": [
            "11111111111111111111",
            "1                  1",
            "1                  1",
            "1   2222    2222   1",
            "1                  1",
            "1   2          2   1",
            "1   2   2222   2   1",
            "1       2  2       1",
            "111111  2  2  111111",
            "1       2  2       1",
            "1   2   2222   2   1",
            "1   2          2   1",
            "1                  1",
            "1                  1",
            "11111111111111111111",
        ],
        "desert": [
            "11111111111111111111",
            "1                  1",
            "1                  1",
            "1   1111    1111   1",
            "1                  1",
            "1                  1",
            "1       1111       1",
            "1       1  1       1",
            "111111  1  1  111111",
            "1       1  1       1",
            "1       1111       1",
            "1                  1",
            "1                  1",
            "1                  1",
            "11111111111111111111",
        ]
    }

    def __init__(self, theme="summer"):
        self.theme = theme.lower() if theme.lower() in self.MAPS else "summer"

        self.width = 20
        self.height = 15

        # считаем размер клетки по меньшей стороне окна
        scalex = settings.WIDTH / self.width
        scaley = settings.HEIGHT / self.height
        self.tile_size = int(min(scalex, scaley))

        map_px_width = self.width * self.tile_size
        map_px_height = self.height * self.tile_size
        self.offset_x = (settings.WIDTH - map_px_width) // 2
        self.offset_y = (settings.HEIGHT - map_px_height) // 2

        self.grid = []
        for row in self.MAPS[self.theme]:
            padded = row.ljust(self.width)[:self.width]
            self.grid.append([int(c) if c in "12" else 0 for c in padded])

        # спавн‑поинты считаем в координатах карты + отступ
        self.spawn_points = [
            (self.offset_x + 3 * self.tile_size,  self.offset_y + 3 * self.tile_size),
            (self.offset_x + 17 * self.tile_size, self.offset_y + 3 * self.tile_size),
            (self.offset_x + 3 * self.tile_size,  self.offset_y + 12 * self.tile_size),
            (self.offset_x + 17 * self.tile_size, self.offset_y + 12 * self.tile_size),
        ]

    def get_colors(self):
        if self.theme == "winter":
            return {"ground": (230, 245, 255), "wall": (130, 160, 200), "decor": (255, 255, 255), "decor2": (200, 230, 255)}
        elif self.theme == "desert":
            return {"ground": (220, 190, 130), "wall": (180, 130, 70), "decor": (210, 180, 100), "decor2": (160, 120, 70)}
        else:
            return {"ground": (70, 180, 70), "wall": (160, 90, 30), "decor": (40, 120, 40), "decor2": (20, 90, 20)}

    def draw(self, screen):
        colors = self.get_colors()
        for y in range(self.height):
            for x in range(self.width):
                tile = self.grid[y][x]
                rect = pygame.Rect(
                    self.offset_x + x * self.tile_size,
                    self.offset_y + y * self.tile_size,
                    self.tile_size,
                    self.tile_size
                )
                if tile == 1:
                    padding = 0
                    inner = rect.inflate(-padding, -padding)
                    pygame.draw.rect(screen, colors["wall"], inner)
                    pygame.draw.rect(screen, (0, 0, 0), inner, max(1, padding // 6))
                elif tile == 2:
                    pygame.draw.rect(screen, colors["ground"], rect)
                    # Декор центрируем внутри внутренней области стены/плитки,
                    padding = max(2, int(self.tile_size * 0.18))
                    inner = rect.inflate(-padding, -padding)
                    decor_r1 = max(4, int(self.tile_size * 0.4))
                    decor_r2 = max(2, int(self.tile_size * 0.22))
                    pygame.draw.circle(screen, colors["decor"], inner.center, decor_r1)
                    pygame.draw.circle(screen, colors["decor2"], inner.center, decor_r2)
                else:
                    pygame.draw.rect(screen, colors["ground"], rect)

    def is_wall(self, x, y):
        tx = int((x - self.offset_x) // self.tile_size)
        ty = int((y - self.offset_y) // self.tile_size)
        if tx < 0 or tx >= self.width or ty < 0 or ty >= self.height:
            return True
        return self.grid[ty][tx] == 1
