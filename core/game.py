import pygame
import settings
from objects.tank import Tank
from objects.enemy_tank import EnemyTank


class Game:
    """Одиночная игра — классика танчиков"""
    def __init__(self):
        self.screen = pygame.display.get_surface()
        pygame.display.set_caption("Tanki 2D — Бой")

        self.clock = pygame.time.Clock()
        self.running = True
        self.return_to_main_menu = False

        # Группы спрайтов
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        # Позиции врагов
        self.enemy_positions = [(100, 100), (700, 100), (700, 500), (100, 500)]

        # Игрок
        self.player = Tank(400, 300, "assets/images/tank_player.png")
        self.all_sprites.add(self.player)

        self.spawn_enemies()

        # Таймеры
        self.player_respawn_timer = 0
        self.player_respawn_delay = 3000
        self.victory = False

        # Шрифты
        self.font_title = pygame.font.SysFont("arial", 80, bold=True)
        self.font_button = pygame.font.SysFont("arial", 48)
        self.font_timer = pygame.font.SysFont("arial", 40)

        self.btn_restart = None
        self.btn_main_menu = None

    def spawn_enemies(self):
        self.enemies.empty()
        for x, y in self.enemy_positions:
            enemy = EnemyTank(x, y)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.return_to_main_menu = False

            if self.victory and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if self.btn_restart and self.btn_restart.collidepoint(mx, my):
                    self.restart_level()
                elif self.btn_main_menu and self.btn_main_menu.collidepoint(mx, my):
                    self.return_to_main_menu = True
                    self.running = False

    def update(self):
        if not any(enemy.alive for enemy in self.enemies) and not self.victory:
            self.victory = True
            return

        if not self.player.alive:
            if self.player_respawn_timer == 0:
                self.player_respawn_timer = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - self.player_respawn_timer >= self.player_respawn_delay:
                self.player.respawn(400, 300)
                self.player_respawn_timer = 0
            return

        self.player.update()
        for enemy in self.enemies:
            if enemy.alive:
                enemy.update(self.player, self)

        # Пули игрока → враги
        for bullet in self.player.bullets:
            hits = pygame.sprite.spritecollide(bullet, self.enemies, False)
            for hit in hits:
                if bullet.owner == self.player and hit.alive:
                    hit.take_damage(34)
                    bullet.kill()

        # Пули врагов → игрок
        for enemy in self.enemies:
            for bullet in enemy.bullets:
                if bullet.owner != self.player and pygame.sprite.collide_rect(bullet, self.player):
                    if self.player.alive:
                        self.player.take_damage(34)
                    bullet.kill()

    def restart_level(self):
        self.spawn_enemies()
        self.player.respawn(400, 300)
        self.victory = False

    def draw(self):
        self.screen.fill((30, 30, 30))

        for sprite in self.all_sprites:
            if hasattr(sprite, "draw"):
                sprite.draw(self.screen)
            else:
                self.screen.blit(sprite.image, sprite.rect)

        self.player.draw_bullets(self.screen)
        for enemy in self.enemies:
            enemy.draw_bullets(self.screen)

        if self.victory:
            self.draw_victory_screen()
        elif not self.player.alive:
            self.draw_death_screen()

        pygame.display.flip()

    def draw_victory_screen(self):
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title = self.font_title.render("ПОБЕДА!", True, (0, 255, 100))
        self.screen.blit(title, title.get_rect(center=(settings.WIDTH//2, 180)))

        restart_surf = self.font_button.render("Перезапустить", True, (255, 255, 255))
        menu_surf = self.font_button.render("Главное меню", True, (255, 255, 255))

        pad_x, pad_y = 60, 30

        w1 = restart_surf.get_width() + pad_x
        h1 = restart_surf.get_height() + pad_y
        self.btn_restart = pygame.Rect(0, 0, w1, h1)
        self.btn_restart.centerx = settings.WIDTH // 2
        self.btn_restart.top = 300

        w2 = menu_surf.get_width() + pad_x
        h2 = menu_surf.get_height() + pad_y
        self.btn_main_menu = pygame.Rect(0, 0, w2, h2)
        self.btn_main_menu.centerx = settings.WIDTH // 2
        self.btn_main_menu.top = self.btn_restart.bottom + 30

        pygame.draw.rect(self.screen, (0, 150, 0), self.btn_restart, border_radius=15)
        pygame.draw.rect(self.screen, (150, 0, 0), self.btn_main_menu, border_radius=15)

        self.screen.blit(restart_surf, restart_surf.get_rect(center=self.btn_restart.center))
        self.screen.blit(menu_surf, menu_surf.get_rect(center=self.btn_main_menu.center))

        mx, my = pygame.mouse.get_pos()
        if self.btn_restart.collidepoint(mx, my):
            pygame.draw.rect(self.screen, (0, 255, 0), self.btn_restart, 6, border_radius=15)
        if self.btn_main_menu.collidepoint(mx, my):
            pygame.draw.rect(self.screen, (255, 0, 0), self.btn_main_menu, 6, border_radius=15)

    def draw_death_screen(self):
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        death = self.font_title.render("УНИЧТОЖЕН", True, (255, 50, 50))
        self.screen.blit(death, death.get_rect(center=(settings.WIDTH//2, settings.HEIGHT//2 - 50)))

        sec = max(0, (self.player_respawn_delay - (pygame.time.get_ticks() - self.player_respawn_timer)) // 1000)
        respawn = self.font_timer.render(f"Возрождение через {sec}...", True, (255, 255, 255))
        self.screen.blit(respawn, respawn.get_rect(center=(settings.WIDTH//2, settings.HEIGHT//2 + 50)))

    def run(self):
        while self.running:
            self.clock.tick(settings.FPS)
            self.handle_events()
            self.update()
            self.draw()
        return self.return_to_main_menu


# ВЕРНУЛ МУЛЬТИПЛЕЕР — ЧТОБЫ main.py НЕ РУГАЛСЯ
class MultiplayerGame:
    """Мультиплеерный мир без ботов, с настоящими танками игроков."""
    def __init__(self, is_host=False, server=None, client=None):
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        pygame.display.set_caption("Tanki 2D Multiplayer")
        self.clock = pygame.time.Clock()
        self.running = True
        self.is_host = is_host
        self.server = server
        self.client = client

        self.player = Tank(200, 200, "assets/images/tank_player.png")
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.bullets = self.player.bullets

        self.other_players = {}
        self.player_id = None
        if self.is_host and self.server:
            self.player_id = "host"
            self.server.players[self.player_id] = {
                "x": self.player.rect.centerx,
                "y": self.player.rect.centery,
                "angle": self.player.angle,
                "hp": self.player.hp,
                "alive": self.player.alive
            }

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
        self.player.update()

        action = {
            "x": self.player.rect.centerx,
            "y": self.player.rect.centery,
            "angle": self.player.angle,
            "hp": self.player.hp,
            "alive": self.player.alive
        }

        if self.is_host and self.server:
            if self.player_id:
                self.server.players[self.player_id] = action
        elif not self.is_host and self.client:
            self.client.send_action(action)

        state_src = None
        local_pid = self.player_id
        if self.client:
            state_src = self.client.state
            local_pid = self.client.player_id
        elif self.is_host and self.server:
            with self.server.lock:
                state_src = dict(self.server.players)

        if state_src:
            for pid, data in state_src.items():
                if pid == local_pid:
                    continue
                if pid not in self.other_players:
                    self.other_players[pid] = Tank(100, 100, "assets/images/tank_player.png")
                    self.all_sprites.add(self.other_players[pid])

                tank = self.other_players[pid]
                tank.rect.centerx = data.get("x", tank.rect.centerx)
                tank.rect.centery = data.get("y", tank.rect.centery)
                tank.angle = data.get("angle", tank.angle)
                tank.hp = data.get("hp", tank.hp)
                tank.alive = data.get("alive", True)
                tank.rotate()

        self.bullets.update()

    def draw(self):
        self.screen.fill((30, 30, 30))
        self.all_sprites.draw(self.screen)
        self.player.draw_bullets(self.screen)

        for tank in self.other_players.values():
            tank.draw(self.screen)
            tank.draw_bullets(self.screen)

        pid = self.player_id or (self.client.player_id if self.client else "???")
        info = f"ID: {pid} | Игроков: {len(self.other_players)+1}"
        text = self.font.render(info, True, (255, 255, 255))
        self.screen.blit(text, (10, 10))

        pygame.display.flip()
