import pygame
import settings
from objects.tank import Tank
from objects.enemy_tank import EnemyTank


class Game:
    """Основной класс игры."""
    def __init__(self):
        self.screen = pygame.display.set_mode((
            settings.WIDTH, settings.HEIGHT
        ))
        pygame.display.set_caption("Tanki 2D")
        self.clock = pygame.time.Clock()
        self.running = True
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()

        self.player = Tank(
            200,
            200,
            "assets/images/tank_player.png"
        )

        self.all_sprites.add(self.player)

        self.enemies = pygame.sprite.Group()
        positions = [
            (100, 100), (700, 500), (600, 100), (200, 500)
        ]  # можешь менять координаты
        for x, y in positions:
            enemy = EnemyTank(x, y)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

    def run(self):
        while self.running:
            self.clock.tick(settings.FPS)
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        self.player.update()
        for enemy in self.enemies:
            enemy.update(self.player, self)
        self.bullets.update()

    def draw(self):
        self.screen.fill((30, 30, 30))
        self.all_sprites.draw(self.screen)
        self.bullets.draw(self.screen)
        self.player.draw_bullets(self.screen)
        pygame.display.flip()


class MultiplayerGame:
    """Мультиплеерный мир без ботов, с настоящими танками игроков."""
    def __init__(self, is_host=False, server=None, client=None):
        self.screen = pygame.display.set_mode((
            settings.WIDTH, settings.HEIGHT
        ))
        pygame.display.set_caption("Tanki 2D Multiplayer")
        self.clock = pygame.time.Clock()
        self.running = True

        self.is_host = is_host
        self.server = server
        self.client = client

        # Локальный игрок
        self.player = Tank(200, 200, "assets/images/tank_player.png")
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.bullets = self.player.bullets

        # Словарь для других игроков: pid -> Tank
        self.other_players = {}
        # player_id для локального игрока (для хоста отметим как 'host')
        self.player_id = None
        if self.is_host and self.server:
            # назначаем уникальный id для хоста и регистрируем в сервере
            self.player_id = "host"
            self.server.players[self.player_id] = {
                "x": self.player.rect.centerx,
                "y": self.player.rect.centery,
                "angle": self.player.angle
            }
        # шрифт для отладки на экране
        self.font = pygame.font.SysFont("arial", 18)

    def run(self):
        while self.running:
            self.clock.tick(settings.FPS)
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        # Локальный игрок
        self.player.update()

        # Отправка позиции по сети
        action = {
            "x": self.player.rect.centerx,
            "y": self.player.rect.centery,
            "angle": self.player.angle
        }
        if self.is_host and self.server:
            # обновляем состояние хоста в сервере и отправляем всем клиенам
            if self.player_id:
                self.server.players[self.player_id] = action
            # broadcaster Server отправляет state
        elif not self.is_host and self.client:
            self.client.send_action(action)

        # Другие игроки
        # получаем состояния других игроков от клиента или сервера (если хост)
        state_src = None
        if self.client:
            state_src = self.client.state
            local_pid = self.client.player_id
        elif self.is_host and self.server:
            # у хоста берем источник из server.players
            with self.server.lock:
                state_src = dict(self.server.players)
            local_pid = self.player_id

        if state_src:
            for pid, data in state_src.items():
                if pid == local_pid:  # локальный игрок
                    continue
                if not isinstance(data, dict):
                    continue

                x = data.get("x", 0)
                y = data.get("y", 0)
                angle = data.get("angle", 0)

                if pid not in self.other_players:
                    self.other_players[pid] = Tank(
                        x, y, "assets/images/tank_player.png"
                    )
                    self.all_sprites.add(self.other_players[pid])

                self.other_players[pid].rect.centerx = x
                self.other_players[pid].rect.centery = y
                self.other_players[pid].angle = angle
                self.other_players[pid].rotate()

        # Пули локального игрока
        self.bullets.update()

    def draw(self):
        self.screen.fill((30, 30, 30))
        self.all_sprites.draw(self.screen)
        self.bullets.draw(self.screen)
        self.player.draw_bullets(self.screen)
        # отладочная информация: player_id и число известных игроков
        pid = self.player_id
        if not pid and self.client:
            pid = self.client.player_id
        players_count = 0
        if self.client:
            players_count = len(self.client.state)
        elif self.server:
            players_count = len(self.server.players)

        info_text = f"id: {pid}  players: {players_count}"
        info_surf = self.font.render(info_text, True, (255, 255, 255))
        self.screen.blit(info_surf, (10, 10))
        pygame.display.flip()

