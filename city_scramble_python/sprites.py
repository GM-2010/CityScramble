import pygame
import random
from settings import *
vec = pygame.math.Vector2

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = vec()
        self.half_w = self.display_surface.get_size()[0] // 2
        self.half_h = self.display_surface.get_size()[1] // 2
        
        # Create a map surface (optional, but good for performance if static)
        # For now, we'll just draw a grid dynamically or a large background rect
        self.ground_surf = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
        self.ground_surf.fill(DARK_GREY)
        # Draw grid
        for x in range(0, MAP_WIDTH, 100):
            pygame.draw.line(self.ground_surf, LIGHT_GREY, (x, 0), (x, MAP_HEIGHT))
        for y in range(0, MAP_HEIGHT, 100):
            pygame.draw.line(self.ground_surf, LIGHT_GREY, (0, y), (MAP_WIDTH, y))
        self.ground_rect = self.ground_surf.get_rect(topleft=(0, 0))

    def custom_draw(self, player):
        # Calculate offset
        self.offset.x = player.rect.centerx - self.half_w
        self.offset.y = player.rect.centery - self.half_h

        # Keep camera within map bounds (optional, but good polish)
        self.offset.x = max(0, min(self.offset.x, MAP_WIDTH - SCREEN_WIDTH))
        self.offset.y = max(0, min(self.offset.y, MAP_HEIGHT - SCREEN_HEIGHT))

        # Draw ground
        ground_offset = self.ground_rect.topleft - self.offset
        self.display_surface.blit(self.ground_surf, ground_offset)

        # Draw sprites
        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        # Use selected character color from game
        player_color = game.character_colors[game.selected_color]['rgb']
        self.image.fill(player_color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.last_shot = 0
        self.weapon = 'pistol'
        self.facing_dir = vec(1, 0) # Default facing right
        self.hit_count = 0  # Track hits from enemies
        self.last_action_time = pygame.time.get_ticks()  # For regeneration
        self.last_regen_time = pygame.time.get_ticks()  # For regeneration interval
        self.rainbow_hue = 0  # For rainbow animation

    def get_keys(self):
        self.vel = vec(0, 0)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel.x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel.x = PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vel.y = -PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vel.y = PLAYER_SPEED
        
        # Mouse Aiming
        mx, my = pygame.mouse.get_pos()
        # Adjust mouse pos by camera offset
        camera_offset = self.game.all_sprites.offset
        world_mouse_pos = vec(mx, my) + camera_offset
        
        mouse_dir = world_mouse_pos - self.pos
        if mouse_dir.length() > 0:
            self.facing_dir = mouse_dir.normalize()

        if pygame.mouse.get_pressed()[0]: # Left click
            self.game.shoot(self)
            self.last_action_time = pygame.time.get_ticks()  # Reset regen timer
        
        if pygame.mouse.get_pressed()[2]: # Right click - shoot at buildings
            self.game.shoot_at_building(self, world_mouse_pos)
            self.last_action_time = pygame.time.get_ticks()  # Reset regen timer
        
        # Normalize diagonal movement
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071

    def update(self):
        self.get_keys()
        self.pos += self.vel * self.game.dt
        
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')

        # Boundary checks
        if self.pos.x < 0: self.pos.x = 0
        if self.pos.x > MAP_WIDTH - PLAYER_SIZE: self.pos.x = MAP_WIDTH - PLAYER_SIZE
        if self.pos.y < 0: self.pos.y = 0
        if self.pos.y > MAP_HEIGHT - PLAYER_SIZE: self.pos.y = MAP_HEIGHT - PLAYER_SIZE
        
        # Sync rect with pos after boundary checks
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        
        # Regeneration system: heal 1 hit every 5 seconds after 7 seconds of inactivity
        now = pygame.time.get_ticks()
        time_since_action = now - self.last_action_time
        
        if time_since_action >= 7000 and self.hit_count > 0:  # 7 seconds
            time_since_regen = now - self.last_regen_time
            if time_since_regen >= 5000:  # 5 seconds between regenerations
                self.hit_count -= 1
                self.last_regen_time = now
        
        # Rainbow color animation
        if self.game.selected_color == 'rainbow':
            self.rainbow_hue = (self.rainbow_hue + 2) % 360  # Cycle through hues
            # Convert HSV to RGB
            import colorsys
            rgb = colorsys.hsv_to_rgb(self.rainbow_hue / 360.0, 1.0, 1.0)
            color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
            self.image.fill(color)

    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - self.rect.width
                if self.vel.x < 0:
                    self.pos.x = hits[0].rect.right
                self.vel.x = 0
                self.rect.x = self.pos.x
        if dir == 'y':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.rect.height
                if self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                self.rect.y = self.pos.y



class Obstacle(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls, game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((w, h))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hp = 10  # Buildings have 10 HP
        self.max_hp = 10
        # Store original position and size for respawning
        self.original_x = x
        self.original_y = y
        self.original_w = w
        self.original_h = h
    
    def take_damage(self, amount):
        """Take damage and destroy if HP reaches 0"""
        self.hp -= amount
        # Visual feedback - darken when damaged
        damage_percent = self.hp / self.max_hp
        color_value = int(139 * damage_percent)  # BROWN = (139, 69, 19)
        self.image.fill((color_value, int(69 * damage_percent), int(19 * damage_percent)))
        
        if self.hp <= 0:
            # Schedule respawn
            self.game.schedule_obstacle_respawn(self.original_x, self.original_y, 
                                                self.original_w, self.original_h)
            self.kill()

class Projectile(pygame.sprite.Sprite):
    def __init__(self, game, x, y, dir_x, dir_y, owner, damage, speed, lifetime, color, is_rainbow=False):
        self.groups = game.all_sprites, game.projectiles
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.owner = owner
        self.damage = damage
        self.image = pygame.Surface((10, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vel = vec(dir_x, dir_y) * speed
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = lifetime
        self.is_rainbow = is_rainbow
        self.rainbow_hue = 0

    def update(self):
        self.rect.center += self.vel * self.game.dt
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()
        if pygame.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        
        # Rainbow animation
        if self.is_rainbow:
            self.rainbow_hue = (self.rainbow_hue + 5) % 360
            import colorsys
            rgb = colorsys.hsv_to_rgb(self.rainbow_hue / 360.0, 1.0, 1.0)
            color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
            self.image.fill(color)
            
        # Check collision with enemies
        if self.owner == 'player':
            hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
            for hit in hits:
                hit.take_damage(self.damage)
                self.kill()
        elif self.owner == 'enemy':
            if pygame.sprite.collide_rect(self, self.game.player):
                # Increase hit counter
                self.game.player.hit_count += 1
                # Reset regeneration timer when hit
                self.game.player.last_action_time = pygame.time.get_ticks()
                self.game.player.last_regen_time = pygame.time.get_ticks()
                self.kill()

class BuildingProjectile(pygame.sprite.Sprite):
    """Special projectile for destroying buildings"""
    def __init__(self, game, x, y, dir_x, dir_y, damage, speed, lifetime, color):
        self.groups = game.all_sprites, game.projectiles
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.damage = damage
        self.image = pygame.Surface((10, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vel = vec(dir_x, dir_y) * speed
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = lifetime

    def update(self):
        self.rect.center += self.vel * self.game.dt
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()
        
        # Check collision with walls/obstacles
        hits = pygame.sprite.spritecollide(self, self.game.walls, False)
        for obstacle in hits:
            obstacle.take_damage(self.damage)
            self.kill()
            break


class Grenade(Projectile):
    def __init__(self, game, x, y, dir_x, dir_y, owner, damage, speed, lifetime, color, is_rainbow=False):
        super().__init__(game, x, y, dir_x, dir_y, owner, damage, speed, lifetime, color, is_rainbow)
        self.explosion_radius = 100  # Area damage radius
        
    def update(self):
        self.rect.center += self.vel * self.game.dt
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.explode()
            self.kill()
        # NOTE: No wall collision check! Grenades fly over buildings
        
        # Rainbow animation
        if self.is_rainbow:
            self.rainbow_hue = (self.rainbow_hue + 5) % 360
            import colorsys
            rgb = colorsys.hsv_to_rgb(self.rainbow_hue / 360.0, 1.0, 1.0)
            color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
            self.image.fill(color)
            
        # Check collision with enemies for direct hit
        if self.owner == 'player':
            hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
            if hits:
                self.explode()
                self.kill()
        elif self.owner == 'enemy':
            if pygame.sprite.collide_rect(self, self.game.player):
                # Increase hit counter
                self.game.player.hit_count += 1
                self.kill()
    
    def explode(self):
        # Deal area damage to all enemies within explosion radius
        if self.owner == 'player':
            for enemy in self.game.enemies:
                dist = vec(enemy.rect.centerx - self.rect.centerx, 
                          enemy.rect.centery - self.rect.centery).length()
                if dist <= self.explosion_radius:
                    enemy.take_damage(self.damage)


class HitMarker(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # Larger surface for better visibility
        self.image = pygame.Surface((60, 40))
        self.image.fill(DARK_GREY)  # Background color (transparent effect)
        self.image.set_colorkey(DARK_GREY)  # Make background transparent
        
        # Draw white background circle for contrast
        pygame.draw.circle(self.image, WHITE, (30, 20), 25)  # White background
        pygame.draw.circle(self.image, BLACK, (30, 20), 25, 2)  # Black border
        
        # Draw "HIT!" text - larger and bolder
        font = pygame.font.SysFont("Arial", 24, bold=True)
        text = font.render("HIT!", True, RED)
        text_rect = text.get_rect(center=(30, 20))
        self.image.blit(text, text_rect)
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 400  # Show for 400ms (slightly longer)
        self.alpha = 255  # Start fully opaque
        
    def update(self):
        # Fade out effect
        now = pygame.time.get_ticks()
        elapsed = now - self.spawn_time
        
        if elapsed > self.lifetime:
            self.kill()
        else:
            # Calculate alpha based on time remaining
            self.alpha = int(255 * (1 - elapsed / self.lifetime))
            self.image.set_alpha(self.alpha)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        self.image.fill(ENEMY_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.rect.center = self.pos
        self.hp = 50
        self.last_shot = 0
        self.weapon = 'pistol' # Enemies use pistol for now

    def update(self):
        # AI behavior: prioritize upgrades, then chase player
        target_pos = None
        
        # Check for nearby upgrades (within 300 pixels)
        closest_upgrade = None
        closest_distance = 300  # Detection range
        
        for upgrade in self.game.upgrade_items:
            dist = (vec(upgrade.rect.centerx, upgrade.rect.centery) - self.pos).length()
            if dist < closest_distance:
                closest_distance = dist
                closest_upgrade = upgrade
        
        # If upgrade found, go for it
        if closest_upgrade:
            target_pos = vec(closest_upgrade.rect.centerx, closest_upgrade.rect.centery)
        else:
            # Otherwise chase player
            target_pos = self.game.player.pos
        
        # Move towards target
        dir = target_pos - self.pos
        if dir.length() > 0:
            self.vel = dir.normalize() * ENEMY_SPEED
        else:
            self.vel = vec(0, 0)
            
        self.pos += self.vel * self.game.dt
        
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')
        
        # Shooting AI - 750ms for most weapons, machinegun uses its own rate
        now = pygame.time.get_ticks()
        if self.weapon == 'machinegun':
            fire_rate = WEAPONS['machinegun']['rate']
        else:
            fire_rate = 750  # 0.75 seconds for pistol and shotgun
        
        # Apply fire rate bonus if enemy has picked up upgrades
        if hasattr(self, 'fire_rate_bonus'):
            fire_rate = max(100, fire_rate - self.fire_rate_bonus)
        
        if now - self.last_shot > fire_rate:
            # Shoot at player
            self.game.shoot(self, (self.game.player.rect.centerx, self.game.player.rect.centery))

        if self.hp <= 0:
            self.kill()

    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - self.rect.width
                if self.vel.x < 0:
                    self.pos.x = hits[0].rect.right
                self.vel.x = 0
                self.rect.x = self.pos.x
        if dir == 'y':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.rect.height
                if self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                self.rect.y = self.pos.y

    def take_damage(self, amount):
        self.hp -= amount
        self.game.score += amount
        # Show hit marker
        HitMarker(self.game, self.rect.centerx, self.rect.centery)
        if self.hp <= 0:
            self.game.score += 50 # Bonus for kill
            # Spawn kill animation
            anim_type = self.game.selected_kill_animation
            if anim_type != 'none':
                KillAnimation(self.game, self.rect.centerx, self.rect.centery, anim_type)
            # Play kill sound
            if self.game.sounds_enabled:
                try:
                    self.game.winsound.Beep(400, 100)  # 400 Hz, 100ms - kill sound  
                except:
                    pass
            self.kill()

class WeaponItem(pygame.sprite.Sprite):
    def __init__(self, game, x, y, weapon_type=None):
        self.groups = game.all_sprites, game.items
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # Use provided weapon type or choose random
        self.type = weapon_type if weapon_type else random.choice(list(WEAPONS.keys()))
        self.image = pygame.Surface((WEAPON_SIZE, WEAPON_SIZE))
        self.image.fill(WEAPONS[self.type]['color'])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class UpgradeItem(pygame.sprite.Sprite):
    """Upgrade items that AI enemies can pick up"""
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.upgrade_items
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        # Random upgrade type - changed damage to enemy_count
        self.upgrade_type = random.choice(['fire_rate', 'enemy_count', 'health'])
        
        # Visual representation based on type
        self.image = pygame.Surface((30, 30))
        colors = {
            'fire_rate': (255, 200, 0),  # Yellow
            'enemy_count': (200, 50, 255),  # Purple
            'health': (50, 255, 50)       # Green
        }
        self.image.fill(colors[self.upgrade_type])
        
        # Draw a star or special marker
        pygame.draw.circle(self.image, WHITE, (15, 15), 12, 2)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 15000  # Disappear after 15 seconds if not picked up
    
    def update(self):
        # Remove if too old
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()

class KillAnimation(pygame.sprite.Sprite):
    """Death animation sprite for killed enemies"""
    def __init__(self, game, x, y, anim_type):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.anim_type = anim_type
        
        # Get animation data
        anim_data = game.kill_animations[anim_type]
        self.lifetime = anim_data['duration']
        
        # Create visual based on type
        size = 50
        self.image = pygame.Surface((size, size))
        self.image.set_colorkey((0, 0, 0))  # Make black transparent
        
        if anim_type == 'bloodsplat':
            # Red splat
            self.image.fill((0, 0, 0))
            pygame.draw.circle(self.image, (180, 0, 0), (size//2, size//2), size//2)
            # Add some irregular spots
            pygame.draw.circle(self.image, (150, 0, 0), (size//3, size//3), size//4)
            pygame.draw.circle(self.image, (200, 20, 20), (size*2//3, size*2//3), size//5)
            
        elif anim_type == 'flowers':
            # Colorful flowers
            self.image.fill((0, 0, 0))
            # Draw several flowers
            colors = [(255, 100, 200), (255, 255, 100), (100, 200, 255), (200, 100, 255)]
            positions = [(15, 15), (35, 15), (15, 35), (35, 35), (25, 25)]
            for pos, color in zip(positions, colors):
                pygame.draw.circle(self.image, color, pos, 8)
                pygame.draw.circle(self.image, (255, 255, 0), pos, 3)  # Yellow center
            
        elif anim_type == 'gravestone':
            # Gray gravestone
            self.image.fill((0, 0, 0))
            # Draw tombstone shape
            pygame.draw.rect(self.image, (100, 100, 100), (12, 15, 26, 30))
            pygame.draw.ellipse(self.image, (100, 100, 100), (12, 10, 26, 20))
            # Add "RIP" text
            font = pygame.font.SysFont("Arial", 10, bold=True)
            rip_text = font.render("RIP", True, (50, 50, 50))
            self.image.blit(rip_text, (17, 25))
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.spawn_time = pygame.time.get_ticks()
        self.alpha = 255
        
    def update(self):
        # Fade out effect over lifetime
        now = pygame.time.get_ticks()
        elapsed = now - self.spawn_time
        
        if elapsed > self.lifetime:
            self.kill()
        else:
            # Calculate alpha based on time remaining (fade out in last 30%)
            fade_start = self.lifetime * 0.7
            if elapsed > fade_start:
                fade_progress = (elapsed - fade_start) / (self.lifetime - fade_start)
                self.alpha = int(255 * (1 - fade_progress))
                self.image.set_alpha(self.alpha)


class NetworkPlayer(pygame.sprite.Sprite):
    """Remote player in multiplayer game"""
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill((255, 100, 100))  # Red color for opponent
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.pos = vec(x, y)
        self.weapon = 'pistol'
        self.hit_count = 0
        
    def update_from_network(self, data):
        """Update position and state from network data"""
        self.pos.x = data.get('x', self.pos.x)
        self.pos.y = data.get('y', self.pos.y)
        self.weapon = data.get('weapon', self.weapon)
        self.hit_count = data.get('hits', self.hit_count)
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
    
    def update(self):
        """No local update needed - controlled by network"""
        pass
