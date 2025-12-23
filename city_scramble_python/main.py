import pygame
import sys
import random
import json
import os
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
        self.small_font = pygame.font.SysFont("Arial", 18)  # For shop subtexts
        self.medium_font = pygame.font.SysFont("Arial", 26)  # Smaller for compact buttons
        self.large_font = pygame.font.SysFont("Arial", 48)
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
        
        # Persistent score system
        self.score_file = "city_scramble_score.json"
        self.total_score = self.load_total_score()
        
        # Weapon upgrade system (only for player)
        self.weapon_upgrades = {
            weapon: {'fire_rate': 0, 'damage': 0, 'spawn_rate': 0}
            for weapon in WEAPONS.keys()
        }
        self.base_upgrade_cost = 500  # Base cost per upgrade
        self.total_upgrades_purchased = 0  # Track total purchases for price scaling
        
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
        self.owned_colors = ['white']  # Start with white
        self.selected_color = 'white'  # Currently selected color
        
        # Bullet color system (same colors and prices as character)
        self.bullet_colors = self.character_colors.copy()  # Same color definitions
        self.owned_bullet_colors = ['white']  # Start with white
        self.selected_bullet_color = 'white'  # Currently selected bullet color
        
        # Kill animation system
        self.kill_animations = {
            'none': {'name': 'Keine', 'duration': 0, 'cost': 0},  # Default
            'bloodsplat': {'name': 'Blutfleck', 'duration': 1000, 'cost': 50000},  # 1 sec
            'flowers': {'name': 'Blumen', 'duration': 2000, 'cost': 175000},  # 2 sec
            'gravestone': {'name': 'Grabstein', 'duration': 2500, 'cost': 500000}  # 2.5 sec
        }
        self.owned_kill_animations = ['none']  # Start with no animation
        self.selected_kill_animation = 'none'  # Currently selected animation
        
        # Load saved upgrades if they exist
        if hasattr(self, 'saved_upgrades'):
            for weapon, upgrades in self.saved_upgrades.items():
                if weapon in self.weapon_upgrades:
                    self.weapon_upgrades[weapon] = upgrades
        
        # Load saved purchase count if it exists
        if hasattr(self, 'saved_purchase_count'):
            self.total_upgrades_purchased = self.saved_purchase_count
        
        # Load saved colors if they exist
        if hasattr(self, 'saved_owned_colors'):
            self.owned_colors = self.saved_owned_colors
        if hasattr(self, 'saved_selected_color'):
            self.selected_color = self.saved_selected_color
        
        # Load saved bullet colors if they exist
        if hasattr(self, 'saved_owned_bullet_colors'):
            self.owned_bullet_colors = self.saved_owned_bullet_colors
        if hasattr(self, 'saved_selected_bullet_color'):
            self.selected_bullet_color = self.saved_selected_bullet_color
        
        # Load saved kill animations if they exist
        if hasattr(self, 'saved_owned_kill_animations'):
            self.owned_kill_animations = self.saved_owned_kill_animations
        if hasattr(self, 'saved_selected_kill_animation'):
            self.selected_kill_animation = self.saved_selected_kill_animation
            
        # Mini-Map ownership and active state
        self.minimap_owned = False
        self.minimap_active = False
        if hasattr(self, 'saved_minimap_owned'):
            self.minimap_owned = self.saved_minimap_owned
        if hasattr(self, 'saved_minimap_active'):
            self.minimap_active = self.saved_minimap_active
        
        # AI Aim Difficulty setting
        self.ai_aim_difficulty = 'normal'  # Options: 'easy', 'normal', 'hard'
        if hasattr(self, 'saved_ai_aim_difficulty'):
            self.ai_aim_difficulty = self.saved_ai_aim_difficulty
        
        # AI Dodge Difficulty setting (separate from aiming)
        self.ai_dodge_difficulty = 'normal'  # Options: 'easy', 'normal', 'hard'
        if hasattr(self, 'saved_ai_dodge_difficulty'):
            self.ai_dodge_difficulty = self.saved_ai_dodge_difficulty

        # Game Mode setting
        self.game_mode = 'classic'  # Options: 'classic', 'survival', 'team5v5'
        if hasattr(self, 'saved_game_mode'):
            self.game_mode = self.saved_game_mode

        # Tutorial completion tracking
        self.tutorial_completed = False
        if hasattr(self, 'saved_tutorial_completed'):
            self.tutorial_completed = self.saved_tutorial_completed
        
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
            print(f"[OK] Menue-Musik '{self.menu_music_file}' erfolgreich geladen")
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
        
        self.all_sprites = CameraGroup()  # Use CameraGroup
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
        
        if self.match_music_loaded:
            try:
                # Starte Match-Musik mit Fade-In über 2 Sekunden
                pygame.mixer.music.play(-1, fade_ms=2000)  # fade_ms = 2000ms Fade-In
                print("[OK] Match-Musik wird eingeblendet (2s) und laeuft in Dauerschleife")
            except Exception as e:
                print(f"[FEHLER] Fehler beim Starten der Match-Musik: {e}")
        else:
            print("[INFO] Match-Musik nicht geladen, spiele ohne Musik")
        
        # Starte parallel den zweiten Sound-Layer (75% leiser)
        if self.match_sound2_loaded and self.match_sound2:
            try:
                self.match_sound2.play(-1, fade_ms=2000)  # -1 = Dauerschleife, 2s Fade-In
                print("[OK] Match-Sound-Layer-2 parallel gestartet (75% leiser, 2s Fade-In)")
            except Exception as e:
                print(f"[FEHLER] Fehler beim Starten von Sound-Layer-2: {e}")

        self.run()
        
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
                self.show_message_box("Tutorial Abgeschlossen", "Du bist bereit für das Spiel!")

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

    def show_start_screen(self):
        # Starte Menü-Musik in Dauerschleife
        if self.menu_music_loaded and self.menu_music:
            self.menu_music.play(-1)  # -1 = Endlosschleife
            print("[OK] Menue-Musik gestartet (laeuft in Dauerschleife)")
        
        # Define buttons - 6 main buttons + start (compact layout)
        button_width = 250
        button_height = 45  # Back to 45
        button_spacing = 15  # Back to 15

        # Center buttons horizontally, start higher up
        buttons_x = SCREEN_WIDTH // 2 - button_width // 2
        buttons_start_y = SCREEN_HEIGHT // 2 - 70  # Adjusted for 6 buttons

        # Six main buttons
        game_mode_button = pygame.Rect(buttons_x, buttons_start_y, button_width, button_height)
        enemy_button = pygame.Rect(buttons_x, buttons_start_y + (button_height + button_spacing), button_width, button_height)
        ai_aim_button = pygame.Rect(buttons_x, buttons_start_y + (button_height + button_spacing) * 2, button_width, button_height)
        ai_dodge_button = pygame.Rect(buttons_x, buttons_start_y + (button_height + button_spacing) * 3, button_width, button_height)
        shop_button = pygame.Rect(buttons_x, buttons_start_y + (button_height + button_spacing) * 4, button_width, button_height)
        multiplayer_button = pygame.Rect(buttons_x, buttons_start_y + (button_height + button_spacing) * 5, button_width, button_height)

        # Tutorial button (Top Left Corner)
        tutorial_button = pygame.Rect(20, 20, 200, 40)

        # Start button (centered below, compact)
        start_button = pygame.Rect(SCREEN_WIDTH // 2 - 140, buttons_start_y + (button_height + button_spacing) * 6 + 15, 280, 55)
        
        while True:
            self.screen.fill(DARK_GREY)
            # Title
            title_text = self.large_font.render(TITLE, True, WHITE)
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 200))
            
            # Total Score Display
            total_score_text = self.large_font.render(f"Gesamtpunkte: {self.total_score:,}", True, (255, 215, 0))
            total_score_rect = total_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120))
            # Background box for total score
            box_rect = pygame.Rect(total_score_rect.x - 20, total_score_rect.y - 10, 
                                   total_score_rect.width + 40, total_score_rect.height + 20)
            pygame.draw.rect(self.screen, (50, 50, 50), box_rect)
            pygame.draw.rect(self.screen, (255, 215, 0), box_rect, 3)
            self.screen.blit(total_score_text, total_score_rect)
            
            # Game Mode button
            mode_names = {'classic': 'Klassisch', 'survival': 'Überlebens-Modus', 'team5v5': '5vs5 Team'}
            mode_colors = {'classic': (100, 200, 100), 'survival': (255, 100, 50), 'team5v5': (100, 100, 255)}
            current_mode_name = mode_names[self.game_mode]
            current_mode_color = mode_colors[self.game_mode]

            pygame.draw.rect(self.screen, current_mode_color, game_mode_button)
            pygame.draw.rect(self.screen, WHITE, game_mode_button, 3)
            mode_text = self.medium_font.render(f"Modus: {current_mode_name}", True, WHITE)
            mode_text_rect = mode_text.get_rect(center=game_mode_button.center)
            self.screen.blit(mode_text, mode_text_rect)

            # Enemy count button
            pygame.draw.rect(self.screen, LIGHT_GREY, enemy_button)
            pygame.draw.rect(self.screen, WHITE, enemy_button, 3)
            enemy_text = self.medium_font.render("Gegner ändern", True, WHITE)
            enemy_text_rect = enemy_text.get_rect(center=enemy_button.center)
            self.screen.blit(enemy_text, enemy_text_rect)
            
            # AI Aiming difficulty button
            difficulty_names = {'easy': 'Einfach', 'normal': 'Normal', 'hard': 'Schwer', 'hardcore': 'HARDCORE'}
            difficulty_colors = {'easy': (50, 200, 50), 'normal': (255, 200, 50), 'hard': (255, 50, 50), 'hardcore': (200, 0, 200)}
            current_difficulty_name = difficulty_names[self.ai_aim_difficulty]
            current_difficulty_color = difficulty_colors[self.ai_aim_difficulty]
            
            pygame.draw.rect(self.screen, current_difficulty_color, ai_aim_button)
            pygame.draw.rect(self.screen, WHITE, ai_aim_button, 3)
            ai_aim_text = self.medium_font.render(f"KI-Aiming: {current_difficulty_name}", True, WHITE)
            ai_aim_text_rect = ai_aim_text.get_rect(center=ai_aim_button.center)
            self.screen.blit(ai_aim_text, ai_aim_text_rect)
            
            # AI Dodge difficulty button
            dodge_difficulty_name = difficulty_names[self.ai_dodge_difficulty]
            dodge_difficulty_color = difficulty_colors[self.ai_dodge_difficulty]
            
            pygame.draw.rect(self.screen, dodge_difficulty_color, ai_dodge_button)
            pygame.draw.rect(self.screen, WHITE, ai_dodge_button, 3)
            ai_dodge_text = self.medium_font.render(f"KI-Ausweichen: {dodge_difficulty_name}", True, WHITE)
            ai_dodge_text_rect = ai_dodge_text.get_rect(center=ai_dodge_button.center)
            self.screen.blit(ai_dodge_text, ai_dodge_text_rect)
            
            # Tutorial button
            pygame.draw.rect(self.screen, (255, 150, 50), tutorial_button)  # Orange
            pygame.draw.rect(self.screen, WHITE, tutorial_button, 3)
            tutorial_text = self.medium_font.render("TUTORIAL", True, WHITE)
            tutorial_text_rect = tutorial_text.get_rect(center=tutorial_button.center)
            self.screen.blit(tutorial_text, tutorial_text_rect)
            
            # Unified Shop button
            pygame.draw.rect(self.screen, (100, 200, 255), shop_button)
            pygame.draw.rect(self.screen, WHITE, shop_button, 3)
            shop_text = self.medium_font.render("SHOP", True, WHITE)
            shop_text_rect = shop_text.get_rect(center=shop_button.center)
            self.screen.blit(shop_text, shop_text_rect)
            
            # Multiplayer button
            pygame.draw.rect(self.screen, (255, 100, 255), multiplayer_button)
            pygame.draw.rect(self.screen, WHITE, multiplayer_button, 3)
            multi_text = self.medium_font.render("1vs1 ONLINE", True, WHITE)
            multi_text_rect = multi_text.get_rect(center=multiplayer_button.center)
            self.screen.blit(multi_text, multi_text_rect)
            
            # Start game button
            pygame.draw.rect(self.screen, (50, 200, 50), start_button)
            pygame.draw.rect(self.screen, WHITE, start_button, 4)
            start_text = self.medium_font.render("SPIEL STARTEN", True, WHITE)
            start_text_rect = start_text.get_rect(center=start_button.center)
            self.screen.blit(start_text, start_text_rect)
            
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if game_mode_button.collidepoint(event.pos):
                        # Cycle through: classic -> survival -> team5v5 -> classic
                        if self.game_mode == 'classic':
                            self.game_mode = 'survival'
                        elif self.game_mode == 'survival':
                            self.game_mode = 'team5v5'
                        else:
                            self.game_mode = 'classic'
                        self.save_total_score()  # Save the setting
                    elif enemy_button.collidepoint(event.pos):
                        self.max_enemies = self.max_enemies + 1 if self.max_enemies < 20 else 1
                    elif ai_aim_button.collidepoint(event.pos):
                        # Cycle through difficulties: easy -> normal -> hard -> hardcore -> easy
                        if self.ai_aim_difficulty == 'easy':
                            self.ai_aim_difficulty = 'normal'
                        elif self.ai_aim_difficulty == 'normal':
                            self.ai_aim_difficulty = 'hard'
                        elif self.ai_aim_difficulty == 'hard':
                            self.ai_aim_difficulty = 'hardcore'
                        else:
                            self.ai_aim_difficulty = 'easy'
                        self.save_total_score()  # Save the setting
                    elif ai_dodge_button.collidepoint(event.pos):
                        # Cycle through difficulties: easy -> normal -> hard -> hardcore -> easy
                        if self.ai_dodge_difficulty == 'easy':
                            self.ai_dodge_difficulty = 'normal'
                        elif self.ai_dodge_difficulty == 'normal':
                            self.ai_dodge_difficulty = 'hard'
                        elif self.ai_dodge_difficulty == 'hard':
                            self.ai_dodge_difficulty = 'hardcore'
                        else:
                            self.ai_dodge_difficulty = 'easy'
                        self.save_total_score()  # Save the setting
                    elif tutorial_button.collidepoint(event.pos):
                        # Show tutorial
                        self.show_tutorial()
                    elif shop_button.collidepoint(event.pos):
                        self.show_unified_shop()
                    elif multiplayer_button.collidepoint(event.pos):
                        self.show_multiplayer_menu()
                    elif start_button.collidepoint(event.pos):
                        return

    def show_multiplayer_menu(self):
        """Multiplayer host/join selection menu"""
        from network import ensure_server, GameClient
        ensure_server()
        
        button_width, button_height, button_spacing = 300, 70, 30
        buttons_x = SCREEN_WIDTH // 2 - button_width // 2
        buttons_y = SCREEN_HEIGHT // 2 - 50
        
        host_button = pygame.Rect(buttons_x, buttons_y, button_width, button_height)
        join_button = pygame.Rect(buttons_x, buttons_y + button_height + button_spacing, button_width, button_height)
        back_button = pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 100, 240, 60)
        
        while True:
            self.screen.fill(DARK_GREY)
            title_text = self.large_font.render("MULTIPLAYER", True, (255, 100, 255))
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - 130, 100))
            
            pygame.draw.rect(self.screen, (100, 255, 100), host_button)
            pygame.draw.rect(self.screen, WHITE, host_button, 3)
            host_text = self.large_font.render("SPIEL HOSTEN", True, WHITE)
            self.screen.blit(host_text, (host_button.centerx - 110, host_button.centery - 20))
            
            pygame.draw.rect(self.screen, (255, 200, 100), join_button)
            pygame.draw.rect(self.screen, WHITE, join_button, 3)
            join_text = self.large_font.render("SPIEL BEITRETEN", True, WHITE)
            self.screen.blit(join_text, (join_button.centerx - 140, join_button.centery - 20))
            
            pygame.draw.rect(self.screen, LIGHT_GREY, back_button)
            pygame.draw.rect(self.screen, WHITE, back_button, 3)
            back_text = self.large_font.render("ZURÜCK", True, WHITE)
            back_rect = back_text.get_rect(center=back_button.center)
            self.screen.blit(back_text, back_rect)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if back_button.collidepoint(event.pos):
                        return
                    elif host_button.collidepoint(event.pos):
                        self.multiplayer_host()
                    elif join_button.collidepoint(event.pos):
                        self.multiplayer_join()
    
    def multiplayer_host(self):
        """Host multiplayer game"""
        from network import GameClient, get_local_ip
        local_ip = get_local_ip()
        client = GameClient()
        if not client.connect():
            self.show_message_box("Fehler", "Server nicht erreichbar!")
            return
        
        room_code = client.create_room()
        if not room_code:
            self.show_message_box("Fehler", "Raum konnte nicht erstellt werden!")
            client.close()
            return
        
        waiting, other_joined = True, False
        while waiting:
            self.screen.fill(DARK_GREY)
            title = self.large_font.render("WARTE AUF GEGNER...", True, WHITE)
            self.screen.blit(title, (SCREEN_WIDTH // 2 - 200, 150))
            
            code_font = pygame.font.SysFont("Arial", 72, bold=True)
            code_text = code_font.render(room_code, True, (255, 255, 100))
            code_rect = code_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            pygame.draw.rect(self.screen, (50, 50, 50), (code_rect.x - 20, code_rect.y - 20, code_rect.width + 40, code_rect.height + 40))
            pygame.draw.rect(self.screen, (255, 255, 100), (code_rect.x - 20, code_rect.y - 20, code_rect.width + 40, code_rect.height + 40), 3)
            self.screen.blit(code_text, code_rect)
            
            # Show Monitor/IP Info
            ip_text = self.font.render(f"Host-IP: {local_ip}", True, (100, 255, 100))
            self.screen.blit(ip_text, (SCREEN_WIDTH // 2 - ip_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))
            
            instr = self.font.render("Gib Code & IP an deinen Gegner weiter!", True, WHITE)
            self.screen.blit(instr, (SCREEN_WIDTH // 2 - instr.get_width() // 2, SCREEN_HEIGHT // 2 + 100))
            
            cancel_btn = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50)
            pygame.draw.rect(self.screen, (200, 50, 50), cancel_btn)
            pygame.draw.rect(self.screen, WHITE, cancel_btn, 2)
            cancel_text = self.font.render("Abbrechen", True, WHITE)
            self.screen.blit(cancel_text, (cancel_btn.centerx - 40, cancel_btn.centery - 10))
            
            pygame.display.flip()
            
            for msg in client.get_messages():
                if msg.get('type') == 'ready':
                    other_joined = True
                    waiting = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    client.close()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP and cancel_btn.collidepoint(event.pos):
                    client.close()
                    return
        
        if other_joined:
            self.start_multiplayer_game(client, is_host=True)
    
    def multiplayer_join(self):
        """Join multiplayer game via room code"""
        from network import GameClient
        
        # 1. Ask for Host IP
        host_ip = self.get_text_input("HOST-IP EINGEBEN (Leer=Lokal)", "127.0.0.1", max_length=15)
        if host_ip is None: return
        if host_ip == "": host_ip = "127.0.0.1"
        
        # 2. Ask for Room Code
        room_code = self.get_text_input("RAUM-CODE EINGEBEN")
        if not room_code:
            return
        
        client = GameClient()
        if not client.connect(host=host_ip):
            self.show_message_box("Fehler", "Server nicht erreichbar!")
            return
        
        if client.join_room(room_code.upper()):
            self.start_multiplayer_game(client, is_host=False)
        else:
            self.show_message_box("Fehler", f"Raum '{room_code}' nicht gefunden!")
            client.close()
    
    def get_text_input(self, prompt, default_text="", max_length=6):
        """Simple text input dialog"""
        text = default_text
        while True:
            # Drawing code skipped for brevity (unchanged logic, just parameters)
            self.screen.fill(DARK_GREY)
            prompt_surf = self.large_font.render(prompt, True, WHITE)
            self.screen.blit(prompt_surf, (SCREEN_WIDTH // 2 - prompt_surf.get_width() // 2, 200))
            
            input_box = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 30, 300, 60)
            pygame.draw.rect(self.screen, (50, 50, 50), input_box)
            pygame.draw.rect(self.screen, WHITE, input_box, 3)
            # Use smaller font if text is long
            font_size = 48 if len(text) < 10 else 32
            text_surf = pygame.font.SysFont("Arial", font_size).render(text, True, (255, 255, 100))
            self.screen.blit(text_surf, (input_box.centerx - text_surf.get_width() // 2, input_box.centery - text_surf.get_height() // 2))
            
            ok_btn = pygame.Rect(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT - 150, 100, 50)
            cancel_btn = pygame.Rect(SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT - 150, 100, 50)
            pygame.draw.rect(self.screen, (100, 200, 100), ok_btn)
            pygame.draw.rect(self.screen, WHITE, ok_btn, 2)
            self.screen.blit(self.font.render("OK", True, WHITE), (ok_btn.centerx - 15, ok_btn.centery - 10))
            pygame.draw.rect(self.screen, (200, 100, 100), cancel_btn)
            pygame.draw.rect(self.screen, WHITE, cancel_btn, 2)
            self.screen.blit(self.font.render("Abbruch", True, WHITE), (cancel_btn.centerx - 30, cancel_btn.centery - 10))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return text if text else None
                    elif event.key == pygame.K_ESCAPE:
                        return None
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    elif len(text) < max_length and (event.unicode.isalnum() or event.unicode in ['.', ':']):
                        text += event.unicode.upper()
                if event.type == pygame.MOUSEBUTTONUP:
                    if ok_btn.collidepoint(event.pos):
                        return text if text else None
                    elif cancel_btn.collidepoint(event.pos):
                        return None
    
    def show_message_box(self, title, message):
        """Simple message box"""
        while True:
            self.screen.fill(DARK_GREY)
            title_surf = self.large_font.render(title, True, (255, 100, 100))
            self.screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 200))
            msg_surf = self.font.render(message, True, WHITE)
            self.screen.blit(msg_surf, (SCREEN_WIDTH // 2 - msg_surf.get_width() // 2, SCREEN_HEIGHT // 2))
            
            ok_btn = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 150, 150, 50)
            pygame.draw.rect(self.screen, (100, 200, 100), ok_btn)
            pygame.draw.rect(self.screen, WHITE, ok_btn, 2)
            ok_text = self.font.render("OK", True, WHITE)
            self.screen.blit(ok_text, (ok_btn.centerx - 15, ok_btn.centery - 10))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP and ok_btn.collidepoint(event.pos):
                    return
                if event.type == pygame.KEYDOWN and event.key in [pygame.K_RETURN, pygame.K_ESCAPE]:
                    return
    
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

    def show_multiplayer_game_over(self, winner, client, is_host):
        """Show multiplayer game over screen with rematch option"""
        rematch_btn = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, 300, 60)
        menu_btn = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 130, 300, 60)
        
        # Send waiting flag to clean up previous messages?
        # Maybe just wait for input.
        
        waiting = True
        while waiting and client.connected:
            self.screen.fill(0) # Black screen or transparent overlay?
            # Draw game behind it (optional, but need to pass 'draw' first)
            # Just fill dark grey
            self.screen.fill(DARK_GREY)
            
            # Result Text
            if (winner == "Host" and is_host) or (winner == "Client" and not is_host):
                title = "SIEG!"
                color = (100, 255, 100)
            else:
                title = "NIEDERLAGE"
                color = (255, 100, 100)
            
            title_surf = self.large_font.render(title, True, color)
            self.screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 150))
            
            stats_text = f"Mein Treffer: {self.player.hit_count} | Gegner Treffer: {self.network_player.hit_count}"
            s_surf = self.font.render(stats_text, True, WHITE)
            self.screen.blit(s_surf, (SCREEN_WIDTH // 2 - s_surf.get_width() // 2, 250))
            
            # Buttons
            pygame.draw.rect(self.screen, (50, 150, 255), rematch_btn)
            pygame.draw.rect(self.screen, WHITE, rematch_btn, 3)
            r_text = self.medium_font.render("REVANCHE", True, WHITE)
            self.screen.blit(r_text, r_text.get_rect(center=rematch_btn.center))
            
            pygame.draw.rect(self.screen, (150, 50, 50), menu_btn)
            pygame.draw.rect(self.screen, WHITE, menu_btn, 3)
            m_text = self.medium_font.render("MENÜ", True, WHITE)
            self.screen.blit(m_text, m_text.get_rect(center=menu_btn.center))
            
            pygame.display.flip()
            
            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'menu'
                if event.type == pygame.MOUSEBUTTONUP:
                    if rematch_btn.collidepoint(event.pos):
                        client.send({'type': 'rematch'})
                        return 'rematch'
                    if menu_btn.collidepoint(event.pos):
                        return 'menu'
            
            # Network Messages
            for msg in client.get_messages():
                if msg.get('type') == 'rematch':
                    # Opponent wants rematch
                    # We can auto-accept or show "Opponent wants rematch"
                    # For simplicity: If ANYONE clicks rematch, we accept.
                    return 'rematch'
                if msg.get('type') == 'left':
                    return 'menu'

        return 'menu'

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
            action = self.show_multiplayer_game_over(winner, client, is_host)
            if action == 'menu':
                break
            # if 'rematch', loop continues
            
        client.close()


    def show_unified_shop(self):
        """Unified shop menu with category selection"""
        # Define 2 large category buttons
        button_width = 350
        button_height = 80
        button_spacing = 40
        
        # Center buttons
        start_x = SCREEN_WIDTH // 2 - button_width // 2
        start_y = 220
        
        # Two category buttons
        shops_button = pygame.Rect(start_x, start_y, button_width, button_height)
        wardrobes_button = pygame.Rect(start_x, start_y + button_height + button_spacing, button_width, button_height)
        
        # Back button
        back_button = pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 100, 240, 60)
        
        while True:
            self.screen.fill(DARK_GREY)
            
            # Title
            title_text = self.large_font.render("SHOP-MENÜ", True, (100, 200, 255))
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - 120, 60))
            
            # Current score
            score_text = self.font.render(f"Verfügbare Punkte: {self.total_score:,}", True, (255, 215, 0))
            self.screen.blit(score_text, (SCREEN_WIDTH // 2 - 120, 130))
            
            # Shops button
            pygame.draw.rect(self.screen, (100, 200, 100), shops_button)
            pygame.draw.rect(self.screen, WHITE, shops_button, 4)
            shops_text = self.medium_font.render("SHOPS", True, WHITE)
            shops_subtext = self.small_font.render("(Waffen, Charakter, Kugel, Kill-Anim, Spezial)", True, WHITE)
            shops_text_rect = shops_text.get_rect(center=(shops_button.centerx, shops_button.centery - 15))
            shops_subtext_rect = shops_subtext.get_rect(center=(shops_button.centerx, shops_button.centery + 15))
            self.screen.blit(shops_text, shops_text_rect)
            self.screen.blit(shops_subtext, shops_subtext_rect)
            
            # Wardrobes button
            pygame.draw.rect(self.screen, (200, 100, 200), wardrobes_button)
            pygame.draw.rect(self.screen, WHITE, wardrobes_button, 4)
            wardrobes_text = self.medium_font.render("KLEIDERSCHRÄNKE", True, WHITE)
            wardrobes_subtext = self.small_font.render("(Charakter, Kugel, Kill-Anim, Spezial)", True, WHITE)
            wardrobes_text_rect = wardrobes_text.get_rect(center=(wardrobes_button.centerx, wardrobes_button.centery - 15))
            wardrobes_subtext_rect = wardrobes_subtext.get_rect(center=(wardrobes_button.centerx, wardrobes_button.centery + 15))
            self.screen.blit(wardrobes_text, wardrobes_text_rect)
            self.screen.blit(wardrobes_subtext, wardrobes_subtext_rect)
            
            # Back button
            pygame.draw.rect(self.screen, LIGHT_GREY, back_button)
            pygame.draw.rect(self.screen, WHITE, back_button, 3)
            back_text = self.large_font.render("ZURÜCK", True, WHITE)
            back_text_rect = back_text.get_rect(center=back_button.center)
            self.screen.blit(back_text, back_text_rect)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if back_button.collidepoint(event.pos):
                        return
                    elif shops_button.collidepoint(event.pos):
                        self.show_shops_submenu()
                    elif wardrobes_button.collidepoint(event.pos):
                        self.show_wardrobes_submenu()
    
    def show_shops_submenu(self):
        """Submenu for all shops"""
        # Define button layout - 3 columns, 2 rows (5 shops)
        button_width = 250
        button_height = 60
        button_spacing_x = 25
        button_spacing_y = 25
        buttons_per_row = 3
        
        # Calculate starting position to center the grid
        total_width = buttons_per_row * button_width + (buttons_per_row - 1) * button_spacing_x
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = 200
        
        # Shop data
        shop_buttons = []
        shop_data = [
            {'name': 'Waffen-Shop', 'color': (100, 200, 100), 'method': self.show_shop},
            {'name': 'Charakter-Shop', 'color': (200, 100, 200), 'method': self.show_character_shop},
            {'name': 'Kugel-Shop', 'color': (255, 150, 50), 'method': self.show_bullet_shop},
            {'name': 'Kill-Animationen', 'color': (150, 50, 150), 'method': self.show_kill_animation_shop},
            {'name': 'Spezial-Shop', 'color': (100, 100, 255), 'method': self.show_special_shop},
        ]
        
        for i, shop_info in enumerate(shop_data):
            row = i // buttons_per_row
            col = i % buttons_per_row
            x = start_x + col * (button_width + button_spacing_x)
            y = start_y + row * (button_height + button_spacing_y)
            shop_buttons.append({
                'rect': pygame.Rect(x, y, button_width, button_height),
                'name': shop_info['name'],
                'color': shop_info['color'],
                'method': shop_info['method']
            })
        
        # Back button
        back_button = pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 100, 240, 60)
        
        while True:
            self.screen.fill(DARK_GREY)
            
            # Title
            title_text = self.large_font.render("SHOPS", True, (100, 200, 100))
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - 80, 60))
            
            # Current score
            score_text = self.font.render(f"Verfügbare Punkte: {self.total_score:,}", True, (255, 215, 0))
            self.screen.blit(score_text, (SCREEN_WIDTH // 2 - 120, 130))
            
            # Draw all shop buttons
            for button_data in shop_buttons:
                pygame.draw.rect(self.screen, button_data['color'], button_data['rect'])
                pygame.draw.rect(self.screen, WHITE, button_data['rect'], 3)
                
                # Center text
                text_surface = self.font.render(button_data['name'], True, WHITE)
                text_rect = text_surface.get_rect(center=button_data['rect'].center)
                self.screen.blit(text_surface, text_rect)
            
            # Back button
            pygame.draw.rect(self.screen, LIGHT_GREY, back_button)
            pygame.draw.rect(self.screen, WHITE, back_button, 3)
            back_text = self.large_font.render("ZURÜCK", True, WHITE)
            back_text_rect = back_text.get_rect(center=back_button.center)
            self.screen.blit(back_text, back_text_rect)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if back_button.collidepoint(event.pos):
                        return
                    # Check which shop button was clicked
                    for button_data in shop_buttons:
                        if button_data['rect'].collidepoint(event.pos):
                            button_data['method']()
    
    def show_wardrobes_submenu(self):
        """Submenu for all wardrobes"""
        # Define button layout - 2 columns, 2 rows (4 wardrobes)
        button_width = 280
        button_height = 65
        button_spacing_x = 30
        button_spacing_y = 30
        buttons_per_row = 2
        
        # Calculate starting position to center the grid
        total_width = buttons_per_row * button_width + (buttons_per_row - 1) * button_spacing_x
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = 200
        
        # Wardrobe data
        wardrobe_buttons = []
        wardrobe_data = [
            {'name': 'Charakter-Kleiderschrank', 'color': (100, 150, 200), 'method': self.show_wardrobe},
            {'name': 'Kugel-Farben', 'color': (200, 200, 50), 'method': self.show_bullet_wardrobe},
            {'name': 'Kill-Animation-Auswahl', 'color': (200, 100, 150), 'method': self.show_kill_animation_wardrobe},
            {'name': 'Spezial-Kleiderschrank', 'color': (150, 100, 200), 'method': self.show_special_wardrobe},
        ]
        
        for i, wardrobe_info in enumerate(wardrobe_data):
            row = i // buttons_per_row
            col = i % buttons_per_row
            x = start_x + col * (button_width + button_spacing_x)
            y = start_y + row * (button_height + button_spacing_y)
            wardrobe_buttons.append({
                'rect': pygame.Rect(x, y, button_width, button_height),
                'name': wardrobe_info['name'],
                'color': wardrobe_info['color'],
                'method': wardrobe_info['method']
            })
        
        # Back button
        back_button = pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 100, 240, 60)
        
        while True:
            self.screen.fill(DARK_GREY)
            
            # Title
            title_text = self.large_font.render("KLEIDERSCHRÄNKE", True, (200, 100, 200))
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - 180, 60))
            
            # Current selection display
            current_text = self.font.render("Aktuelle Auswahl:", True, WHITE)
            self.screen.blit(current_text, (SCREEN_WIDTH // 2 - 80, 130))
            
            # Draw all wardrobe buttons
            for button_data in wardrobe_buttons:
                pygame.draw.rect(self.screen, button_data['color'], button_data['rect'])
                pygame.draw.rect(self.screen, WHITE, button_data['rect'], 3)
                
                # Center text
                text_surface = self.font.render(button_data['name'], True, WHITE)
                text_rect = text_surface.get_rect(center=button_data['rect'].center)
                self.screen.blit(text_surface, text_rect)
            
            # Back button
            pygame.draw.rect(self.screen, LIGHT_GREY, back_button)
            pygame.draw.rect(self.screen, WHITE, back_button, 3)
            back_text = self.large_font.render("ZURÜCK", True, WHITE)
            back_text_rect = back_text.get_rect(center=back_button.center)
            self.screen.blit(back_text, back_text_rect)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if back_button.collidepoint(event.pos):
                        return
                    # Check which wardrobe button was clicked
                    for button_data in wardrobe_buttons:
                        if button_data['rect'].collidepoint(event.pos):
                            button_data['method']()

    def show_shop(self):

        """Shop screen for buying random weapon upgrades"""
        back_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 40)
        buy_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 160, 200, 40)
        
        # Select random weapon and upgrade type
        selected_weapon = random.choice(list(WEAPONS.keys()))
        upgrade_types = ['fire_rate', 'damage', 'spawn_rate']
        selected_upgrade = random.choice(upgrade_types)
        
        upgrade_names = {
            'fire_rate': 'Feuerrate',
            'damage': 'Schaden',
            'spawn_rate': 'Spawn-Rate'
        }
        
        upgrade_descriptions = {
            'fire_rate': '-0.1s Schussgeschwindigkeit',
            'damage': '+10% Schaden',
            'spawn_rate': '+10% Spawn-Chance'
        }
        
        message = ""
        message_color = WHITE
        
        while True:
            self.screen.fill(DARK_GREY)
            
            # Calculate current upgrade cost (1% increase per purchase, rounded up)
            import math
            current_cost = math.ceil(self.base_upgrade_cost * (1.01 ** self.total_upgrades_purchased))
            
            # Title
            title_text = self.large_font.render("WAFFEN-SHOP", True, (255, 215, 0))
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - 150, 50))
            
            # Current score
            self.draw_text(f"Verfügbare Punkte: {self.total_score:,}", SCREEN_WIDTH // 2 - 100, 120)
            self.draw_text(f"Upgrade-Kosten: {current_cost}", SCREEN_WIDTH // 2 - 80, 150)
            self.draw_text(f"Gekaufte Upgrades: {self.total_upgrades_purchased}", SCREEN_WIDTH // 2 - 90, 175)
            
            # Random upgrade offer
            self.draw_text("Zufälliges Upgrade-Angebot:", SCREEN_WIDTH // 2 - 100, 210)
            weapon_text = self.font.render(f"Waffe: {selected_weapon.upper()}", True, WEAPONS[selected_weapon]['color'])
            self.screen.blit(weapon_text, (SCREEN_WIDTH // 2 - 80, 250))
            self.draw_text(f"Upgrade: {upgrade_names[selected_upgrade]}", SCREEN_WIDTH // 2 - 80, 290)
            self.draw_text(upgrade_descriptions[selected_upgrade], SCREEN_WIDTH // 2 - 100, 330)
            
            # Current upgrade level
            current_level = self.weapon_upgrades[selected_weapon][selected_upgrade]
            self.draw_text(f"Aktuelle Stufe: {current_level}", SCREEN_WIDTH // 2 - 80, 370)
            
            # Buy button
            can_afford = self.total_score >= current_cost
            button_color = (100, 200, 100) if can_afford else (100, 100, 100)
            pygame.draw.rect(self.screen, button_color, buy_button)
            pygame.draw.rect(self.screen, WHITE, buy_button, 2)
            self.draw_text("Kaufen", buy_button.x + 60, buy_button.y + 10)
            
            # Back button
            pygame.draw.rect(self.screen, LIGHT_GREY, back_button)
            pygame.draw.rect(self.screen, WHITE, back_button, 2)
            self.draw_text("Zurück", back_button.x + 60, back_button.y + 10)
            
            # Message
            if message:
                self.draw_text(message, SCREEN_WIDTH // 2 - 150, 420, message_color)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if back_button.collidepoint(event.pos):
                        return
                    elif buy_button.collidepoint(event.pos) and can_afford:
                        # Purchase upgrade
                        self.total_score -= current_cost
                        self.weapon_upgrades[selected_weapon][selected_upgrade] += 1
                        self.total_upgrades_purchased += 1  # Increment purchase counter
                        self.save_total_score()
                        message = f"Upgrade gekauft! Neue Stufe: {self.weapon_upgrades[selected_weapon][selected_upgrade]}"
                        message_color = (100, 255, 100)
                        # Generate new random offer
                        selected_weapon = random.choice(list(WEAPONS.keys()))
                        selected_upgrade = random.choice(upgrade_types)
                    elif buy_button.collidepoint(event.pos):
                        message = "Nicht genug Punkte!"
                        message_color = (255, 100, 100)

    def show_character_shop(self):
        """Character shop screen for buying character colors"""
        back_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 40)
        
        # Create a grid of color buttons (2 columns)
        colors_per_row = 2
        button_width = 220
        button_height = 50
        button_spacing = 20
        start_x = SCREEN_WIDTH // 2 - (colors_per_row * button_width + (colors_per_row - 1) * button_spacing) // 2
        start_y = 180
        
        color_buttons = {}
        row = 0
        col = 0
        
        # Create buttons for colors not yet owned (excluding white which is default)
        available_colors = {k: v for k, v in self.character_colors.items() 
                           if k not in self.owned_colors and k != 'white'}
        
        for color_id, color_data in available_colors.items():
            x = start_x + col * (button_width + button_spacing)
            y = start_y + row * (button_height + button_spacing)
            color_buttons[color_id] = pygame.Rect(x, y, button_width, button_height)
            col += 1
            if col >= colors_per_row:
                col = 0
                row += 1
        
        message = ""
        message_color = WHITE
        
        while True:
            self.screen.fill(DARK_GREY)
            
            # Title
            title_text = self.large_font.render("CHARAKTER-SHOP", True, (200, 100, 200))
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - 180, 40))
            
            # Current score
            self.draw_text(f"Verfügbare Punkte: {self.total_score:,}", SCREEN_WIDTH // 2 - 100, 100)
            self.draw_text(f"Farbenpreis: 15.000", SCREEN_WIDTH // 2 - 80, 130)
            
            # Draw color buttons
            for color_id, button_rect in color_buttons.items():
                color_data = self.character_colors[color_id]
                can_afford = self.total_score >= color_data['cost']
                
                # Button background
                button_color = color_data['rgb'] if can_afford else (60, 60, 60)
                pygame.draw.rect(self.screen, button_color, button_rect)
                pygame.draw.rect(self.screen, WHITE, button_rect, 3)
                
                # Text
                text_color = BLACK if sum(color_data['rgb']) > 400 else WHITE
                name_surface = self.font.render(color_data['name'], True, text_color if can_afford else (120, 120, 120))
                price_surface = self.font.render(f"{color_data['cost']:,} Punkte", True, text_color if can_afford else (120, 120, 120))
                
                self.screen.blit(name_surface, (button_rect.x + 10, button_rect.y + 5))
                self.screen.blit(price_surface, (button_rect.x + 10, button_rect.y + 27))
            
            # If no colors available
            if not color_buttons:
                no_colors_text = self.large_font.render("Alle Farben bereits gekauft!", True, (100, 255, 100))
                self.screen.blit(no_colors_text, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 30))
            
            # Back button
            pygame.draw.rect(self.screen, LIGHT_GREY, back_button)
            pygame.draw.rect(self.screen, WHITE, back_button, 2)
            self.draw_text("Zurück", back_button.x + 60, back_button.y + 10)
            
            # Message
            if message:
                self.draw_text(message, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 130, message_color)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if back_button.collidepoint(event.pos):
                        return
                    
                    # Check color button clicks
                    for color_id, button_rect in color_buttons.items():
                        if button_rect.collidepoint(event.pos):
                            color_data = self.character_colors[color_id]
                            if self.total_score >= color_data['cost']:
                                # Purchase color
                                self.total_score -= color_data['cost']
                                self.owned_colors.append(color_id)
                                self.save_total_score()
                                message = f"{color_data['name']} gekauft!"
                                message_color = (100, 255, 100)
                                # Remove from available colors
                                del color_buttons[color_id]
                                
                                # Rebuild buttons
                                color_buttons.clear()
                                row = 0
                                col = 0
                                available_colors = {k: v for k, v in self.character_colors.items() 
                                                   if k not in self.owned_colors and k != 'white'}
                                for new_color_id, new_color_data in available_colors.items():
                                    x = start_x + col * (button_width + button_spacing)
                                    y = start_y + row * (button_height + button_spacing)
                                    color_buttons[new_color_id] = pygame.Rect(x, y, button_width, button_height)
                                    col += 1
                                    if col >= colors_per_row:
                                        col = 0
                                        row += 1
                                break
                            else:
                                message = "Nicht genug Punkte!"
                                message_color = (255, 100, 100)

    def show_wardrobe(self):
        """Wardrobe screen for selecting owned character colors"""
        back_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 40)
        
        # Create a grid of color buttons (3 columns)
        colors_per_row = 3
        button_size = 100
        sell_button_height = 30
        button_spacing = 20
        vertical_spacing = button_size + sell_button_height + 10  # Space for sell button
        start_x = SCREEN_WIDTH // 2 - (colors_per_row * button_size + (colors_per_row - 1) * button_spacing) // 2
        start_y = 180
        
        color_buttons = {}
        sell_buttons = {}
        row = 0
        col = 0
        
        # Create buttons for owned colors
        for color_id in self.owned_colors:
            x = start_x + col * (button_size + button_spacing)
            y = start_y + row * vertical_spacing
            color_buttons[color_id] = pygame.Rect(x, y, button_size, button_size)
            
            # Add sell button only for non-white colors
            if color_id != 'white':
                sell_buttons[color_id] = pygame.Rect(x, y + button_size + 5, button_size, sell_button_height)
            
            col += 1
            if col >= colors_per_row:
                col = 0
                row += 1
        
        message = ""
        message_color = WHITE
        
        while True:
            self.screen.fill(DARK_GREY)
            
            # Title
            title_text = self.large_font.render("KLEIDERSCHRANK", True, (100, 150, 200))
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - 200, 40))
            
            # Current selection and points
            current_color_name = self.character_colors[self.selected_color]['name']
            self.draw_text(f"Aktuelle Farbe: {current_color_name}", SCREEN_WIDTH // 2 - 100, 100)
            self.draw_text(f"Punkte: {self.total_score:,}", SCREEN_WIDTH // 2 - 60, 130)
            
            # Draw color buttons
            for color_id, button_rect in color_buttons.items():
                color_data = self.character_colors[color_id]
                
                # Button background
                pygame.draw.rect(self.screen, color_data['rgb'], button_rect)
                
                # Highlight selected color
                border_width = 5 if color_id == self.selected_color else 2
                border_color = (255, 215, 0) if color_id == self.selected_color else WHITE
                pygame.draw.rect(self.screen, border_color, button_rect, border_width)
                
                # Text
                text_color = BLACK if sum(color_data['rgb']) > 400 else WHITE
                name_surface = self.font.render(color_data['name'], True, text_color)
                # Center text
                text_rect = name_surface.get_rect(center=button_rect.center)
                self.screen.blit(name_surface, text_rect)
            
            # Draw sell buttons
            for color_id, sell_button_rect in sell_buttons.items():
                color_data = self.character_colors[color_id]
                sell_price = color_data['cost'] // 2  # 50% of original price
                
                # Sell button
                pygame.draw.rect(self.screen, (180, 50, 50), sell_button_rect)
                pygame.draw.rect(self.screen, WHITE, sell_button_rect, 1)
                
                # Sell text
                sell_text = self.font.render(f"Verkaufen: {sell_price:,}", True, WHITE)
                # Use smaller font for better fit
                small_font = pygame.font.SysFont("Arial", 16)
                sell_text = small_font.render(f"Verkauf: {sell_price:,}", True, WHITE)
                text_rect = sell_text.get_rect(center=sell_button_rect.center)
                self.screen.blit(sell_text, text_rect)
            
            # Back button
            pygame.draw.rect(self.screen, LIGHT_GREY, back_button)
            pygame.draw.rect(self.screen, WHITE, back_button, 2)
            self.draw_text("Zurück", back_button.x + 60, back_button.y + 10)
            
            # Message
            if message:
                self.draw_text(message, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 130, message_color)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if back_button.collidepoint(event.pos):
                        return
                    
                    # Check sell button clicks first
                    for color_id, sell_button_rect in sell_buttons.items():
                        if sell_button_rect.collidepoint(event.pos):
                            color_data = self.character_colors[color_id]
                            sell_price = color_data['cost'] // 2
                            
                            # Sell the color
                            self.total_score += sell_price
                            self.owned_colors.remove(color_id)
                            
                            # If selling the currently selected color, switch to white
                            if self.selected_color == color_id:
                                self.selected_color = 'white'
                            
                            self.save_total_score()
                            message = f"{color_data['name']} verkauft für {sell_price:,} Punkte!"
                            message_color = (255, 215, 0)
                            
                            # Rebuild buttons
                            color_buttons.clear()
                            sell_buttons.clear()
                            row = 0
                            col = 0
                            
                            for new_color_id in self.owned_colors:
                                x = start_x + col * (button_size + button_spacing)
                                y = start_y + row * vertical_spacing
                                color_buttons[new_color_id] = pygame.Rect(x, y, button_size, button_size)
                                
                                if new_color_id != 'white':
                                    sell_buttons[new_color_id] = pygame.Rect(x, y + button_size + 5, button_size, sell_button_height)
                                
                                col += 1
                                if col >= colors_per_row:
                                    col = 0
                                    row += 1
                            break
                    
                    # Check color button clicks
                    for color_id, button_rect in color_buttons.items():
                        if button_rect.collidepoint(event.pos):
                            self.selected_color = color_id
                            self.save_total_score()
                            color_name = self.character_colors[color_id]['name']
                            message = f"Farbe gewählt: {color_name}"
                            message_color = (100, 255, 100)
                            break


    def show_bullet_shop(self):
        """Bullet shop screen for buying bullet colors"""
        back_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 40)
        
        # Create a grid of color buttons (2 columns)
        colors_per_row = 2
        button_width = 220
        button_height = 50
        button_spacing = 20
        start_x = SCREEN_WIDTH // 2 - (colors_per_row * button_width + (colors_per_row - 1) * button_spacing) // 2
        start_y = 180
        
        color_buttons = {}
        row = 0
        col = 0
        
        # Create buttons for colors not yet owned (excluding white which is default)
        available_colors = {k: v for k, v in self.bullet_colors.items() 
                           if k not in self.owned_bullet_colors and k != 'white'}
        
        for color_id, color_data in available_colors.items():
            x = start_x + col * (button_width + button_spacing)
            y = start_y + row * (button_height + button_spacing)
            color_buttons[color_id] = pygame.Rect(x, y, button_width, button_height)
            col += 1
            if col >= colors_per_row:
                col = 0
                row += 1
        
        message = ""
        message_color = WHITE
        
        while True:
            self.screen.fill(DARK_GREY)
            
            # Title
            title_text = self.large_font.render("KUGEL-SHOP", True, (255, 150, 50))
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - 140, 40))
            
            # Current score
            self.draw_text(f"Verfügbare Punkte: {self.total_score:,}", SCREEN_WIDTH // 2 - 100, 100)
            self.draw_text(f"Farbenpreise wie im Charakter-Shop", SCREEN_WIDTH // 2 - 140, 130)
            
            # Draw color buttons
            for color_id, button_rect in color_buttons.items():
                color_data = self.bullet_colors[color_id]
                can_afford = self.total_score >= color_data['cost']
                
                # Button background
                button_color = color_data['rgb'] if can_afford else (60, 60, 60)
                pygame.draw.rect(self.screen, button_color, button_rect)
                pygame.draw.rect(self.screen, WHITE, button_rect, 3)
                
                # Text
                text_color = BLACK if sum(color_data['rgb']) > 400 else WHITE
                name_surface = self.font.render(color_data['name'], True, text_color if can_afford else (120, 120, 120))
                price_surface = self.font.render(f"{color_data['cost']:,} Punkte", True, text_color if can_afford else (120, 120, 120))
                
                self.screen.blit(name_surface, (button_rect.x + 10, button_rect.y + 5))
                self.screen.blit(price_surface, (button_rect.x + 10, button_rect.y + 27))
            
            # If no colors available
            if not color_buttons:
                no_colors_text = self.large_font.render("Alle Farben bereits gekauft!", True, (100, 255, 100))
                self.screen.blit(no_colors_text, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 30))
            
            # Back button
            pygame.draw.rect(self.screen, LIGHT_GREY, back_button)
            pygame.draw.rect(self.screen, WHITE, back_button, 2)
            self.draw_text("Zurück", back_button.x + 60, back_button.y + 10)
            
            # Message
            if message:
                self.draw_text(message, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 130, message_color)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if back_button.collidepoint(event.pos):
                        return
                    
                    # Check color button clicks
                    for color_id, button_rect in color_buttons.items():
                        if button_rect.collidepoint(event.pos):
                            color_data = self.bullet_colors[color_id]
                            if self.total_score >= color_data['cost']:
                                # Purchase color
                                self.total_score -= color_data['cost']
                                self.owned_bullet_colors.append(color_id)
                                self.save_total_score()
                                message = f"{color_data['name']} gekauft!"
                                message_color = (100, 255, 100)
                                # Remove from available colors
                                del color_buttons[color_id]
                                
                                # Rebuild buttons
                                color_buttons.clear()
                                row = 0
                                col = 0
                                available_colors = {k: v for k, v in self.bullet_colors.items() 
                                                   if k not in self.owned_bullet_colors and k != 'white'}
                                for new_color_id, new_color_data in available_colors.items():
                                    x = start_x + col * (button_width + button_spacing)
                                    y = start_y + row * (button_height + button_spacing)
                                    color_buttons[new_color_id] = pygame.Rect(x, y, button_width, button_height)
                                    col += 1
                                    if col >= colors_per_row:
                                        col = 0
                                        row += 1
                                break
                            else:
                                message = "Nicht genug Punkte!"
                                message_color = (255, 100, 100)

    def show_bullet_wardrobe(self):
        """Bullet wardrobe screen for selecting owned bullet colors"""
        back_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 40)
        
        # Create a grid of color buttons (3 columns)
        colors_per_row = 3
        button_size = 100
        sell_button_height = 30
        button_spacing = 20
        vertical_spacing = button_size + sell_button_height + 10  # Space for sell button
        start_x = SCREEN_WIDTH // 2 - (colors_per_row * button_size + (colors_per_row - 1) * button_spacing) // 2
        start_y = 180
        
        color_buttons = {}
        sell_buttons = {}
        row = 0
        col = 0
        
        # Create buttons for owned colors
        for color_id in self.owned_bullet_colors:
            x = start_x + col * (button_size + button_spacing)
            y = start_y + row * vertical_spacing
            color_buttons[color_id] = pygame.Rect(x, y, button_size, button_size)
            
            # Add sell button only for non-white colors
            if color_id != 'white':
                sell_buttons[color_id] = pygame.Rect(x, y + button_size + 5, button_size, sell_button_height)
            
            col += 1
            if col >= colors_per_row:
                col = 0
                row += 1
        
        message = ""
        message_color = WHITE
        
        while True:
            self.screen.fill(DARK_GREY)
            
            # Title
            title_text = self.large_font.render("KUGEL-FARBEN", True, (200, 200, 50))
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - 160, 40))
            
            # Current selection and points
            current_color_name = self.bullet_colors[self.selected_bullet_color]['name']
            self.draw_text(f"Aktuelle Farbe: {current_color_name}", SCREEN_WIDTH // 2 - 100, 100)
            self.draw_text(f"Punkte: {self.total_score:,}", SCREEN_WIDTH // 2 - 60, 130)
            
            # Draw color buttons
            for color_id, button_rect in color_buttons.items():
                color_data = self.bullet_colors[color_id]
                
                # Button background
                pygame.draw.rect(self.screen, color_data['rgb'], button_rect)
                
                # Highlight selected color
                border_width = 5 if color_id == self.selected_bullet_color else 2
                border_color = (255, 215, 0) if color_id == self.selected_bullet_color else WHITE
                pygame.draw.rect(self.screen, border_color, button_rect, border_width)
                
                # Text
                text_color = BLACK if sum(color_data['rgb']) > 400 else WHITE
                name_surface = self.font.render(color_data['name'], True, text_color)
                # Center text
                text_rect = name_surface.get_rect(center=button_rect.center)
                self.screen.blit(name_surface, text_rect)
            
            # Draw sell buttons
            for color_id, sell_button_rect in sell_buttons.items():
                color_data = self.bullet_colors[color_id]
                sell_price = color_data['cost'] // 2  # 50% of original price
                
                # Sell button
                pygame.draw.rect(self.screen, (180, 50, 50), sell_button_rect)
                pygame.draw.rect(self.screen, WHITE, sell_button_rect, 1)
                
                # Sell text
                small_font = pygame.font.SysFont("Arial", 16)
                sell_text = small_font.render(f"Verkauf: {sell_price:,}", True, WHITE)
                text_rect = sell_text.get_rect(center=sell_button_rect.center)
                self.screen.blit(sell_text, text_rect)
            
            # Back button
            pygame.draw.rect(self.screen, LIGHT_GREY, back_button)
            pygame.draw.rect(self.screen, WHITE, back_button, 2)
            self.draw_text("Zurück", back_button.x + 60, back_button.y + 10)
            
            # Message
            if message:
                self.draw_text(message, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 130, message_color)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if back_button.collidepoint(event.pos):
                        return
                    
                    # Check sell button clicks first
                    for color_id, sell_button_rect in sell_buttons.items():
                        if sell_button_rect.collidepoint(event.pos):
                            color_data = self.bullet_colors[color_id]
                            sell_price = color_data['cost'] // 2
                            
                            # Sell the color
                            self.total_score += sell_price
                            self.owned_bullet_colors.remove(color_id)
                            
                            # If selling the currently selected color, switch to white
                            if self.selected_bullet_color == color_id:
                                self.selected_bullet_color = 'white'
                            
                            self.save_total_score()
                            message = f"{color_data['name']} verkauft für {sell_price:,} Punkte!"
                            message_color = (255, 215, 0)
                            
                            # Rebuild buttons
                            color_buttons.clear()
                            sell_buttons.clear()
                            row = 0
                            col = 0
                            
                            for new_color_id in self.owned_bullet_colors:
                                x = start_x + col * (button_size + button_spacing)
                                y = start_y + row * vertical_spacing
                                color_buttons[new_color_id] = pygame.Rect(x, y, button_size, button_size)
                                
                                if new_color_id != 'white':
                                    sell_buttons[new_color_id] = pygame.Rect(x, y + button_size + 5, button_size, sell_button_height)
                                
                                col += 1
                                if col >= colors_per_row:
                                    col = 0
                                    row += 1
                            break
                    
                    # Check color button clicks
                    for color_id, button_rect in color_buttons.items():
                        if button_rect.collidepoint(event.pos):
                            self.selected_bullet_color = color_id
                            self.save_total_score()
                            color_name = self.bullet_colors[color_id]['name']
                            message = f"Farbe gewählt: {color_name}"
                            message_color = (100, 255, 100)
                            break


    def show_kill_animation_shop(self):
        """Kill animation shop screen for buying death animations"""
        back_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 40)
        
        # Create buttons for animations (1 column layout)
        button_width = 400
        button_height = 60
        button_spacing = 20
        start_x = SCREEN_WIDTH // 2 - button_width // 2
        start_y = 180
        
        anim_buttons = {}
        row = 0
        
        # Create buttons for animations not yet owned (excluding 'none')
        available_anims = {k: v for k, v in self.kill_animations.items() 
                          if k not in self.owned_kill_animations and k != 'none'}
        
        for anim_id, anim_data in available_anims.items():
            y = start_y + row * (button_height + button_spacing)
            anim_buttons[anim_id] = pygame.Rect(start_x, y, button_width, button_height)
            row += 1
        
        message = ""
        message_color = WHITE
        
        while True:
            self.screen.fill(DARK_GREY)
            
            # Title
            title_text = self.large_font.render("KILL-ANIMATIONEN", True, (150, 50, 150))
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - 190, 40))
            
            # Current score
            self.draw_text(f"Verfügbare Punktе: {self.total_score:,}", SCREEN_WIDTH // 2 - 100, 100)
            
            # Info about current selection  
            current_anim_name = self.kill_animations[self.selected_kill_animation]['name']
            self.draw_text(f"Gewählt: {current_anim_name}", SCREEN_WIDTH // 2 - 70, 130)
            
            # Draw animation buttons
            for anim_id, button_rect in anim_buttons.items():
                anim_data = self.kill_animations[anim_id]
                can_afford = self.total_score >= anim_data['cost']
                
                # Button background
                button_color = (100, 100, 100) if can_afford else (50, 50, 50)
                pygame.draw.rect(self.screen, button_color, button_rect)
                pygame.draw.rect(self.screen, WHITE if can_afford else (80, 80, 80), button_rect, 3)
                
                # Text
                text_color = WHITE if can_afford else (120, 120, 120)
                name_surface = self.font.render(anim_data['name'], True, text_color)
                price_surface = self.font.render(f"{anim_data['cost']:,} Punkte", True, text_color)
                duration_surface = self.font.render(f"Dauer: {anim_data['duration']/1000:.1f}s", True, text_color)
                
                self.screen.blit(name_surface, (button_rect.x + 15, button_rect.y + 8))
                self.screen.blit(price_surface, (button_rect.x + 15, button_rect.y + 32))
                self.screen.blit(duration_surface, (button_rect.x + 250, button_rect.y + 20))
            
            # If no animations available
            if not anim_buttons:
                no_anims_text = self.large_font.render("Alle Animationen gekauft!", True, (100, 255, 100))
                self.screen.blit(no_anims_text, (SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2 - 30))
            
            # Back button
            pygame.draw.rect(self.screen, LIGHT_GREY, back_button)
            pygame.draw.rect(self.screen, WHITE, back_button, 2)
            self.draw_text("Zurück", back_button.x + 60, back_button.y + 10)
            
            # Message
            if message:
                self.draw_text(message, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 130, message_color)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if back_button.collidepoint(event.pos):
                        return
                    
                    # Check animation button clicks
                    for anim_id, button_rect in anim_buttons.items():
                        if button_rect.collidepoint(event.pos):
                            anim_data = self.kill_animations[anim_id]
                            if self.total_score >= anim_data['cost']:
                                # Purchase animation
                                self.total_score -= anim_data['cost']
                                self.owned_kill_animations.append(anim_id)
                                # Auto-select newly purchased animation
                                self.selected_kill_animation = anim_id
                                self.save_total_score()
                                message = f"{anim_data['name']} gekauft und gewählt!"
                                message_color = (100, 255, 100)
                                # Remove from available animations
                                del anim_buttons[anim_id]
                                
                                # Rebuild buttons
                                anim_buttons.clear()
                                row = 0
                                available_anims = {k: v for k, v in self.kill_animations.items() 
                                                  if k not in self.owned_kill_animations and k != 'none'}
                                for new_anim_id, new_anim_data in available_anims.items():
                                    y = start_y + row * (button_height + button_spacing)
                                    anim_buttons[new_anim_id] = pygame.Rect(start_x, y, button_width, button_height)
                                    row += 1
                                break
                            else:
                                message = "Nicht genug Punkte!"
                                message_color = (255, 100, 100)


    def show_kill_animation_wardrobe(self):
        """Kill animation wardrobe screen for selecting owned animations"""
        back_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 40)
        
        # Create buttons for owned animations (1 column layout)
        button_width = 400
        button_height = 60
        button_spacing = 15
        start_x = SCREEN_WIDTH // 2 - button_width // 2
        start_y = 180
        
        anim_buttons = {}
        sell_buttons = {}
        row = 0
        
        # Create buttons for owned animations
        for anim_id in self.owned_kill_animations:
            y = start_y + row * (button_height + button_spacing + 35)  # Extra space for sell button
            anim_buttons[anim_id] = pygame.Rect(start_x, y, button_width, button_height)
            
            # Add sell button only for non-'none' animations
            if anim_id != 'none':
                sell_buttons[anim_id] = pygame.Rect(start_x, y + button_height + 5, button_width, 30)
            
            row += 1
        
        message = ""
        message_color = WHITE
        
        while True:
            self.screen.fill(DARK_GREY)
            
            # Title
            title_text = self.large_font.render("ANIMATIONS-AUSWAHL", True, (200, 100, 150))
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - 220, 40))
            
            # Current selection and points
            current_anim_name = self.kill_animations[self.selected_kill_animation]['name']
            self.draw_text(f"Aktuelle Animation: {current_anim_name}", SCREEN_WIDTH // 2 - 110, 100)
            self.draw_text(f"Punkte: {self.total_score:,}", SCREEN_WIDTH // 2 - 60, 130)
            
            # Draw animation buttons
            for anim_id, button_rect in anim_buttons.items():
                anim_data = self.kill_animations[anim_id]
                
                # Button background
                is_selected = anim_id == self.selected_kill_animation
                button_color = (120, 120, 120) if is_selected else (80, 80, 80)
                pygame.draw.rect(self.screen, button_color, button_rect)
                
                # Highlight selected animation
                border_width = 5 if is_selected else 2
                border_color = (255, 215, 0) if is_selected else WHITE
                pygame.draw.rect(self.screen, border_color, button_rect, border_width)
                
                # Text
                name_surface = self.font.render(anim_data['name'], True, WHITE)
                duration_surface = self.font.render(f"Dauer: {anim_data['duration']/1000:.1f}s", True, (200, 200, 200))
                
                self.screen.blit(name_surface, (button_rect.x + 15, button_rect.y + 12))
                self.screen.blit(duration_surface, (button_rect.x + 250, button_rect.y + 12))
            
            # Draw sell buttons
            for anim_id, sell_button_rect in sell_buttons.items():
                anim_data = self.kill_animations[anim_id]
                sell_price = anim_data['cost'] // 2  # 50% of original price
                
                # Sell button
                pygame.draw.rect(self.screen, (180, 50, 50), sell_button_rect)
                pygame.draw.rect(self.screen, WHITE, sell_button_rect, 1)
                
                # Sell text
                sell_text = self.font.render(f"Verkaufen für {sell_price:,} Punkte", True, WHITE)
                text_rect = sell_text.get_rect(center=sell_button_rect.center)
                self.screen.blit(sell_text, text_rect)
            
            # Back button
            pygame.draw.rect(self.screen, LIGHT_GREY, back_button)
            pygame.draw.rect(self.screen, WHITE, back_button, 2)
            self.draw_text("Zurück", back_button.x + 60, back_button.y + 10)
            
            # Message
            if message:
                self.draw_text(message, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 130, message_color)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if back_button.collidepoint(event.pos):
                        return
                    
                    # Check sell button clicks first
                    for anim_id, sell_button_rect in sell_buttons.items():
                        if sell_button_rect.collidepoint(event.pos):
                            anim_data = self.kill_animations[anim_id]
                            sell_price = anim_data['cost'] // 2
                            
                            # Sell the animation
                            self.total_score += sell_price
                            self.owned_kill_animations.remove(anim_id)
                            
                            # If selling the currently selected animation, switch to 'none'
                            if self.selected_kill_animation == anim_id:
                                self.selected_kill_animation = 'none'
                            
                            self.save_total_score()
                            message = f"{anim_data['name']} verkauft für {sell_price:,} Punkte!"
                            message_color = (255, 215, 0)
                            
                            # Rebuild buttons
                            anim_buttons.clear()
                            sell_buttons.clear()
                            row = 0
                            
                            for new_anim_id in self.owned_kill_animations:
                                y = start_y + row * (button_height + button_spacing + 35)
                                anim_buttons[new_anim_id] = pygame.Rect(start_x, y, button_width, button_height)
                                
                                if new_anim_id != 'none':
                                    sell_buttons[new_anim_id] = pygame.Rect(start_x, y + button_height + 5, button_width, 30)
                                
                                row += 1
                            break
                    
                    # Check animation button clicks
                    for anim_id, button_rect in anim_buttons.items():
                        if button_rect.collidepoint(event.pos):
                            self.selected_kill_animation = anim_id
                            self.save_total_score()
                            anim_name = self.kill_animations[anim_id]['name']
                            message = f"Animation gewählt: {anim_name}"
                            message_color = (100, 255, 100)
                            break


    def show_go_screen(self):
        # Game over screen with 3 second auto-return
        self.screen.fill(DARK_GREY)

        if self.game_mode == 'team5v5':
            # Team mode game over screen
            if self.team_blue_score > self.team_red_score:
                winner_text = "TEAM BLAU GEWINNT!"
                winner_color = (50, 50, 255)
            elif self.team_red_score > self.team_blue_score:
                winner_text = "TEAM ROT GEWINNT!"
                winner_color = (255, 50, 50)
            else:
                winner_text = "UNENTSCHIEDEN!"
                winner_color = (255, 255, 0)

            # Display winner
            winner_surf = self.large_font.render(winner_text, True, winner_color)
            self.screen.blit(winner_surf, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 80))

            # Display final scores
            self.draw_text(f"Team Blau: {self.team_blue_score} Punkte", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 20, (50, 50, 255))
            self.draw_text(f"Team Rot: {self.team_red_score} Punkte", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20, (255, 50, 50))

            # Add winning team score to total score
            if self.team_blue_score > self.team_red_score:
                self.total_score += self.team_blue_score
                self.save_total_score()
                self.draw_text(f"Neue Gesamtpunkte: {self.total_score:,}", SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 60, (255, 215, 0))
        else:
            # Normal mode game over screen
            # Add current game score to total score
            self.total_score += self.score
            self.save_total_score()

            self.draw_text("GAME OVER", SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 - 80)
            self.draw_text(f"Erreichte Punkte: {self.score}", SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 20)
            self.draw_text(f"Neue Gesamtpunkte: {self.total_score:,}", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20)

        self.draw_text("Zurück zum Startbildschirm...", SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 110)
        pygame.display.flip()
        
        # Wait 3 seconds or quit
        start_wait = pygame.time.get_ticks()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
            
            # Auto-return after 3 seconds
            if pygame.time.get_ticks() - start_wait > 3000:
                waiting = False

    def show_special_shop(self):
        """Special shop for buying unique items like the Mini-Map"""
        back_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 40)
        buy_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 160, 200, 40)
        
        minimap_price = 1000000
        
        message = ""
        message_color = WHITE
        
        while True:
            self.screen.fill(DARK_GREY)
            
            # Title
            title_text = self.large_font.render("SPEZIAL-SHOP", True, (100, 100, 255))
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - 150, 50))
            
            # Current score
            self.draw_text(f"Verfügbare Punkte: {self.total_score:,}", SCREEN_WIDTH // 2 - 100, 120)
            
            # Item Display: Mini-Map
            item_y = 200
            pygame.draw.rect(self.screen, (60, 60, 80), (SCREEN_WIDTH // 2 - 200, item_y, 400, 150))
            pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH // 2 - 200, item_y, 400, 150), 2)
            
            self.draw_text("Mini-Map", SCREEN_WIDTH // 2 - 40, item_y + 20, (255, 255, 0))
            self.draw_text("Zeigt Gegner & Gebäude an", SCREEN_WIDTH // 2 - 110, item_y + 60)
            self.draw_text(f"Preis: {minimap_price:,} Punkte", SCREEN_WIDTH // 2 - 90, item_y + 100)
            
            # Buy/Sell button logic
            if self.minimap_owned:
                # Sell button
                sell_price = minimap_price // 2
                pygame.draw.rect(self.screen, (180, 50, 50), buy_button)
                pygame.draw.rect(self.screen, WHITE, buy_button, 2)
                self.draw_text(f"Verkaufen ({sell_price})", buy_button.x + 30, buy_button.y + 10)
            else:
                # Buy button
                can_afford = self.total_score >= minimap_price
                button_color = (100, 200, 100) if can_afford else (100, 100, 100)
                pygame.draw.rect(self.screen, button_color, buy_button)
                pygame.draw.rect(self.screen, WHITE, buy_button, 2)
                self.draw_text("Kaufen", buy_button.x + 60, buy_button.y + 10)
            
            # Back button
            pygame.draw.rect(self.screen, LIGHT_GREY, back_button)
            pygame.draw.rect(self.screen, WHITE, back_button, 2)
            self.draw_text("Zurück", back_button.x + 60, back_button.y + 10)
            
            # Message
            if message:
                self.draw_text(message, SCREEN_WIDTH // 2 - 150, 420, message_color)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if back_button.collidepoint(event.pos):
                        return
                    elif buy_button.collidepoint(event.pos):
                        if self.minimap_owned:
                            # Sell Mini-Map
                            sell_price = minimap_price // 2
                            self.total_score += sell_price
                            self.minimap_owned = False
                            self.save_total_score()
                            message = f"Mini-Map für {sell_price} verkauft!"
                            message_color = (255, 215, 0)
                        elif not self.minimap_owned:
                            # Buy Mini-Map
                            if self.total_score >= minimap_price:
                                self.total_score -= minimap_price
                                self.minimap_owned = True
                                self.save_total_score()
                                message = "Mini-Map gekauft!"
                                message_color = (100, 255, 100)
                            else:
                                message = "Nicht genug Punkte!"
                                message_color = (255, 100, 100)

    def show_special_wardrobe(self):
        """Wardrobe for equipping/unequipping special items"""
        back_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 40)
        toggle_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 160, 200, 40)
        
        message = ""
        message_color = WHITE
        
        while True:
            self.screen.fill(DARK_GREY)
            
            # Title
            title_text = self.large_font.render("SPEZIAL-SCHRANK", True, (150, 100, 200))
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - 180, 50))
            
            # Item Display: Mini-Map
            item_y = 200
            pygame.draw.rect(self.screen, (60, 60, 80), (SCREEN_WIDTH // 2 - 200, item_y, 400, 150))
            
            # Border color based on active state
            border_color = (0, 255, 0) if self.minimap_active else WHITE
            border_width = 4 if self.minimap_active else 2
            pygame.draw.rect(self.screen, border_color, (SCREEN_WIDTH // 2 - 200, item_y, 400, 150), border_width)
            
            self.draw_text("Mini-Map", SCREEN_WIDTH // 2 - 40, item_y + 20, (255, 255, 0))
            
            status_text = "AUSGERÜSTET" if self.minimap_active else "NICHT AUSGERÜSTET"
            status_color = (0, 255, 0) if self.minimap_active else (200, 200, 200)
            self.draw_text(status_text, SCREEN_WIDTH // 2 - 80, item_y + 60, status_color)
            
            if not self.minimap_owned:
                self.draw_text("(Nicht im Besitz)", SCREEN_WIDTH // 2 - 70, item_y + 100, (200, 100, 100))
            
            # Toggle button logic
            if self.minimap_owned:
                button_text = "Ablegen" if self.minimap_active else "Ausrüsten"
                button_color = (150, 50, 50) if self.minimap_active else (50, 150, 50)
                
                pygame.draw.rect(self.screen, button_color, toggle_button)
                pygame.draw.rect(self.screen, WHITE, toggle_button, 2)
                self.draw_text(button_text, toggle_button.x + 60, toggle_button.y + 10)
            else:
                # Disabled button if not owned
                pygame.draw.rect(self.screen, (80, 80, 80), toggle_button)
                pygame.draw.rect(self.screen, (150, 150, 150), toggle_button, 2)
                self.draw_text("Nicht verfügbar", toggle_button.x + 40, toggle_button.y + 10)
            
            # Back button
            pygame.draw.rect(self.screen, LIGHT_GREY, back_button)
            pygame.draw.rect(self.screen, WHITE, back_button, 2)
            self.draw_text("Zurück", back_button.x + 60, back_button.y + 10)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if back_button.collidepoint(event.pos):
                        return
                    elif toggle_button.collidepoint(event.pos):
                        if self.minimap_owned:
                            self.minimap_active = not self.minimap_active
                            self.save_total_score()

    def load_total_score(self):
        """Load total score and weapon upgrades from JSON file"""
        try:
            if os.path.exists(self.score_file):
                with open(self.score_file, 'r') as f:
                    data = json.load(f)
                    # Load upgrades if they exist
                    if 'weapon_upgrades' in data:
                        # Will be set after __init__ completes, so we return it separately
                        self.saved_upgrades = data.get('weapon_upgrades', {})
                    # Load purchase counter
                    if 'total_upgrades_purchased' in data:
                        self.saved_purchase_count = data.get('total_upgrades_purchased', 0)
                    # Load color data
                    if 'owned_colors' in data:
                        self.saved_owned_colors = data.get('owned_colors', ['white'])
                    if 'selected_color' in data:
                        self.saved_selected_color = data.get('selected_color', 'white')
                    # Load bullet color data
                    if 'owned_bullet_colors' in data:
                        self.saved_owned_bullet_colors = data.get('owned_bullet_colors', ['white'])
                    if 'selected_bullet_color' in data:
                        self.saved_selected_bullet_color = data.get('selected_bullet_color', 'white')
                    # Load kill animation data
                    if 'owned_kill_animations' in data:
                        self.saved_owned_kill_animations = data.get('owned_kill_animations', ['none'])
                    if 'selected_kill_animation' in data:
                        self.saved_selected_kill_animation = data.get('selected_kill_animation', 'none')
                    # Load minimap ownership
                    if 'minimap_owned' in data:
                        self.saved_minimap_owned = data.get('minimap_owned', False)
                    if 'minimap_active' in data:
                        self.saved_minimap_active = data.get('minimap_active', False)
                    # Load AI aim difficulty
                    if 'ai_aim_difficulty' in data:
                        self.saved_ai_aim_difficulty = data.get('ai_aim_difficulty', 'normal')
                    # Load AI dodge difficulty
                    if 'ai_dodge_difficulty' in data:
                        self.saved_ai_dodge_difficulty = data.get('ai_dodge_difficulty', 'normal')
                    # Load tutorial completion
                    if 'tutorial_completed' in data:
                        self.saved_tutorial_completed = data.get('tutorial_completed', False)
                    # Load game mode
                    if 'game_mode' in data:
                        self.saved_game_mode = data.get('game_mode', 'classic')
                    return data.get('total_score', 0)
        except Exception as e:
            print(f"Error loading score: {e}")
        return 0
    
    def save_total_score(self):
        """Save total score and weapon upgrades to JSON file"""
        try:
            with open(self.score_file, 'w') as f:
                json.dump({
                    'total_score': self.total_score,
                    'weapon_upgrades': self.weapon_upgrades,
                    'total_upgrades_purchased': self.total_upgrades_purchased,
                    'owned_colors': self.owned_colors,
                    'selected_color': self.selected_color,
                    'owned_bullet_colors': self.owned_bullet_colors,
                    'selected_bullet_color': self.selected_bullet_color,
                    'owned_kill_animations': self.owned_kill_animations,
                    'selected_kill_animation': self.selected_kill_animation,
                    'minimap_owned': self.minimap_owned,
                    'minimap_active': self.minimap_active,
                    'ai_aim_difficulty': self.ai_aim_difficulty,
                    'ai_dodge_difficulty': self.ai_dodge_difficulty,
                    'tutorial_completed': self.tutorial_completed,
                    'game_mode': self.game_mode
                }, f)
        except Exception as e:
            print(f"Error saving score: {e}")
    
    def show_tutorial(self):
        """Interactive in-game tutorial"""
        self.new(tutorial_mode=True)

if __name__ == "__main__":
    g = Game()
    # Show tutorial for new players
    if not g.tutorial_completed:
        g.show_tutorial()
    g.show_start_screen()
    while g.running:
        g.new()
        g.show_go_screen()
        # Return to start screen after game over
        if g.running:  # Only show start screen if not quitting
            g.show_start_screen()
    pygame.quit()
    sys.exit()

