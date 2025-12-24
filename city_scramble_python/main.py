import pygame
import sys
import random
import json
import os
from menu_system import MenuManager
from settings import *
from sprites import *
from pathfinding import PathfindingGrid
from spatial_hash import SpatialHash
from data_manager import DataManager
from network import ensure_server, GameClient, get_local_ip

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.SysFont("Arial", 24)
        self.small_font = pygame.font.SysFont("Arial", 18)  # For shop subtexts
        self.medium_font = pygame.font.SysFont("Arial", 26)  # Smaller for compact buttons
        self.large_font = pygame.font.SysFont("Arial", 48)
        
        self.menu_manager = MenuManager(self)
        self.running = True
        # Default maximum number of enemies; can be changed in the start menu
        self.max_enemies = 7
        # Sound effects using Windows beep (simple but works)
        self.sounds_enabled = False
        try:
            import winsound
            self.winsound = winsound
        except ImportError:
            self.sounds_enabled = False
            print("Sound not available on this system")
        
        # Data Manager initialization
        self.data_manager = DataManager()
        
        # Load values from DataManager
        self.total_score = self.data_manager.get('total_score', 0)
        self.saved_upgrades = self.data_manager.get('weapon_upgrades', {})
        self.total_upgrades_purchased = self.data_manager.get('total_upgrades_purchased', 0)
        self.owned_colors = self.data_manager.get('owned_colors', ['white'])
        self.selected_color = self.data_manager.get('selected_color', 'white')
        self.owned_bullet_colors = self.data_manager.get('owned_bullet_colors', ['white'])
        self.selected_bullet_color = self.data_manager.get('selected_bullet_color', 'white')
        self.owned_kill_animations = self.data_manager.get('owned_kill_animations', ['none'])
        self.selected_kill_animation = self.data_manager.get('selected_kill_animation', 'none')
        self.minimap_owned = self.data_manager.get('minimap_owned', False)
        self.minimap_active = self.data_manager.get('minimap_active', False)
        self.ai_aim_difficulty = self.data_manager.get('ai_aim_difficulty', 'normal')
        self.ai_dodge_difficulty = self.data_manager.get('ai_dodge_difficulty', 'normal')
        self.game_mode = self.data_manager.get('game_mode', 'classic')
        self.tutorial_completed = self.data_manager.get('tutorial_completed', False)
        self.sounds_owned = self.data_manager.get('sounds_owned', False)
        self.sounds_active = self.data_manager.get('sounds_active', False)
        self.owned_designs = self.data_manager.get('owned_designs', ['classic'])
        self.selected_design = self.data_manager.get('selected_design', 'classic')
        
        self.special_minimap_cost = 1000000
        self.special_sounds_cost = 1000000
        self.special_design_cost = 1000000
        
        # Design configuration
        self.designs = {
            'classic': {'name': 'Klassisch', 'img': None, 'color': DARK_GREY},
            'desert': {'name': 'Wüste', 'img': 'sand.webp', 'color': (235, 215, 175)},
            'grass': {'name': 'Wiese', 'img': 'grass.png', 'color': (50, 150, 50)},
            'winter': {'name': 'Winter', 'img': 'snow.png', 'color': (200, 230, 255)}
        }
        
        # Weapon upgrade system (only for player)
        self.weapon_upgrades = {
            weapon: {'fire_rate': 0, 'damage': 0, 'spawn_rate': 0}
            for weapon in WEAPONS.keys()
        }
        # Apply saved upgrades
        for weapon, upgrades in self.saved_upgrades.items():
            if weapon in self.weapon_upgrades:
                self.weapon_upgrades[weapon] = upgrades
        
        self.base_upgrade_cost = 500  # Base cost per upgrade
        
        # Character color system
        self.character_colors = {
            'white': {'name': 'Weiß', 'rgb': (255, 255, 255), 'cost': 0},  # Default, free
            'yellow': {'name': 'Gelb', 'rgb': (255, 255, 0), 'cost': 15000},
            'blue': {'name': 'Blau', 'rgb': (0, 100, 255), 'cost': 15000},
            'green': {'name': 'Grün', 'rgb': (0, 255, 0), 'cost': 15000},
            'black': {'name': 'Schwarz', 'rgb': (30, 30, 30), 'cost': 15000},
            'brown': {'name': 'Braun', 'rgb': (139, 69, 19), 'cost': 15000},
            'gold': {'name': 'Gold', 'rgb': (218, 165, 32), 'cost': 100000},
            'silver': {'name': 'Silber', 'rgb': (192, 192, 192), 'cost': 50000},
            'bronze': {'name': 'Bronze', 'rgb': (205, 127, 50), 'cost': 20000},
            'purple': {'name': 'Lila', 'rgb': (160, 32, 240), 'cost': 15000},
            'pink': {'name': 'Pink', 'rgb': (255, 105, 180), 'cost': 15000},
            'rainbow': {'name': 'Regenbogen', 'rgb': (255, 0, 0), 'cost': 1000000, 'animated': True}  # Special animated skin
        }
        
        # Bullet color system (same colors and prices as character)
        self.bullet_colors = self.character_colors.copy()  # Same color definitions
        
        # Kill animation system
        self.kill_animations = {
            'none': {'name': 'Keine', 'duration': 0, 'cost': 0},  # Default
            'bloodsplat': {'name': 'Blutfleck', 'duration': 1000, 'cost': 50000},  # 1 sec
            'flowers': {'name': 'Blumen', 'duration': 2000, 'cost': 175000},  # 2 sec
            'gravestone': {'name': 'Grabstein', 'duration': 2500, 'cost': 500000}  # 2.5 sec
        }
        
        # Music setup - separate files for menu and match
        # Menu music (start.mp3) - plays in start screen
        self.menu_music_file = os.path.join(os.path.dirname(__file__), "start.mp3")
        self.menu_music_loaded = False
        self.menu_music = None
        
        # Match music (Background.mp3) - plays during gameplay
        self.match_music_file = os.path.join(os.path.dirname(__file__), "Background.mp3")
        self.match_music_loaded = False
        
        # Second match sound layer (sound2.mp3) - plays parallel to match music at 75% quieter
        self.match_sound2_file = os.path.join(os.path.dirname(__file__), "sound2.mp3")
        self.match_sound2_loaded = False
        self.match_sound2 = None
        
        # Try to load menu music (optional - game works without it)
        try:
            self.menu_music = pygame.mixer.Sound(self.menu_music_file)
            self.menu_music.set_volume(0.5)
            self.menu_music_loaded = True
            # Only play if owned and active
            if self.sounds_owned and self.sounds_active:
                self.menu_music.play(-1)
                print(f"[OK] Menue-Musik '{self.menu_music_file}' erfolgreich geladen und gestartet")
            else:
                print(f"[OK] Menue-Musik '{self.menu_music_file}' geladen (stumm, da nicht gekauft/aktiv)")
        except (pygame.error, FileNotFoundError) as e:
            self.menu_music_loaded = False
            print(f"[INFO] Konnte Menue-Musik nicht laden: {e}")
            print(f"       Optional: Fuege 'start.mp3' zum Verzeichnis hinzu fuer Menue-Musik")
        
        # Load match music (will be played via pygame.mixer.music)
        try:
            pygame.mixer.music.load(self.match_music_file)
            pygame.mixer.music.set_volume(0.5)
            self.match_music_loaded = True
            print(f"[OK] Match-Musik '{self.match_music_file}' erfolgreich geladen")
        except (pygame.error, FileNotFoundError) as e:
            self.match_music_loaded = False
            print(f"[FEHLER] Konnte Match-Musik nicht laden: {e}")
            print(f"         Gesuchter Pfad: {self.match_music_file}")
        
        # Load second match sound layer (optional - plays parallel at 25% volume = 75% quieter)
        try:
            self.match_sound2 = pygame.mixer.Sound(self.match_sound2_file)
            self.match_sound2.set_volume(0.125)  # 0.5 * 0.25 = 0.125 (75% leiser als normal)
            self.match_sound2_loaded = True
            print(f"[OK] Match-Sound-Layer-2 '{self.match_sound2_file}' geladen (75% leiser)")
        except (pygame.error, FileNotFoundError) as e:
            self.match_sound2_loaded = False
            print(f"[INFO] Konnte Match-Sound-Layer-2 nicht laden: {e}")
            print(f"       Optional: Fuege 'sound2.mp3' zum Verzeichnis hinzu")

    def new(self, tutorial_mode=False):
        # Start a new game
        self.tutorial_mode = tutorial_mode
        self.tutorial_step = 0
        self.tutorial_progress = 0
        self.tutorial_shots_fired = 0
        self.tutorial_target_pos = None
        self.tutorial_message = ""
        
        self.all_sprites = CameraGroup(self)  # Use CameraGroup
        self.walls = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.upgrade_items = pygame.sprite.Group()  # For AI upgrades

        # Team mode groups
        self.team_allies = pygame.sprite.Group()  # Blue team (player + 4 AI)
        self.team_enemies = pygame.sprite.Group()  # Red team (5 AI)

        # Team mode variables
        if self.game_mode == 'team5v5':
            self.team_blue_score = 0
            self.team_red_score = 0
            self.match_start_time = pygame.time.get_ticks()
            self.match_duration = 180000  # 3 minutes in milliseconds
            self.team_respawn_queue = []  # (respawn_time, team, x, y)

            # Blue team spawn point (bottom-right)
            blue_spawn_x = MAP_WIDTH - 200
            blue_spawn_y = MAP_HEIGHT - 200

            # Red team spawn point (top-left)
            red_spawn_x = 100
            red_spawn_y = 100

            # Create player (blue team)
            self.player = Player(self, blue_spawn_x, blue_spawn_y)
            self.player.team = 'blue'
            self.player.image.fill((50, 50, 255))  # Blue color
            self.team_allies.add(self.player)

            # Create 4 blue AI teammates (always 4, regardless of max_enemies setting)
            for i in range(4):
                offset_x = random.randint(-100, 100)
                offset_y = random.randint(-100, 100)
                x = max(50, min(MAP_WIDTH - 50, blue_spawn_x + offset_x))
                y = max(50, min(MAP_HEIGHT - 50, blue_spawn_y + offset_y))
                TeamAI(self, x, y, team='blue', member_index=i+1)

            # Create 5 red AI enemies (always 5, regardless of max_enemies setting)
            for i in range(5):
                offset_x = random.randint(-100, 100)
                offset_y = random.randint(-100, 100)
                x = max(50, min(MAP_WIDTH - 50, red_spawn_x + offset_x))
                y = max(50, min(MAP_HEIGHT - 50, red_spawn_y + offset_y))
                red_ai = TeamAI(self, x, y, team='red', member_index=i)
                print(f"DEBUG: Created red TeamAI #{i+1}, in team_enemies: {red_ai in self.team_enemies.sprites()}")

            print(f"DEBUG: Total team_enemies: {len(self.team_enemies)}")
            print(f"DEBUG: Total team_allies: {len(self.team_allies)}")
        else:
            # Normal spawn for non-team modes
            self.player = Player(self, MAP_WIDTH - 100, MAP_HEIGHT - 100)  # Spawn in bottom-right corner

        # Enemy upgrade storage - persists across respawns
        # Format: {enemy_index: {'fire_rate_bonus': 0, 'health_pickups': 0}}
        if not hasattr(self, 'enemy_upgrades'):
            self.enemy_upgrades = {}
        
        # Track total enemy count pickups (max 10)
        if not hasattr(self, 'enemy_count_pickups'):
            self.enemy_count_pickups = 0
        
        # Initial Enemies (use max_enemies) - SKIP IN TUTORIAL AND TEAM MODE
        if not self.tutorial_mode and self.game_mode != 'team5v5':
            for i in range(self.max_enemies):
                while True:
                    # Spawn in top-left corner area
                    x = random.randint(0, MAP_WIDTH // 4)
                    y = random.randint(0, MAP_HEIGHT // 4)
                    rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
                    if not any(wall.rect.colliderect(rect) for wall in self.walls):
                        enemy = Enemy(self, x, y)
                        enemy.enemy_index = i  # Assign unique index
                        # Restore upgrades if they exist
                        if i in self.enemy_upgrades:
                            if 'fire_rate_bonus' in self.enemy_upgrades[i]:
                                enemy.fire_rate_bonus = self.enemy_upgrades[i]['fire_rate_bonus']
                            if 'health_pickups' in self.enemy_upgrades[i]:
                                enemy.health_pickups = self.enemy_upgrades[i]['health_pickups']
                        break

        # Obstacle respawn queue: list of (respawn_time, x, y, w, h)
        self.obstacle_respawn_queue = []
        
        # Destroyed building zones: list of pygame.Rect for areas where buildings are destroyed
        # Items should not spawn in these zones until building respawns
        self.destroyed_building_zones = []

        if self.game_mode == 'team5v5':
            # FIXED MAP LAYOUT FOR 5VS5
            # Create defensive cover around Blue spawn (Bottom-Right)
            blue_base_x = MAP_WIDTH - 200
            blue_base_y = MAP_HEIGHT - 200
            
            # Defensive walls (U-shape pointing towards center)
            # Top wall
            Obstacle(self, blue_base_x - 300, blue_base_y - 200, 400, 50)
            # Left wall
            Obstacle(self, blue_base_x - 300, blue_base_y - 200, 50, 400)
            # Bottom wall
            Obstacle(self, blue_base_x - 300, blue_base_y + 150, 400, 50)
            
            # Some scattered cover in the middle field
            Obstacle(self, MAP_WIDTH // 2 - 100, MAP_HEIGHT // 2 - 100, 200, 200) # Center block
            Obstacle(self, MAP_WIDTH // 2 - 400, MAP_HEIGHT // 2 + 200, 100, 100)
            Obstacle(self, MAP_WIDTH // 2 + 300, MAP_HEIGHT // 2 - 300, 100, 100)
            
            # Create defensive cover around Red spawn (Top-Left)
            red_base_x = 100
            red_base_y = 100
            
            # Defensive walls (U-shape pointing towards center)
            # Bottom wall
            Obstacle(self, red_base_x + 100, red_base_y + 300, 400, 50)
            # Right wall
            Obstacle(self, red_base_x + 450, red_base_y + 100, 50, 400)
            # Top wall
            Obstacle(self, red_base_x + 100, red_base_y - 100, 400, 50)

        else:
            # Create some obstacles (randomly scattered for now)
            # In tutorial, create a controlled environment (or just fewer obstacles)
            num_obstacles = 5 if self.tutorial_mode else 20
            for _ in range(num_obstacles):
                x = random.randint(0, MAP_WIDTH - 100)
                y = random.randint(0, MAP_HEIGHT - 100)
                w = random.randint(50, 200)
                h = random.randint(50, 200)
                # Ensure not spawning on player in tutorial
                if self.tutorial_mode:
                    if abs(x - self.player.pos.x) < 300 and abs(y - self.player.pos.y) < 300:
                        continue
                Obstacle(self, x, y, w, h)

        # Initialize pathfinding grid after all obstacles are created
        self.pathfinding_grid = PathfindingGrid(MAP_WIDTH, MAP_HEIGHT, self.walls, cell_size=40)
        
        # Initialize Spatial Hash Grid for Collision Optimization
        self.spatial_hash = SpatialHash(cell_size=100)
        # Add static walls to spatial hash once (if they don't move)
        for wall in self.walls:
            self.spatial_hash.add(wall)

        # Spawn weapons - SKIP IN TUTORIAL (spawned by script)
        if not self.tutorial_mode:
            self.spawn_weapons()

        self.score = 0
        self.start_time = pygame.time.get_ticks()
        self.last_enemy_spawn = pygame.time.get_ticks()
        self.last_weapon_spawn = pygame.time.get_ticks()
        self.last_upgrade_spawn = pygame.time.get_ticks()  # For AI upgrades
        
        
        # Sanfter Übergang: Menü-Musik ausblenden, Match-Musik einblenden
        if self.menu_music_loaded and self.menu_music:
            # Fade-Out der Menü-Musik über 1.5 Sekunden
            self.menu_music.fadeout(1500)  # 1500ms = 1.5 Sekunden
            print("[OK] Menue-Musik wird ausgeblendet (1.5s)...")
            # Kurze Pause, damit Fade-Out abgeschlossen wird
            pygame.time.wait(1500)
        
        # Starte Match-Musik nur wenn gekauft und aktiv
        if self.match_music_loaded and self.sounds_owned and self.sounds_active:
            try:
                # Starte Match-Musik mit Fade-In über 2 Sekunden
                pygame.mixer.music.play(-1, fade_ms=2000)  # fade_ms = 2000ms Fade-In
                print("[OK] Match-Musik wird eingeblendet (2s) und laeuft in Dauerschleife")
            except Exception as e:
                print(f"[FEHLER] Fehler beim Starten der Match-Musik: {e}")
        else:
            print("[INFO] Match-Musik nicht geladen oder nicht gekauft, spiele ohne Musik")
        
        # Starte parallel den zweiten Sound-Layer (75% leiser) nur wenn gekauft und aktiv
        if self.match_sound2_loaded and self.match_sound2 and self.sounds_owned and self.sounds_active:
            try:
                self.match_sound2.play(-1, fade_ms=2000)  # -1 = Dauerschleife, 2s Fade-In
                print("[OK] Match-Sound-Layer-2 parallel gestartet (75% leiser, 2s Fade-In)")
            except Exception as e:
                print(f"[FEHLER] Fehler beim Starten von Sound-Layer-2: {e}")

        self.run()
        
        # Add score to total score and save (unless in tutorial)
        if not self.tutorial_mode:
            self.total_score += self.score
            self.save_total_score()
            print(f"[DataManager] Match score {self.score} added to total score. Total: {self.total_score}")

        # Fade-Out beider Match-Sounds nach Match-Ende (2 Sekunden)
        pygame.mixer.music.fadeout(2000)  # 2000ms = 2 Sekunden
        if self.match_sound2_loaded and self.match_sound2:
            self.match_sound2.fadeout(2000)
        print("[OK] Match-Musik und Sound-Layer-2 werden ausgeblendet (2s)...")
        # Warte kurz, damit Fade-Out abgeschlossen wird
        pygame.time.wait(2000)
        # Menü-Musik wird in show_start_screen() wieder gestartet

    def spawn_weapons(self):
        for _ in range(WEAPON_SPAWN_COUNT):
            for attempt in range(100):  # Try up to 100 times to find valid position
                x = random.randint(0, MAP_WIDTH - WEAPON_SIZE)
                y = random.randint(0, MAP_HEIGHT - WEAPON_SIZE)
                rect = pygame.Rect(x, y, WEAPON_SIZE, WEAPON_SIZE)
                # Check if weapon would spawn inside a wall or destroyed building zone
                if (not any(wall.rect.colliderect(rect) for wall in self.walls) and
                    not any(zone.colliderect(rect) for zone in self.destroyed_building_zones)):
                    weapon = WeaponItem(self, x, y)
                    # Spawn additional copies based on spawn rate upgrade
                    spawn_bonus = self.weapon_upgrades[weapon.type]['spawn_rate']
                    if spawn_bonus > 0 and random.random() < spawn_bonus * 0.1:
                        # 10% chance per upgrade level to spawn an extra copy nearby
                        for extra_attempt in range(50):
                            offset_x = random.randint(50, 100)
                            offset_y = random.randint(50, 100)
                            x2 = max(0, min(MAP_WIDTH - WEAPON_SIZE, x + offset_x))
                            y2 = max(0, min(MAP_HEIGHT - WEAPON_SIZE, y + offset_y))
                            rect2 = pygame.Rect(x2, y2, WEAPON_SIZE, WEAPON_SIZE)
                            # Also check extra weapon doesn't spawn in wall or destroyed zone
                            if (not any(wall.rect.colliderect(rect2) for wall in self.walls) and
                                not any(zone.colliderect(rect2) for zone in self.destroyed_building_zones)):
                                WeaponItem(self, x2, y2, weapon.type)
                                break
                    break  # Found valid position, move to next weapon

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
        
        # Apply fire rate upgrade for player
        fire_rate = weapon_stats['rate']
        if isinstance(sprite, Player):
            # Reduce fire rate by 100ms per upgrade (faster shooting)
            fire_rate = max(100, fire_rate - (self.weapon_upgrades[weapon_name]['fire_rate'] * 100))
        
        if now - sprite.last_shot > fire_rate:
            sprite.last_shot = now
            # Determine direction
            if isinstance(sprite, Player):
                if self.tutorial_mode:
                    self.tutorial_shots_fired += 1
                mx, my = pygame.mouse.get_pos()
                camera_offset = self.all_sprites.offset
                world_mouse_pos = vec(mx, my) + camera_offset
                dir = world_mouse_pos - sprite.pos
                if dir.length() > 0:
                    dir = dir.normalize()
                owner = 'player'
            else:
                mx, my = target_pos
                enemy_center = vec(sprite.rect.centerx, sprite.rect.centery)
                dir = vec(mx, my) - enemy_center
                if dir.length() > 0:
                    dir = dir.normalize()
                owner = 'enemy'
            
            # Apply damage upgrade for player
            damage = weapon_stats['damage']
            if isinstance(sprite, Player):
                # Increase damage by 10% per upgrade
                damage = int(damage * (1 + self.weapon_upgrades[weapon_name]['damage'] * 0.1))
            # Enemies no longer have damage bonus
            
            # Set projectile color based on owner
            if isinstance(sprite, Player):
                # Use selected bullet color for player
                projectile_color = self.bullet_colors[self.selected_bullet_color]['rgb']
                is_rainbow = self.selected_bullet_color == 'rainbow'
            else:
                projectile_color = (255, 50, 50)  # Red for enemies
                is_rainbow = False
            
            # Create projectiles
            for _ in range(weapon_stats['count']):
                spread = random.uniform(-weapon_stats['spread'], weapon_stats['spread'])
                vel = dir.rotate(spread)
                if weapon_name == 'grenade':
                    Grenade(self, sprite.rect.centerx, sprite.rect.centery, vel.x, vel.y, owner,
                           damage, weapon_stats['speed'], weapon_stats['lifetime'], projectile_color, is_rainbow)
                else:
                    Projectile(self, sprite.rect.centerx, sprite.rect.centery, vel.x, vel.y, owner,
                                damage, weapon_stats['speed'], weapon_stats['lifetime'], projectile_color, is_rainbow)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

    def shoot_at_building(self, sprite, target_pos):
        """Shoot at buildings with right-click"""
        weapon_name = sprite.weapon
        weapon_stats = WEAPONS[weapon_name]
        now = pygame.time.get_ticks()

        # Apply fire rate upgrade for player
        fire_rate = weapon_stats['rate']
        if isinstance(sprite, Player):
            fire_rate = max(100, fire_rate - (self.weapon_upgrades[weapon_name]['fire_rate'] * 100))

        if now - sprite.last_shot > fire_rate:
            sprite.last_shot = now

            # Direction to target
            dir = vec(target_pos.x, target_pos.y) - sprite.pos
            if dir.length() > 0:
                dir = dir.normalize()

            # Create special building-destroying projectiles
            damage = 1  # 1 damage per hit, 10 hits to destroy
            for _ in range(weapon_stats['count']):
                spread = random.uniform(-weapon_stats['spread'], weapon_stats['spread'])
                vel = dir.rotate(spread)
                # Create projectile with special owner flag
                BuildingProjectile(self, sprite.rect.centerx, sprite.rect.centery, vel.x, vel.y,
                                 damage, weapon_stats['speed'], weapon_stats['lifetime'], (255, 165, 0))  # Orange color

    def shoot_team(self, sprite, target_pos, team):
        """Shoot for team mode with team-colored projectiles"""
        weapon_name = sprite.weapon
        weapon_stats = WEAPONS[weapon_name]
        now = pygame.time.get_ticks()

        if now - sprite.last_shot > weapon_stats['rate']:
            # Apply fire rate upgrade for player
            fire_rate = weapon_stats['rate']
            if sprite == self.player:
                fire_rate = max(100, fire_rate - (self.weapon_upgrades[weapon_name]['fire_rate'] * 100))
            
            if now - sprite.last_shot > fire_rate:
                sprite.last_shot = now

                # Direction to target
                mx, my = target_pos
                sprite_center = vec(sprite.rect.centerx, sprite.rect.centery)
                dir = vec(mx, my) - sprite_center
                if dir.length() > 0:
                    dir = dir.normalize()

                damage = weapon_stats['damage']
                # Apply damage upgrade for player
                if sprite == self.player:
                     damage = int(damage * (1 + self.weapon_upgrades[weapon_name]['damage'] * 0.1))

            # Set projectile color based on team
            projectile_color = (50, 50, 255) if team == 'blue' else (255, 50, 50)
            owner = f'team_{team}'

            print(f"DEBUG: shoot_team called by {team} team, owner={owner}, damage={damage}")

            # Create projectiles
            for _ in range(weapon_stats['count']):
                spread = random.uniform(-weapon_stats['spread'], weapon_stats['spread'])
                vel = dir.rotate(spread)
                if weapon_name == 'grenade':
                    proj = Grenade(self, sprite.rect.centerx, sprite.rect.centery, vel.x, vel.y, owner,
                           damage, weapon_stats['speed'], weapon_stats['lifetime'], projectile_color, False)
                else:
                    proj = Projectile(self, sprite.rect.centerx, sprite.rect.centery, vel.x, vel.y, owner,
                              damage, weapon_stats['speed'], weapon_stats['lifetime'], projectile_color, False)
                print(f"DEBUG: Created projectile with owner={proj.owner}")

    def schedule_team_respawn(self, team, x, y):
        """Schedule a team member to respawn after delay"""
        respawn_time = pygame.time.get_ticks() + 5000  # 5 second respawn delay
        self.team_respawn_queue.append((respawn_time, team, x, y))

    def update(self):
        # Update Spatial Hash for dynamic entities
        # Clear dynamic entities from hash (only if we track them separately, 
        # but for simplicity we can just clear and rebuild or remove/add moving ones)
        # Rebuilding is safer to avoid stale references
        self.spatial_hash = SpatialHash(cell_size=100)
        # Re-add static walls
        for wall in self.walls:
            self.spatial_hash.add(wall)
        # Add dynamic entities
        for sprite in self.enemies:
            self.spatial_hash.add(sprite)
        for sprite in self.team_enemies:
            self.spatial_hash.add(sprite)
        for sprite in self.team_allies:
            self.spatial_hash.add(sprite)
        for sprite in self.projectiles:
            self.spatial_hash.add(sprite)
            
        self.all_sprites.update()

        # Check for game over in survival mode
        if self.game_mode == 'survival' and self.player.hit_count >= 10:
            self.playing = False
            return

        # Check for time up in team5v5 mode
        if self.game_mode == 'team5v5':
            elapsed = pygame.time.get_ticks() - self.match_start_time
            if elapsed >= self.match_duration:
                self.playing = False
                return

            # Check if player died in team mode - respawn after 5 seconds
            if self.player.hit_count >= 10:
                if not hasattr(self, 'player_respawn_time'):
                    self.player_respawn_time = pygame.time.get_ticks() + 5000
                elif pygame.time.get_ticks() >= self.player_respawn_time:
                    # Respawn player at blue spawn point
                    blue_spawn_x = MAP_WIDTH - 200
                    blue_spawn_y = MAP_HEIGHT - 200
                    offset_x = random.randint(-100, 100)
                    offset_y = random.randint(-100, 100)
                    self.player.pos.x = max(50, min(MAP_WIDTH - 50, blue_spawn_x + offset_x))
                    self.player.pos.y = max(50, min(MAP_HEIGHT - 50, blue_spawn_y + offset_y))
                    self.player.rect.x = self.player.pos.x
                    self.player.rect.y = self.player.pos.y
                    self.player.hit_count = 0
                    del self.player_respawn_time

            # Process team respawn queue
            now = pygame.time.get_ticks()
            for item in self.team_respawn_queue[:]:
                respawn_time, team, x, y = item
                if now >= respawn_time:
                    # Respawn with random offset
                    offset_x = random.randint(-100, 100)
                    offset_y = random.randint(-100, 100)
                    spawn_x = max(50, min(MAP_WIDTH - 50, x + offset_x))
                    spawn_y = max(50, min(MAP_HEIGHT - 50, y + offset_y))
                    TeamAI(self, spawn_x, spawn_y, team=team, member_index=random.randint(0, 4))
                    self.team_respawn_queue.remove(item)

        if self.tutorial_mode:
            self.update_tutorial()
            # Still allow building respawn in tutorial
            now = pygame.time.get_ticks()
            # Respawn broken buildings
            for item in self.obstacle_respawn_queue[:]:
                respawn_time, x, y, w, h = item
                if now > respawn_time:
                    Obstacle(self, x, y, w, h)
                    self.obstacle_respawn_queue.remove(item)
                    # Remove from destroyed zones
                    for zone in self.destroyed_building_zones[:]:
                        if zone.x == x and zone.y == y and zone.width == w and zone.height == h:
                            self.destroyed_building_zones.remove(zone)
            return

        # Enemy Respawn Logic (use max_enemies) - SKIP IN TEAM MODE
        if self.game_mode != 'team5v5' and len(self.enemies) < self.max_enemies:
            now = pygame.time.get_ticks()
            if now - self.last_enemy_spawn > ENEMY_RESPAWN_TIME:
                self.last_enemy_spawn = now
                # Find which enemy index is missing
                existing_indices = {enemy.enemy_index for enemy in self.enemies if hasattr(enemy, 'enemy_index')}
                missing_index = None
                for i in range(self.max_enemies):
                    if i not in existing_indices:
                        missing_index = i
                        break
                
                while True:
                    # Spawn in top-left corner area
                    x = random.randint(0, MAP_WIDTH // 4)
                    y = random.randint(0, MAP_HEIGHT // 4)
                    rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
                    if not any(wall.rect.colliderect(rect) for wall in self.walls):
                        enemy = Enemy(self, x, y)
                        if missing_index is not None:
                            enemy.enemy_index = missing_index
                            # Restore upgrades if they exist
                            if missing_index in self.enemy_upgrades:
                                if 'fire_rate_bonus' in self.enemy_upgrades[missing_index]:
                                    enemy.fire_rate_bonus = self.enemy_upgrades[missing_index]['fire_rate_bonus']
                                if 'health_pickups' in self.enemy_upgrades[missing_index]:
                                    enemy.health_pickups = self.enemy_upgrades[missing_index]['health_pickups']
                        break
        # Weapon Respawn Logic
        now = pygame.time.get_ticks()
        if now - self.last_weapon_spawn > WEAPON_RESPAWN_TIME:
            self.last_weapon_spawn = now
            self.spawn_weapons()

        # Upgrade Spawn Logic (every 5 seconds)
        if now - self.last_upgrade_spawn > 5000:  # 5 seconds
            self.last_upgrade_spawn = now
            # Spawn upgrade at random location (not in walls or destroyed building zones)
            for attempt in range(100):  # Try up to 100 times to find valid position
                x = random.randint(0, MAP_WIDTH - 30)
                y = random.randint(0, MAP_HEIGHT - 30)
                rect = pygame.Rect(x, y, 30, 30)
                # Check if upgrade would spawn inside a wall or destroyed building zone
                if (not any(wall.rect.colliderect(rect) for wall in self.walls) and
                    not any(zone.colliderect(rect) for zone in self.destroyed_building_zones)):
                    UpgradeItem(self, x, y)
                    break
        
        # Weapon Pickup Logic - Player
        hits = pygame.sprite.spritecollide(self.player, self.items, True)
        for hit in hits:
            # Drop old weapon at offset position before picking up new one
            if self.player.weapon != 'pistol':  # Don't drop starting weapon
                # Drop weapon to the side with random offset
                offset_x = random.randint(40, 80) * random.choice([-1, 1])
                offset_y = random.randint(40, 80) * random.choice([-1, 1])
                drop_x = max(0, min(MAP_WIDTH - WEAPON_SIZE, self.player.pos.x + offset_x))
                drop_y = max(0, min(MAP_HEIGHT - WEAPON_SIZE, self.player.pos.y + offset_y))
                WeaponItem(self, drop_x, drop_y, self.player.weapon)
            self.player.weapon = hit.type
            if self.game_mode != 'team5v5':
                self.score += 10

        # Weapon Pickup Logic - Team Members (in team5v5 mode)
        if self.game_mode == 'team5v5':
            for team_member in list(self.team_allies) + list(self.team_enemies):
                if team_member == self.player:
                    continue  # Player already handled above
                hits = pygame.sprite.spritecollide(team_member, self.items, True)
                for hit in hits:
                    # Drop old weapon
                    if team_member.weapon != 'pistol':
                        offset_x = random.randint(40, 80) * random.choice([-1, 1])
                        offset_y = random.randint(40, 80) * random.choice([-1, 1])
                        drop_x = max(0, min(MAP_WIDTH - WEAPON_SIZE, team_member.pos.x + offset_x))
                        drop_y = max(0, min(MAP_HEIGHT - WEAPON_SIZE, team_member.pos.y + offset_y))
                        WeaponItem(self, drop_x, drop_y, team_member.weapon)
                    team_member.weapon = hit.type

        # Weapon Pickup Logic - Enemies (normal modes)
        if self.game_mode != 'team5v5':
            for enemy in self.enemies:
                hits = pygame.sprite.spritecollide(enemy, self.items, True)
                for hit in hits:
                    # Drop old weapon at offset position before picking up new one
                    if enemy.weapon != 'pistol':  # Don't drop starting weapon
                        # Drop weapon to the side with random offset
                        offset_x = random.randint(40, 80) * random.choice([-1, 1])
                        offset_y = random.randint(40, 80) * random.choice([-1, 1])
                        drop_x = max(0, min(MAP_WIDTH - WEAPON_SIZE, enemy.pos.x + offset_x))
                        drop_y = max(0, min(MAP_HEIGHT - WEAPON_SIZE, enemy.pos.y + offset_y))
                        WeaponItem(self, drop_x, drop_y, enemy.weapon)
                    enemy.weapon = hit.type
                    enemy.update_color()

                # Upgrade Pickup Logic - Enemies only
                upgrade_hits = pygame.sprite.spritecollide(enemy, self.upgrade_items, True)
                for upgrade in upgrade_hits:
                    # Get or create enemy index
                    if not hasattr(enemy, 'enemy_index'):
                        enemy.enemy_index = len(self.enemies) - 1

                    # Initialize upgrade storage for this enemy if needed
                    if enemy.enemy_index not in self.enemy_upgrades:
                        self.enemy_upgrades[enemy.enemy_index] = {
                            'fire_rate_bonus': 0,
                            'health_pickups': 0
                        }

                    if upgrade.upgrade_type == 'fire_rate':
                        # Reduce fire rate (faster shooting)
                        if not hasattr(enemy, 'fire_rate_bonus'):
                            enemy.fire_rate_bonus = 0
                        enemy.fire_rate_bonus += 100  # 100ms faster
                        self.enemy_upgrades[enemy.enemy_index]['fire_rate_bonus'] = enemy.fire_rate_bonus
                    elif upgrade.upgrade_type == 'enemy_count':
                        # Increase enemy count (max 10 pickups)
                        if self.enemy_count_pickups < 10:
                            self.enemy_count_pickups += 1
                            # Every 2 pickups, spawn a new enemy
                            if self.enemy_count_pickups % 2 == 0:
                                self.max_enemies += 1
                                # Spawn new enemy immediately
                                for attempt in range(100):  # Try up to 100 times
                                    # Spawn in top-left corner area
                                    x = random.randint(0, MAP_WIDTH // 4)
                                    y = random.randint(0, MAP_HEIGHT // 4)
                                    rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
                                    if not any(wall.rect.colliderect(rect) for wall in self.walls):
                                        new_enemy = Enemy(self, x, y)
                                        new_enemy.enemy_index = self.max_enemies - 1
                                        break
                    elif upgrade.upgrade_type == 'health':
                        # Restore health
                        enemy.hp = min(50, enemy.hp + 20)  # +20 HP, max 50
                        # Track health pickups for display
                        if not hasattr(enemy, 'health_pickups'):
                            enemy.health_pickups = 0
                        enemy.health_pickups += 1
                        self.enemy_upgrades[enemy.enemy_index]['health_pickups'] = enemy.health_pickups
        
        # Obstacle Respawn Logic
        now = pygame.time.get_ticks()
        # Check if any obstacles should respawn
        obstacles_to_remove = []
        for i, (respawn_time, x, y, w, h) in enumerate(self.obstacle_respawn_queue):
            if now >= respawn_time:
                # Respawn the obstacle
                Obstacle(self, x, y, w, h)
                obstacles_to_remove.append(i)
                # Remove the destroyed zone for this building
                zone_rect = pygame.Rect(x, y, w, h)
                self.destroyed_building_zones = [zone for zone in self.destroyed_building_zones 
                                                 if zone != zone_rect]
        
        # Remove respawned obstacles from queue (in reverse to avoid index issues)
        for i in reversed(obstacles_to_remove):
            self.obstacle_respawn_queue.pop(i)
        
        # Game Over Check
        if self.player.hit_count >= 10:
            self.playing = False

    def update_tutorial(self):
        # Tutorial State Machine
        
        # Step 0: Movement
        if self.tutorial_step == 0:
            self.tutorial_message = "Bewege dich mit WASD oder Pfeiltasten"
            if self.player.vel.length() > 0:
                self.tutorial_progress += 1
            if self.tutorial_progress > 60:  # Ca. 1 Sekunde Bewegung
                self.tutorial_step = 1
                self.tutorial_progress = 0
                self.tutorial_shots_fired = 0  # Reset for next step
        
        # Step 1: Shooting
        elif self.tutorial_step == 1:
            shots_needed = 3
            self.tutorial_message = f"Schieße {shots_needed} mal mit LINKSKLICK ({self.tutorial_shots_fired}/{shots_needed})"
            if self.tutorial_shots_fired >= shots_needed:
                self.tutorial_step = 2
                self.tutorial_progress = 0
                self.last_destroyed_buildings_count = len(self.obstacle_respawn_queue)
        
        # Step 2: Destruction
        elif self.tutorial_step == 2:
            self.tutorial_message = "Zerstöre eine Wand mit RECHTSKLICK (10 Treffer)"
            # Check if a new building was destroyed
            if len(self.obstacle_respawn_queue) > self.last_destroyed_buildings_count:
                self.tutorial_step = 3
                self.tutorial_progress = 0
                # Spawn a weapon nearby
                spawn_pos = self.player.pos + vec(100, 0)
                # Ensure within bounds
                x = max(50, min(MAP_WIDTH - 50, spawn_pos.x))
                y = max(50, min(MAP_HEIGHT - 50, spawn_pos.y))
                WeaponItem(self, x, y, 'shotgun')
                self.tutorial_weapon_spawned = True
        
        # Step 3: Weapon Pickup
        elif self.tutorial_step == 3:
            self.tutorial_message = "Sammle die grüne Shotgun ein (einfach drüberlaufen)"
            
            # ALLOW PICKUP IN TUTORIAL
            hits = pygame.sprite.spritecollide(self.player, self.items, True)
            for hit in hits:
                self.player.weapon = hit.type
            
            if self.player.weapon == 'shotgun':
                self.tutorial_step = 4
                self.tutorial_progress = 0
                # Spawn a dummy enemy
                spawn_pos = self.player.pos + vec(0, -300)
                x = max(50, min(MAP_WIDTH - 50, spawn_pos.x))
                y = max(50, min(MAP_HEIGHT - 50, spawn_pos.y))
                enemy = Enemy(self, x, y)
                # Make enemy weaker or passive?
                enemy.hit_count = 0 # 3 hits normally
                # Enemy in tutorial behaves normally but is alone
        
        # Step 4: Combat
        elif self.tutorial_step == 4:
            self.tutorial_message = "Besiege den Gegner!"
            if len(self.enemies) == 0:
                self.tutorial_step = 5
                self.tutorial_progress = 0
        
        # Step 5: Completion
        elif self.tutorial_step == 5:
            self.tutorial_message = "Gut gemacht! Drücke RECHTSKLICK zum Beenden"
            if pygame.mouse.get_pressed()[2]:  # Right click
                self.tutorial_completed = True
                self.save_total_score()
                self.playing = False
                self.menu_manager.show_message_box("Tutorial Abgeschlossen", "Du bist bereit für das Spiel!")

    def draw(self):
        self.screen.fill(DARK_GREY)
        self.all_sprites.custom_draw(self.player)
        
        # Tutorial Overlay
        if self.tutorial_mode:
            # Semi-transparent bar at bottom
            s = pygame.Surface((SCREEN_WIDTH, 60))
            s.set_alpha(180)
            s.fill((0, 0, 0))
            self.screen.blit(s, (0, SCREEN_HEIGHT - 60))
            
            # Message
            msg_surf = self.medium_font.render(self.tutorial_message, True, (255, 255, 0))
            msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            self.screen.blit(msg_surf, msg_rect)
        
        # HUD
        if self.game_mode == 'team5v5':
            # Team mode HUD
            # Timer (center top)
            elapsed = pygame.time.get_ticks() - self.match_start_time
            remaining = max(0, self.match_duration - elapsed)
            minutes = remaining // 60000
            seconds = (remaining % 60000) // 1000
            timer_text = f"{minutes}:{seconds:02d}"
            timer_surf = self.large_font.render(timer_text, True, WHITE)
            self.screen.blit(timer_surf, (SCREEN_WIDTH // 2 - 50, 10))

            # Team scores (top corners)
            blue_score_text = f"BLAU: {self.team_blue_score}"
            red_score_text = f"ROT: {self.team_red_score}"
            blue_surf = self.font.render(blue_score_text, True, (50, 50, 255))
            red_surf = self.font.render(red_score_text, True, (255, 50, 50))
            self.screen.blit(blue_surf, (10, 10))
            self.screen.blit(red_surf, (SCREEN_WIDTH - 150, 10))

            # Weapon and hits info
            self.draw_text(f"Weapon: {self.player.weapon.upper()}", 10, SCREEN_HEIGHT - 30)
            self.draw_text(f"Hits: {self.player.hit_count}/10", 10, SCREEN_HEIGHT - 60)
        else:
            # Normal mode HUD
            if not self.tutorial_mode:
                self.draw_text(f"Score: {self.score}", 10, 10)
            self.draw_text(f"Weapon: {self.player.weapon.upper()}", 10, SCREEN_HEIGHT - 30)
            self.draw_text(f"Hits: {self.player.hit_count}/10", 10, SCREEN_HEIGHT - 60)

            # Enemy Upgrades Display at top
            self.draw_enemy_upgrades()
        
        # Mini-Map (top-right corner) - only if owned AND active
        if self.minimap_owned and self.minimap_active:
            self.draw_minimap()
        
        pygame.display.flip()
    
    def draw_minimap(self):
        """Draw a mini-map in the top-right corner showing buildings, enemies, and player"""
        # Mini-map dimensions and position
        minimap_width = 200
        minimap_height = int(minimap_width * (MAP_HEIGHT / MAP_WIDTH))  # Keep aspect ratio
        minimap_x = SCREEN_WIDTH - minimap_width - 10  # 10px from right edge
        minimap_y = 50  # Below the enemy upgrades display
        
        # Scaling factors
        scale_x = minimap_width / MAP_WIDTH
        scale_y = minimap_height / MAP_HEIGHT
        
        # Draw background and border
        minimap_rect = pygame.Rect(minimap_x, minimap_y, minimap_width, minimap_height)
        pygame.draw.rect(self.screen, (20, 20, 20), minimap_rect)  # Dark background
        pygame.draw.rect(self.screen, WHITE, minimap_rect, 2)  # White border
        
        # Draw obstacles (buildings) on mini-map
        for wall in self.walls:
            scaled_x = minimap_x + int(wall.rect.x * scale_x)
            scaled_y = minimap_y + int(wall.rect.y * scale_y)
            scaled_w = max(2, int(wall.rect.width * scale_x))  # Minimum 2px width
            scaled_h = max(2, int(wall.rect.height * scale_y))  # Minimum 2px height
            pygame.draw.rect(self.screen, (80, 80, 80), (scaled_x, scaled_y, scaled_w, scaled_h))
        
        # Draw enemies on mini-map
        if self.game_mode == 'team5v5':
            # Draw red team (enemies)
            for enemy in self.team_enemies:
                scaled_x = minimap_x + int(enemy.pos.x * scale_x)
                scaled_y = minimap_y + int(enemy.pos.y * scale_y)
                pygame.draw.circle(self.screen, RED, (scaled_x, scaled_y), 3)
            
            # Draw blue team (allies) - excluding player which is drawn later
            for ally in self.team_allies:
                if ally != self.player:
                    scaled_x = minimap_x + int(ally.pos.x * scale_x)
                    scaled_y = minimap_y + int(ally.pos.y * scale_y)
                    pygame.draw.circle(self.screen, (100, 100, 255), (scaled_x, scaled_y), 3) # Lighter blue
        else:
            for enemy in self.enemies:
                scaled_x = minimap_x + int(enemy.pos.x * scale_x)
                scaled_y = minimap_y + int(enemy.pos.y * scale_y)
                pygame.draw.circle(self.screen, RED, (scaled_x, scaled_y), 3)  # 3px red circles
        
        # Draw player on mini-map
        player_scaled_x = minimap_x + int(self.player.pos.x * scale_x)
        player_scaled_y = minimap_y + int(self.player.pos.y * scale_y)
        pygame.draw.circle(self.screen, GREEN, (player_scaled_x, player_scaled_y), 4)  # 4px green circle
    
    def draw_enemy_upgrades(self):
        """Display enemy upgrade statistics at top of screen"""
        # Count total upgrades for all enemies
        total_fire_rate = 0
        total_health_pickups = 0
        
        for enemy in self.enemies:
            if hasattr(enemy, 'fire_rate_bonus'):
                total_fire_rate += enemy.fire_rate_bonus // 100  # Convert ms to count
            if hasattr(enemy, 'health_pickups'):
                total_health_pickups += enemy.health_pickups
        
        # Display at top center - always visible
        y_offset = 10
        x_start = SCREEN_WIDTH // 2 - 250
        
        # Title
        self.draw_text("KI-Upgrades:", x_start, y_offset, (255, 215, 0))
        
        # Fire rate upgrades (yellow) - always show
        self.draw_text(f"Feuerrate: {total_fire_rate}x", x_start + 120, y_offset, (255, 200, 0))
        
        # Enemy count pickups (purple) - always show
        self.draw_text(f"Gegner: {self.enemy_count_pickups}/10", x_start + 260, y_offset, (200, 50, 255))
        
        # Health pickups (green) - always show
        self.draw_text(f"Heilung: {total_health_pickups}x", x_start + 390, y_offset, (50, 255, 50))

    def draw_text(self, text, x, y, color=WHITE):
        surface = self.font.render(text, True, color)
        self.screen.blit(surface, (x, y))
    
    def schedule_obstacle_respawn(self, x, y, w, h):
        """Schedule an obstacle to respawn after 20 seconds"""
        respawn_time = pygame.time.get_ticks() + 20000  # 20 seconds
        self.obstacle_respawn_queue.append((respawn_time, x, y, w, h))
        # Add destroyed zone to prevent items from spawning here
        destroyed_zone = pygame.Rect(x, y, w, h)
        self.destroyed_building_zones.append(destroyed_zone)

    def start_multiplayer_game(self, client, is_host):
        """Start multiplayer match with level 20 weapons"""
        # Save original weapons
        self.saved_weapon_upgrades = {k: v.copy() for k, v in self.weapon_upgrades.items()}
        
        # Set all weapons to level 20
        for weapon in self.weapon_upgrades:
            self.weapon_upgrades[weapon] = {'fire_rate': 20, 'damage': 20, 'spawn_rate': 20}
        
        # Start multiplayer game
        self.run_multiplayer_match(client, is_host)
        
        # Restore original weapons
        self.weapon_upgrades = self.saved_weapon_upgrades
        client.close()
    
    def setup_multiplayer_round(self, is_host):
        """Initialize multiplayer round with fair spawning"""
        from sprites import NetworkPlayer
        
        # Initialize game world
        self.all_sprites = CameraGroup()
        self.walls = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.upgrade_items = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()  # Empty - no AI
        
        self.destroyed_building_zones = []
        self.obstacle_respawn_queue = []
        self.tutorial_mode = False
        
        # Create players
        # Host: Bottom-Right, Client: Top-Left
        p1_x = MAP_WIDTH - 100 if is_host else 100
        p1_y = MAP_HEIGHT - 100 if is_host else 100
        self.player = Player(self, p1_x, p1_y)
        
        p2_x = 100 if is_host else MAP_WIDTH - 100
        p2_y = 100 if is_host else MAP_HEIGHT - 100
        self.network_player = NetworkPlayer(self, p2_x, p2_y)
        
        # Create obstacles (Fair Spawning)
        count = 0
        attempts = 0
        while count < 20 and attempts < 1000:
            attempts += 1
            x = random.randint(0, MAP_WIDTH - 100)
            y = random.randint(0, MAP_HEIGHT - 100)
            w = random.randint(50, 200)
            h = random.randint(50, 200)
            rect = pygame.Rect(x, y, w, h)
            
            # Check distance to players (Safe Zone 300px)
            # Use center of obstacle for distance check
            obs_center = vec(x + w/2, y + h/2)
            if (obs_center - self.player.pos).length() < 300 or \
               (obs_center - self.network_player.pos).length() < 300:
                continue
            
            # Check overlap with existing walls
            if any(wall.rect.colliderect(rect) for wall in self.walls):
                continue
                
            Obstacle(self, x, y, w, h)
            count += 1
        
        # Spawn weapons
        self.spawn_weapons()
        
        self.score = 0
        self.playing = True

    def run_multiplayer_match(self, client, is_host):
        """Run multiplayer match with network sync"""
        from sprites import NetworkPlayer
        
        while client.connected:
            # 1. Setup Round
            self.setup_multiplayer_round(is_host)
            
            last_sync = pygame.time.get_ticks()
            winner = None
            
            # 2. Game Loop
            while self.playing and client.connected:
                self.dt = self.clock.tick(FPS) / 1000
                
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.playing = False
                        client.close()
                        return
                
                # Update local player
                self.player.get_keys()
                self.player.pos += self.player.vel * self.dt
                self.player.rect.x = self.player.pos.x
                self.player.collide_with_walls('x')
                self.player.rect.y = self.player.pos.y
                self.player.collide_with_walls('y')
                
                # Boundary checks
                self.player.pos.x = max(0, min(MAP_WIDTH - PLAYER_SIZE, self.player.pos.x))
                self.player.pos.y = max(0, min(MAP_HEIGHT - PLAYER_SIZE, self.player.pos.y))
                self.player.rect.x = self.player.pos.x
                self.player.rect.y = self.player.pos.y
                
                # Send state to network (10 times per second)
                now = pygame.time.get_ticks()
                if now - last_sync > 100:
                    client.send({'type': 'state', 'x': self.player.pos.x, 'y': self.player.pos.y, 
                               'weapon': self.player.weapon, 'hits': self.player.hit_count})
                    last_sync = now
                
                # Receive network updates
                for msg in client.get_messages():
                    if msg.get('type') == 'state':
                        self.network_player.update_from_network(msg)
                    elif msg.get('type') == 'shoot':
                        # Remote player shot
                        data = msg['data']
                        from sprites import Projectile, Grenade
                        
                        # Recreate spread/count based on weapon stats
                        weapon_stats = WEAPONS[data['weapon']]
                        dir = vec(data['dx'], data['dy'])
                        
                        for _ in range(weapon_stats['count']):
                            spread = random.uniform(-weapon_stats['spread'], weapon_stats['spread'])
                            vel = dir.rotate(spread)
                            
                            if data['weapon'] == 'grenade':
                                Grenade(self, data['x'], data['y'], vel.x, vel.y, 'enemy',
                                       data['damage'], data['speed'], data['lifetime'], (255, 50, 50), False)
                            else:
                                Projectile(self, data['x'], data['y'], vel.x, vel.y, 'enemy',
                                         data['damage'], data['speed'], data['lifetime'], (255, 50, 50), False)
                    
                    elif msg.get('type') == 'shoot_building':
                        # Remote player shot at building
                        data = msg['data']
                        from sprites import BuildingProjectile
                        
                        weapon_stats = WEAPONS[data['weapon']]
                        dir = vec(data['dx'], data['dy'])
                        
                        for _ in range(weapon_stats['count']):
                            spread = random.uniform(-weapon_stats['spread'], weapon_stats['spread'])
                            vel = dir.rotate(spread)
                            BuildingProjectile(self, data['x'], data['y'], vel.x, vel.y,
                                             data['damage'], data['speed'], data['lifetime'], (255, 165, 0))

                    elif msg.get('type') == 'destroy_wall':
                        # Destroy specific wall
                        x, y = msg['x'], msg['y']
                        # Find obstacle at original coordinates
                        for wall in self.walls:
                            if hasattr(wall, 'original_x') and wall.original_x == x and wall.original_y == y:
                                if hasattr(wall, 'game'):
                                    wall.game.schedule_obstacle_respawn(wall.original_x, wall.original_y, 
                                                                      wall.original_w, wall.original_h)
                                wall.kill()
                                break
                    
                    elif msg.get('type') == 'left':
                         # Opponent left
                         self.show_message_box("Info", "Gegner hat das Spiel verlassen.")
                         self.playing = False
                         client.close()
                         return

                # Update sprites
                self.all_sprites.update()
                
                # Weapon pickups for local player
                hits = pygame.sprite.spritecollide(self.player, self.items, True)
                for hit in hits:
                    if self.player.weapon != 'pistol':
                        offset_x = random.randint(40, 80) * random.choice([-1, 1])
                        offset_y = random.randint(40, 80) * random.choice([-1, 1])
                        drop_x = max(0, min(MAP_WIDTH - WEAPON_SIZE, self.player.pos.x + offset_x))
                        drop_y = max(0, min(MAP_HEIGHT - WEAPON_SIZE, self.player.pos.y + offset_y))
                        WeaponItem(self, drop_x, drop_y, self.player.weapon)
                    self.player.weapon = hit.type
                    client.send({'type': 'weapon', 'weapon': hit.type})
                
                # Check game over
                if self.player.hit_count >= 10:
                    winner = "Client" if is_host else "Host"
                    self.playing = False
                elif self.network_player.hit_count >= 10:
                    winner = "Host" if is_host else "Client"
                    self.playing = False
                
                # Draw
                self.screen.fill(DARK_GREY)
                self.all_sprites.custom_draw(self.player)
                
                # HUD
                self.draw_text(f"Deine Treffer: {self.player.hit_count}/10", 10, 10)
                self.draw_text(f"Gegner Treffer: {self.network_player.hit_count}/10", 10, 40)
                self.draw_text(f"Waffe: {self.player.weapon.upper()}", 10, SCREEN_HEIGHT - 30)
                
                pygame.display.flip()
            
            # End of Round
            if not client.connected:
                break
                
            # If we exited due to QUIT event, return
            if not self.playing and winner is None:
                 # Check if it was because of opponent leaving (handled in loop) or manual quit
                 # If manual quit, we would have returned already
                 pass
            
            # Show Game Over Screen
            action = self.menu_manager.show_multiplayer_game_over(winner, client, is_host)
            if action == 'menu':
                break
            # if 'rematch', loop continues
            
        client.close()


    def save_total_score(self):
        """Save total score and settings via DataManager"""
        self.data_manager.set('total_score', self.total_score)
        self.data_manager.set('weapon_upgrades', self.weapon_upgrades)
        self.data_manager.set('total_upgrades_purchased', self.total_upgrades_purchased)
        self.data_manager.set('owned_colors', self.owned_colors)
        self.data_manager.set('selected_color', self.selected_color)
        self.data_manager.set('owned_bullet_colors', self.owned_bullet_colors)
        self.data_manager.set('selected_bullet_color', self.selected_bullet_color)
        self.data_manager.set('owned_kill_animations', self.owned_kill_animations)
        self.data_manager.set('selected_kill_animation', self.selected_kill_animation)
        self.data_manager.set('minimap_owned', self.minimap_owned)
        self.data_manager.set('minimap_active', self.minimap_active)
        self.data_manager.set('ai_aim_difficulty', self.ai_aim_difficulty)
        self.data_manager.set('ai_dodge_difficulty', self.ai_dodge_difficulty)
        self.data_manager.set('tutorial_completed', self.tutorial_completed)
        self.data_manager.set('game_mode', self.game_mode)
        self.data_manager.set('sounds_owned', self.sounds_owned)
        self.data_manager.set('sounds_active', self.sounds_active)
        self.data_manager.set('owned_designs', self.owned_designs)
        self.data_manager.set('selected_design', self.selected_design)
        
        self.data_manager.save()
    
    def show_tutorial(self):
        """Interactive in-game tutorial"""
        self.new(tutorial_mode=True)

if __name__ == "__main__":
    g = Game()
    # Show tutorial for new players
    if not g.tutorial_completed:
        g.show_tutorial()
    g.menu_manager.show_start_screen()
    while g.running:
        g.new()
        g.menu_manager.show_go_screen()
        # Return to start screen after game over
        if g.running:  # Only show start screen if not quitting
            g.menu_manager.show_start_screen()
    pygame.quit()
    sys.exit()

