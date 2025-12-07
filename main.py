import pygame
import sys
import random
from settings import *
from sprites import *

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont("Arial", 24)
        
        # Sound effects using Windows beep (simple but works)
        self.sounds_enabled = True
        try:
            import winsound
            self.winsound = winsound
        except ImportError:
            self.sounds_enabled = False
            print("Sound not available on this system")

    def new(self):
        # Start a new game
        self.all_sprites = CameraGroup() # Use CameraGroup
        self.walls = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        
        self.player = Player(self, MAP_WIDTH // 2, MAP_HEIGHT // 2) # Spawn in middle
        
        # Initial Enemies
        # Initial Enemies
        for _ in range(7):
            while True:
                x = random.randint(0, MAP_WIDTH - ENEMY_SIZE)
                y = random.randint(0, MAP_HEIGHT - ENEMY_SIZE)
                rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
                if not any(wall.rect.colliderect(rect) for wall in self.walls):
                    Enemy(self, x, y)
                    break
        
        # Create some obstacles (randomly scattered for now)
        for _ in range(20):
            x = random.randint(0, MAP_WIDTH - 100)
            y = random.randint(0, MAP_HEIGHT - 100)
            w = random.randint(50, 200)
            h = random.randint(50, 200)
            Obstacle(self, x, y, w, h)
        
        # Spawn weapons
        self.spawn_weapons()
        
        self.score = 0
        self.start_time = pygame.time.get_ticks()
        self.last_enemy_spawn = pygame.time.get_ticks()
        self.last_weapon_spawn = pygame.time.get_ticks()
        
        self.run()

    def spawn_weapons(self):
        for _ in range(WEAPON_SPAWN_COUNT):
            x = random.randint(0, MAP_WIDTH - WEAPON_SIZE)
            y = random.randint(0, MAP_HEIGHT - WEAPON_SIZE)
            # Simple check to avoid spawning inside walls
            rect = pygame.Rect(x, y, WEAPON_SIZE, WEAPON_SIZE)
            if not any(wall.rect.colliderect(rect) for wall in self.walls):
                WeaponItem(self, x, y)

    def run(self):
        # Game Loop
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def shoot(self, sprite, target_pos=None):
        # Get weapon stats
        weapon_name = sprite.weapon
        weapon_stats = WEAPONS[weapon_name]
        
        now = pygame.time.get_ticks()
        if now - sprite.last_shot > weapon_stats['rate']:
            sprite.last_shot = now
            
            # Determine direction
            if isinstance(sprite, Player):
                # Player shoots towards mouse (adjusted for camera)
                mx, my = pygame.mouse.get_pos()
                camera_offset = self.all_sprites.offset
                world_mouse_pos = vec(mx, my) + camera_offset
                
                dir = world_mouse_pos - sprite.pos
                if dir.length() > 0:
                    dir = dir.normalize()
                owner = 'player'
            else:
                # Enemy shoots at target
                mx, my = target_pos
                # Use center for more accurate aiming
                enemy_center = vec(sprite.rect.centerx, sprite.rect.centery)
                dir = vec(mx, my) - enemy_center
                if dir.length() > 0:
                    dir = dir.normalize()
                owner = 'enemy'
            
            # Create projectiles based on weapon count and spread
            for i in range(weapon_stats['count']):
                spread = random.uniform(-weapon_stats['spread'], weapon_stats['spread'])
                vel = dir.rotate(spread)
                
                # Use Grenade for grenade launcher, regular Projectile for others
                if weapon_name == 'grenade':
                    Grenade(self, sprite.rect.centerx, sprite.rect.centery, vel.x, vel.y, owner, 
                           weapon_stats['damage'], weapon_stats['speed'], weapon_stats['lifetime'], weapon_stats['color'])
                else:
                    Projectile(self, sprite.rect.centerx, sprite.rect.centery, vel.x, vel.y, owner, 
                               weapon_stats['damage'], weapon_stats['speed'], weapon_stats['lifetime'], weapon_stats['color'])
            
            # Play shoot sound (only for player)
            if owner == 'player' and self.sounds_enabled:
                try:
                    self.winsound.Beep(800, 30)  # 800 Hz, 30ms
                except:
                    pass

    def events(self):
        # Game Loop - Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()
        
        # Enemy Respawn Logic
        if len(self.enemies) < 7: # Keep at most 7 enemies
            now = pygame.time.get_ticks()
            if now - self.last_enemy_spawn > ENEMY_RESPAWN_TIME:
                self.last_enemy_spawn = now
                while True:
                    x = random.randint(0, MAP_WIDTH - ENEMY_SIZE)
                    y = random.randint(0, MAP_HEIGHT - ENEMY_SIZE)
                    rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
                    if not any(wall.rect.colliderect(rect) for wall in self.walls):
                        Enemy(self, x, y)
                        break

        # Weapon Respawn Logic
        now = pygame.time.get_ticks()
        if now - self.last_weapon_spawn > WEAPON_RESPAWN_TIME:
            self.last_weapon_spawn = now
            self.spawn_weapons()

        # Weapon Pickup Logic - Player
        hits = pygame.sprite.spritecollide(self.player, self.items, True)
        for hit in hits:
            # Equip weapon
            self.player.weapon = hit.type
            self.score += 10

        # Weapon Pickup Logic - Enemies
        for enemy in self.enemies:
            hits = pygame.sprite.spritecollide(enemy, self.items, True)
            for hit in hits:
                # Enemy equips weapon
                enemy.weapon = hit.type

        # Game Over Check - 10 hits
        if self.player.hit_count >= 10:
            self.playing = False

    def draw(self):
        # Game Loop - Draw
        self.screen.fill(DARK_GREY)
        # self.all_sprites.draw(self.screen) # Old draw
        self.all_sprites.custom_draw(self.player) # Camera draw
        
        # HUD
        self.draw_text(f"Score: {self.score}", 10, 10)
        self.draw_text(f"Weapon: {self.player.weapon.upper()}", 10, SCREEN_HEIGHT - 30)
        self.draw_text(f"Hits: {self.player.hit_count}/10", 10, SCREEN_HEIGHT - 60)
        
        pygame.display.flip()

    def draw_text(self, text, x, y):
        surface = self.font.render(text, True, WHITE)
        self.screen.blit(surface, (x, y))

    def show_start_screen(self):
        self.screen.fill(DARK_GREY)
        self.draw_text(TITLE, SCREEN_WIDTH / 2 - 50, SCREEN_HEIGHT / 2 - 50)
        self.draw_text("Press any key to start", SCREEN_WIDTH / 2 - 80, SCREEN_HEIGHT / 2 + 10)
        pygame.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        self.screen.fill(DARK_GREY)
        self.draw_text("GAME OVER", SCREEN_WIDTH / 2 - 60, SCREEN_HEIGHT / 2 - 50)
        self.draw_text(f"Score: {self.score}", SCREEN_WIDTH / 2 - 40, SCREEN_HEIGHT / 2 + 10)
        self.draw_text("Press any key to restart", SCREEN_WIDTH / 2 - 90, SCREEN_HEIGHT / 2 + 50)
        pygame.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYUP:
                    waiting = False

if __name__ == "__main__":
    g = Game()
    g.show_start_screen()
    while g.running:
        g.new()
        g.show_go_screen()

    pygame.quit()
    sys.exit()
