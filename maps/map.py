import pygame

class GameMap:
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
        ]
    }

    def __init__(self, theme="summer"):
        self.theme = theme.lower() if theme.lower() in self.MAPS else "summer"
        self.tile_size = 40
        self.width = 20
        self.height = 15
        self.grid = []
        for row in self.MAPS[self.theme]:
            padded = row.ljust(20)[:20]
            self.grid.append([int(c) if c in "12" else 0 for c in padded])

        self.spawn_points = [
            (120, 120),   # левый верх
            (680, 120),   # правый верх
            (120, 480),   # левый низ
            (680, 480),   # правый низ
        ]

    def get_colors(self):
        if self.theme == "winter":
            return {"ground": (230,245,255), "wall": (130,160,200), "decor": (255,255,255), "decor2": (200,230,255)}
        elif self.theme == "desert":
            return {"ground": (220,190,130), "wall": (180,130,70), "decor": (210,180,100), "decor2": (160,120,70)}
        else:
            return {"ground": (70,180,70), "wall": (160,90,30), "decor": (40,120,40), "decor2": (20,90,20)}

    def draw(self, screen):
        colors = self.get_colors()
        for y in range(self.height):
            for x in range(self.width):
                tile = self.grid[y][x]
                rect = pygame.Rect(x * 40, y * 40, 40, 40)
                if tile == 1:
                    pygame.draw.rect(screen, colors["wall"], rect)
                    pygame.draw.rect(screen, (0,0,0), rect, 2)
                elif tile == 2:
                    pygame.draw.rect(screen, colors["ground"], rect)
                    pygame.draw.circle(screen, colors["decor"], rect.center, 16)
                    pygame.draw.circle(screen, colors["decor2"], rect.center, 9)
                else:
                    pygame.draw.rect(screen, colors["ground"], rect)

    def is_wall(self, x, y):
        tx = int(x // 40)
        ty = int(y // 40)
        if tx < 0 or tx >= 20 or ty < 0 or ty >= 15:
            return True
        return self.grid[ty][tx] == 1