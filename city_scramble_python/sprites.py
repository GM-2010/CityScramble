import pygame
import random
import math
from settings import *
vec = pygame.math.Vector2

class CameraGroup(pygame.sprite.Group):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.display_surface = pygame.display.get_surface()
        self.offset = vec()
        self.half_w = self.display_surface.get_size()[0] // 2
        self.half_h = self.display_surface.get_size()[1] // 2
        
        # Create a map surface (optional, but good for performance if static)
        self.ground_surf = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
        
        # Load texture based on selected design
        design_id = game.selected_design
        design_info = game.designs.get(design_id, game.designs['classic'])
        img_file = design_info['img']
        fallback_color = design_info['color']
        
        if img_file:
            try:
                import os
                script_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(script_dir, img_file)
                ground_img = pygame.image.load(file_path).convert()
                # Tile the texture
                for x in range(0, MAP_WIDTH, ground_img.get_width()):
                    for y in range(0, MAP_HEIGHT, ground_img.get_height()):
                        self.ground_surf.blit(ground_img, (x, y))
                print(f"[OK] Design-Textur '{file_path}' erfolgreich geladen")
            except Exception as e:
                print(f"[FEHLER] Konnte {img_file} nicht laden: {e}")
                self.ground_surf.fill(fallback_color)
        else:
            self.ground_surf.fill(fallback_color)
            
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
        # Define camera view rect for culling (add margin to avoid pop-in)
        camera_view = pygame.Rect(self.offset.x - 50, self.offset.y - 50, 
                                 SCREEN_WIDTH + 100, SCREEN_HEIGHT + 100)
        
        for sprite in self.sprites():
            if camera_view.colliderect(sprite.rect):
                offset_pos = sprite.rect.topleft - self.offset
                self.display_surface.blit(sprite.image, offset_pos)
            else:
                continue # Skip drawing and health bars if off-screen
            
            # Health bars logic continues... (indented)
            # Player / NetworkPlayer (use hit_count)
            if hasattr(sprite, 'hit_count'):
                # Max hits 10. Current Health = 10 - hit_count
                max_hp = 10
                current_hp = max(0, max_hp - sprite.hit_count)
                
                bar_width = sprite.rect.width
                bar_height = 5
                bar_x = offset_pos[0]
                bar_y = offset_pos[1] - 10
                
                # Background (Red)
                pygame.draw.rect(self.display_surface, (200, 0, 0), (bar_x, bar_y, bar_width, bar_height))
                # Foreground (Green)
                if current_hp > 0:
                    health_width = int(bar_width * (current_hp / max_hp))
                    pygame.draw.rect(self.display_surface, (0, 200, 0), (bar_x, bar_y, health_width, bar_height))
            
            # Enemy (uses hp) - Only if not a wall (Obstacle has hp too but we don't want bars on walls)
            elif hasattr(sprite, 'hp') and hasattr(sprite, 'vel'): # Simple check to distinguish enemies from walls
                max_hp = 3 # Default enemy HP
                if hasattr(sprite, 'max_hp'):
                    max_hp = sprite.max_hp
                current_hp = max(0, sprite.hp)
                
                bar_width = sprite.rect.width
                bar_height = 5
                bar_x = offset_pos[0]
                bar_y = offset_pos[1] - 10
                
                # Background (Red)
                pygame.draw.rect(self.display_surface, (200, 0, 0), (bar_x, bar_y, bar_width, bar_height))
                # Foreground (Green)
                if current_hp > 0:
                    health_width = int(bar_width * (current_hp / max_hp))
                    pygame.draw.rect(self.display_surface, (0, 200, 0), (bar_x, bar_y, health_width, bar_height))

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
            # Use team shooting in team5v5 mode
            if self.game.game_mode == 'team5v5':
                self.game.shoot_team(self, world_mouse_pos, 'blue')
            else:
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
        # ONLY IN CLASSIC MODE - No regeneration in survival mode
        if self.game.game_mode == 'classic':
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
        
        # Load and scale house image
        try:
            import os
            script_dir = os.path.dirname(os.path.abspath(__file__))
            house_path = os.path.join(script_dir, "haus.jpg")
            house_img = pygame.image.load(house_path).convert()
            self.original_image = pygame.transform.scale(house_img, (w, h))
            self.image.blit(self.original_image, (0, 0))
        except Exception as e:
            print(f"[FEHLER] Konnte haus.jpg nicht laden: {e}")
            self.image.fill(SANDSTONE)
            self.original_image = self.image.copy()

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
        
        # Redraw original and apply darkening filter
        self.image.blit(self.original_image, (0, 0))
        dark_value = int(255 * damage_percent)
        # Multiply blend to darken the image
        self.image.fill((dark_value, dark_value, dark_value), special_flags=pygame.BLEND_RGB_MULT)
        
        if self.hp <= 0:
            # Schedule respawn
            self.game.schedule_obstacle_respawn(self.original_x, self.original_y, 
                                                self.original_w, self.original_h)
            
            # Network Sync: Tell other player to destroy this wall
            client = getattr(self.game, 'network_client', None)
            if client and client.connected:
                client.send({'type': 'destroy_wall', 'x': self.original_x, 'y': self.original_y})
            
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

        # Team mode collision handling
        if self.owner == 'team_blue':
            # Blue team projectiles hit red team
            hits = pygame.sprite.spritecollide(self, self.game.team_enemies, False)
            if hits:
                print(f"DEBUG: Blue projectile hit {len(hits)} red team members!")
                for hit in hits:
                    print(f"DEBUG: Dealing {self.damage} damage to red TeamAI with {hit.hp} HP")
                    hit.take_damage(self.damage)
                    # Award points to blue team
                    if hasattr(self.game, 'team_blue_score'):
                        self.game.team_blue_score += self.damage
                    self.kill()
                    break  # Only hit one target per projectile
        elif self.owner == 'team_red':
            # Red team projectiles hit blue team
            hits = pygame.sprite.spritecollide(self, self.game.team_allies, False)
            for hit in hits:
                if hasattr(hit, 'hit_count'):
                    hit.hit_count += 1
                    if hasattr(hit, 'last_action_time'):
                        hit.last_action_time = pygame.time.get_ticks()
                    if hasattr(hit, 'last_regen_time'):
                        hit.last_regen_time = pygame.time.get_ticks()
                else:
                    hit.take_damage(self.damage)
                # Award points to red team
                if hasattr(self.game, 'team_red_score'):
                    self.game.team_red_score += self.damage
                self.kill()
        # Normal mode collision handling
        elif self.owner == 'player':
            # Player projectiles hit enemies
            hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
            # FALLBACK: Also check team enemies in 5v5 mode
            if not hits and hasattr(self.game, 'game_mode') and self.game.game_mode == 'team5v5':
                 hits = pygame.sprite.spritecollide(self, self.game.team_enemies, False)

            if hits:
                for hit in hits:
                    hit.take_damage(self.damage)
                    self.kill()
                    return

            # Player projectiles hit civilians (trigger uprising)
            civilian_hits = pygame.sprite.spritecollide(self, self.game.civilians, False)
            if civilian_hits:
                for civ in civilian_hits:
                    civ.take_damage(self.damage, self.game.player)
                    self.kill()
                    return

            # Player projectiles hit uprising civilians
            uprising_hits = pygame.sprite.spritecollide(self, self.game.uprising_civilians, False)
            if uprising_hits:
                for up_civ in uprising_hits:
                    up_civ.take_damage(self.damage)
                    self.kill()
                    return

        elif self.owner == 'enemy':
            # Enemy projectiles hit player
            if pygame.sprite.collide_rect(self, self.game.player):
                # Increase hit counter
                self.game.player.hit_count += 1
                # Reset regeneration timer when hit
                self.game.player.last_action_time = pygame.time.get_ticks()
                self.game.player.last_regen_time = pygame.time.get_ticks()
                self.kill()
                return

            # Enemy projectiles can also hit civilians (trigger uprising against enemies)
            civilian_hits = pygame.sprite.spritecollide(self, self.game.civilians, False)
            if civilian_hits:
                for civ in civilian_hits:
                    # Find which enemy shot this
                    # We need to track the shooter in the projectile
                    # For now, we'll use the first enemy as fallback
                    shooter = getattr(self, 'shooter', None)
                    if shooter is None and len(self.game.enemies) > 0:
                        shooter = list(self.game.enemies)[0]
                    if shooter:
                        civ.take_damage(self.damage, shooter)
                    self.kill()
                    return

        elif self.owner == 'uprising_civilian':
            # Uprising civilian projectiles target their attacker (player OR enemy)
            # First check if it hits player
            if pygame.sprite.collide_rect(self, self.game.player):
                self.game.player.hit_count += 1
                self.game.player.last_action_time = pygame.time.get_ticks()
                self.game.player.last_regen_time = pygame.time.get_ticks()
                print(f"[DEBUG] Uprising civilian projectile hit player! Damage: 1, Total hits: {self.game.player.hit_count}")
                self.kill()
                return

            # Also check if it hits enemies (when uprising is against an enemy)
            enemy_hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
            if enemy_hits:
                for enemy in enemy_hits:
                    # Deal 10 damage per hit (5 hits to kill = 50 HP)
                    damage = 10
                    enemy.hp -= damage  # Direct HP reduction, bypass score system
                    print(f"[DEBUG] Uprising civilian projectile hit enemy! Damage: {damage}, Enemy HP: {enemy.hp}/{enemy.max_hp}")
                    # Show hit marker
                    HitMarker(self.game, enemy.rect.centerx, enemy.rect.centery)

                    # Check if enemy died
                    if enemy.hp <= 0:
                        print(f"[UPRISING] Enemy killed by uprising civilians!")
                        # Don't give player score for civilian kills
                        enemy.kill()

                    self.kill()
                    return

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
                return
            # Also check civilians
            civ_hits = pygame.sprite.spritecollide(self, self.game.civilians, False)
            if civ_hits:
                self.explode()
                self.kill()
                return
            # Also check uprising civilians
            up_civ_hits = pygame.sprite.spritecollide(self, self.game.uprising_civilians, False)
            if up_civ_hits:
                self.explode()
                self.kill()
                return
        elif self.owner == 'team_blue':
            # Player is part of team_blue
            hits = pygame.sprite.spritecollide(self, self.game.team_enemies, False)
            if hits:
                self.explode()
                self.kill()
        elif self.owner == 'team_red':
            hits = pygame.sprite.spritecollide(self, self.game.team_allies, False)
            if hits:
                self.explode()
                self.kill()
        elif self.owner == 'enemy':
            if pygame.sprite.collide_rect(self, self.game.player):
                # Increase hit counter
                self.game.player.hit_count += 1
                self.explode()
                self.kill()
        elif self.owner == 'uprising_civilian':
            # Check collision with player
            if pygame.sprite.collide_rect(self, self.game.player):
                self.game.player.hit_count += 1
                self.explode()
                self.kill()
                return
            # Check collision with enemies (when uprising is against an enemy)
            enemy_hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
            if enemy_hits:
                self.explode()
                self.kill()
    
    def explode(self):
        # Deal area damage to all enemies within explosion radius
        if self.owner == 'team_blue':
            # Blue team grenade hits red team
            for enemy in self.game.team_enemies:
                dist = vec(enemy.rect.centerx - self.rect.centerx,
                          enemy.rect.centery - self.rect.centery).length()
                if dist <= self.explosion_radius:
                    enemy.take_damage(self.damage)
                    if hasattr(self.game, 'team_blue_score'):
                        self.game.team_blue_score += self.damage
        elif self.owner == 'team_red':
            # Red team grenade hits blue team
            for ally in self.game.team_allies:
                dist = vec(ally.rect.centerx - self.rect.centerx,
                          ally.rect.centery - self.rect.centery).length()
                if dist <= self.explosion_radius:
                    if hasattr(ally, 'hit_count'):
                        ally.hit_count += 1
                    else:
                        ally.take_damage(self.damage)
                    if hasattr(self.game, 'team_red_score'):
                        self.game.team_red_score += self.damage
        elif self.owner == 'player':
            # Damage enemies
            for enemy in self.game.enemies:
                dist = vec(enemy.rect.centerx - self.rect.centerx,
                          enemy.rect.centery - self.rect.centery).length()
                if dist <= self.explosion_radius:
                    enemy.take_damage(self.damage)

            # Damage civilians (trigger uprising for each hit)
            for civilian in self.game.civilians:
                dist = vec(civilian.rect.centerx - self.rect.centerx,
                          civilian.rect.centery - self.rect.centery).length()
                if dist <= self.explosion_radius:
                    civilian.take_damage(self.damage, self.game.player)

            # Damage uprising civilians
            for up_civ in self.game.uprising_civilians:
                dist = vec(up_civ.rect.centerx - self.rect.centerx,
                          up_civ.rect.centery - self.rect.centery).length()
                if dist <= self.explosion_radius:
                    up_civ.take_damage(self.damage)

        elif self.owner == 'enemy':
            # Enemy grenades damage the player only
            dist = vec(self.game.player.rect.centerx - self.rect.centerx,
                      self.game.player.rect.centery - self.rect.centery).length()
            if dist <= self.explosion_radius:
                # Calculate damage based on distance (full damage at center, less at edge)
                damage_multiplier = 1.0 - (dist / self.explosion_radius)
                damage = max(1, int(self.damage * damage_multiplier))
                self.game.player.hit_count += damage
                # Reset regeneration timer when hit
                self.game.player.last_action_time = pygame.time.get_ticks()
                self.game.player.last_regen_time = pygame.time.get_ticks()

        elif self.owner == 'uprising_civilian':
            # Uprising civilian grenades damage their target (player or enemies)
            # Damage player
            dist_to_player = vec(self.game.player.rect.centerx - self.rect.centerx,
                                self.game.player.rect.centery - self.rect.centery).length()
            if dist_to_player <= self.explosion_radius:
                damage_multiplier = 1.0 - (dist_to_player / self.explosion_radius)
                damage = max(1, int(self.damage * damage_multiplier))
                self.game.player.hit_count += damage
                self.game.player.last_action_time = pygame.time.get_ticks()
                self.game.player.last_regen_time = pygame.time.get_ticks()

            # Damage enemies (when uprising is against an enemy)
            for enemy in self.game.enemies:
                dist = vec(enemy.rect.centerx - self.rect.centerx,
                          enemy.rect.centery - self.rect.centery).length()
                if dist <= self.explosion_radius:
                    # Fixed 10 damage per grenade hit (5 hits to kill)
                    damage = 10
                    enemy.hp -= damage  # Direct HP reduction
                    print(f"[DEBUG] Uprising civilian grenade hit enemy! Damage: {damage}, Enemy HP: {enemy.hp}/{enemy.max_hp}")
                    # Show hit marker
                    HitMarker(self.game, enemy.rect.centerx, enemy.rect.centery)

                    # Check if enemy died
                    if enemy.hp <= 0:
                        print(f"[UPRISING] Enemy killed by uprising civilian grenade!")
                        enemy.kill()


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
        # Set initial color based on weapon (pistol)
        self.weapon = 'pistol'
        self.update_color()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.rect.center = self.pos
        self.max_hp = 50
        self.hp = self.max_hp
        self.last_shot = 0
        self.player_last_pos = None  # Track player position for velocity calculation
        self.player_last_time = 0

        # Stuck detection
        self.last_move_time = pygame.time.get_ticks()
        self.last_pos_check = vec(x, y)
        self.stuck_check_timer = 0
        self.last_stuck_pos = None
        self.last_stuck_time = 0
        self.reroute_dir = None
        self.reroute_end_time = 0
        self.dodge_direction = None
        self.dodge_start_time = 0
        self.dodge_duration = 500 # 0.5 seconds dodge duration
        self.dodge_speed_multiplier = 3.0 # Speed multiplier during dodge

        # Flanking Logic (Start of match dispersal)
        self.flanking_mode = True
        self.flanking_start_time = pygame.time.get_ticks()
        self.flanking_duration = random.randint(3000, 6000)
        
        # Calculate random flanking target around player
        angle = random.uniform(0, 360)
        distance = random.uniform(500, 900)
        offset = vec(distance, 0).rotate(angle)
        
        # We need player pos, but player might not be fully initialized or self.game.player might be reference.
        # Assuming self.game.player.pos is valid.
        if hasattr(self.game, 'player') and hasattr(self.game.player, 'pos'):
             target = self.game.player.pos + offset
        else:
             target = self.pos + offset # Fallback
             
        # Clamp to map bounds
        target.x = max(50, min(MAP_WIDTH - 50, target.x))
        target.y = max(50, min(MAP_HEIGHT - 50, target.y))
        self.flanking_target = target
        self.stuck_check_timer = 0
        self.reroute_end_time = 0
        self.reroute_dir = vec(0, 0)

        # Dodge state tracking
        self.dodge_start_time = 0
        self.dodge_direction = None
        self.dodge_duration = 400  # milliseconds to dodge (increased for bigger movements)
        self.dodge_speed_multiplier = 3.0  # Default dodge speed multiplier
        
        # New stuck prevention tracking
        self.last_stuck_pos = None
        self.last_stuck_time = 0
        
        # Pathfinding attributes
        self.path = []  # List of waypoint positions [(x,y), ...]
        self.path_target_pos = None  # Target position for current path
        self.path_recalc_timer = 0  # Timer to limit path recalculations
        self.current_waypoint_index = 0  # Index of current waypoint in path

    def update_color(self):
        """Update enemy color to match current weapon color"""
        weapon_color = WEAPONS[self.weapon]['color']
        self.image.fill(weapon_color)

    def has_line_of_sight(self, target_pos):
        """Check if there's a clear line of sight to target position (no walls blocking)"""
        # Simple raycast - check points along the line between enemy and target
        start = vec(self.rect.centerx, self.rect.centery)
        end = vec(target_pos[0], target_pos[1])
        
        direction = end - start
        distance = direction.length()
        
        if distance == 0:
            return True
        
        direction = direction.normalize()
        
        # Check points every 20 pixels along the line
        steps = int(distance / 20) + 1
        for i in range(1, steps):
            check_pos = start + direction * (i * 20)
            check_rect = pygame.Rect(check_pos.x - 5, check_pos.y - 5, 10, 10)
            
            # Check if this point intersects any wall
            for wall in self.game.walls:
                if wall.rect.colliderect(check_rect):
                    return False
        
        return True
    
    def calculate_predicted_target(self):
        """Calculate where to aim based on player movement and projectile speed"""
        player = self.game.player
        
        # Get difficulty setting
        difficulty = self.game.ai_aim_difficulty
        
        # Easy mode: No prediction, just aim at current position with high inaccuracy
        if difficulty == 'easy':
            # High inaccuracy for easy mode
            max_inaccuracy = 100
            offset_x = random.uniform(-max_inaccuracy, max_inaccuracy)
            offset_y = random.uniform(-max_inaccuracy, max_inaccuracy)
            
            predicted_pos = player.pos.copy()
            predicted_pos.x += offset_x
            predicted_pos.y += offset_y
            
            # Clamp to map bounds
            predicted_pos.x = max(0, min(MAP_WIDTH, predicted_pos.x))
            predicted_pos.y = max(0, min(MAP_HEIGHT, predicted_pos.y))
            
            return (predicted_pos.x, predicted_pos.y)
        
        # Normal and Hard modes: Use predictive aiming
        # Calculate player velocity
        now = pygame.time.get_ticks()
        player_vel = vec(0, 0)
        
        if self.player_last_pos is not None and (now - self.player_last_time) > 0:
            time_delta = (now - self.player_last_time) / 1000.0  # Convert to seconds
            player_vel = (player.pos - self.player_last_pos) / time_delta
        
        # Update tracking
        self.player_last_pos = player.pos.copy()
        self.player_last_time = now
        
        # Get projectile speed
        weapon_stats = WEAPONS[self.weapon]
        projectile_speed = weapon_stats['speed']
        
        # Calculate distance to player
        to_player = player.pos - self.pos
        distance = to_player.length()
        
        if distance == 0 or projectile_speed == 0:
            return (player.rect.centerx, player.rect.centery)
        
        # Calculate time for projectile to reach player
        travel_time = distance / projectile_speed
        
        # Predict player position
        predicted_pos = player.pos + player_vel * travel_time
        
        # Add distance-based accuracy variation
        # Difficulty affects max inaccuracy
        max_distance = 1000
        if difficulty == 'hardcore':
            # Hardcore mode: Perfect accuracy (0 pixel inaccuracy)
            max_inaccuracy = 0
        elif difficulty == 'hard':
            # Hard mode: More accurate (±25 pixels max)
            max_inaccuracy = min(25, (distance / max_distance) * 25)
        else:  # normal
            # Normal mode: Standard accuracy (±50 pixels max)
            max_inaccuracy = min(50, (distance / max_distance) * 50)
        
        offset_x = random.uniform(-max_inaccuracy, max_inaccuracy)
        offset_y = random.uniform(-max_inaccuracy, max_inaccuracy)
        
        predicted_pos.x += offset_x
        predicted_pos.y += offset_y
        
        # Clamp to map bounds
        predicted_pos.x = max(0, min(MAP_WIDTH, predicted_pos.x))
        predicted_pos.y = max(0, min(MAP_HEIGHT, predicted_pos.y))
        
        return (predicted_pos.x, predicted_pos.y)
    
    def detect_incoming_projectiles(self):
        """Detect player projectiles that might hit this enemy with threat assessment"""
        dangerous_projectiles = []
        detection_range = 400  # Increased for even earlier detection

        for projectile in self.game.projectiles:
            # Skip if projectile doesn't have owner (e.g., BuildingProjectile)
            if not hasattr(projectile, 'owner'):
                continue

            # Only care about player projectiles
            if projectile.owner != 'player':
                continue

            # Check if projectile has velocity
            if not hasattr(projectile, 'vel') or projectile.vel.length() == 0:
                continue

            # Calculate vector from projectile to enemy
            to_enemy = self.pos - vec(projectile.rect.centerx, projectile.rect.centery)
            distance = to_enemy.length()

            if distance > detection_range or distance == 0:
                continue

            # Get projectile velocity and direction
            projectile_speed = projectile.vel.length()
            projectile_dir = projectile.vel.normalize()
            to_enemy_dir = to_enemy.normalize()

            # Calculate how aligned the projectile is with the enemy
            dot_product = projectile_dir.dot(to_enemy_dir)

            # Only consider if moving towards us (dot > 0.3 for wider detection)
            if dot_product > 0.3:
                # Calculate closest approach distance (perpendicular distance)
                # Project enemy position onto projectile path
                proj_to_enemy = to_enemy
                projection_length = proj_to_enemy.dot(projectile_dir)

                if projection_length > 0:  # Projectile is heading in our general direction
                    closest_point = vec(projectile.rect.centerx, projectile.rect.centery) + projectile_dir * projection_length
                    closest_distance = (self.pos - closest_point).length()

                    # If projectile will pass close enough to be dangerous
                    threat_radius = ENEMY_SIZE * 1.5  # Consider threats within 1.5x enemy size
                    if closest_distance < threat_radius:
                        # Calculate time until impact
                        time_to_impact = projection_length / projectile_speed if projectile_speed > 0 else float('inf')

                        # Threat score: lower is more dangerous (closer distance + sooner impact)
                        threat_score = distance * 0.5 + time_to_impact * 100

                        dangerous_projectiles.append({
                            'projectile': projectile,
                            'distance': distance,
                            'time_to_impact': time_to_impact,
                            'threat_score': threat_score,
                            'closest_distance': closest_distance,
                            'dot_product': dot_product
                        })

        # Sort by threat score (most dangerous first)
        if dangerous_projectiles:
            dangerous_projectiles.sort(key=lambda x: x['threat_score'])
            return dangerous_projectiles

        return []
    
    def calculate_dodge_direction(self, incoming_projectiles):
        """Calculate a safe direction to dodge away from multiple projectiles"""
        if not incoming_projectiles:
            return None

        # Get primary threat (most dangerous projectile)
        primary_threat = incoming_projectiles[0]
        primary_projectile = primary_threat['projectile']

        if not hasattr(primary_projectile, 'vel') or primary_projectile.vel.length() == 0:
            return None

        projectile_dir = primary_projectile.vel.normalize()

        # Generate multiple escape directions to test
        escape_directions = []

        # 1. Perpendicular directions (left and right)
        perpendicular_left = vec(-projectile_dir.y, projectile_dir.x)
        perpendicular_right = vec(projectile_dir.y, -projectile_dir.x)
        escape_directions.append(perpendicular_left)
        escape_directions.append(perpendicular_right)

        # 2. Diagonal escape directions (45 degrees)
        diagonal1 = (perpendicular_left + (-projectile_dir)).normalize()
        diagonal2 = (perpendicular_right + (-projectile_dir)).normalize()
        escape_directions.append(diagonal1)
        escape_directions.append(diagonal2)

        # 3. Backward direction
        escape_directions.append(-projectile_dir)

        # Evaluate each escape direction
        best_direction = None
        best_score = -float('inf')

        # Adaptive dodge distance based on threat urgency
        if primary_threat['time_to_impact'] < 0.3:  # Very urgent (< 0.3 seconds)
            dodge_distance = 80  # Larger dodge
        elif primary_threat['time_to_impact'] < 0.6:  # Urgent (< 0.6 seconds)
            dodge_distance = 60
        else:  # Less urgent
            dodge_distance = 50

        for direction in escape_directions:
            test_pos = self.pos + direction * dodge_distance

            # Check if position is safe from walls and bounds
            if not self.is_position_safe_from_walls(test_pos):
                continue

            # Calculate safety score for this direction
            safety_score = self.evaluate_dodge_position(test_pos, incoming_projectiles)

            # Bonus for perpendicular movement (natural dodge direction)
            if direction in [perpendicular_left, perpendicular_right]:
                safety_score += 20

            # Consider player position - prefer not to dodge towards player if they're close
            to_player = self.game.player.pos - test_pos
            player_distance = to_player.length()
            if player_distance < 150:  # Player is close
                safety_score -= 30  # Penalty for dodging towards player

            if safety_score > best_score:
                best_score = safety_score
                best_direction = direction

        # If we found a good direction, return it
        if best_direction and best_score > -50:  # Threshold for acceptable safety
            return best_direction

        # Emergency: no good direction found, try any perpendicular
        return random.choice([perpendicular_left, perpendicular_right])

    def is_position_safe_from_walls(self, pos):
        """Check if a position is safe from walls and bounds"""
        # Bounds check with margin
        margin = ENEMY_SIZE
        if pos.x < margin or pos.x > MAP_WIDTH - margin:
            return False
        if pos.y < margin or pos.y > MAP_HEIGHT - margin:
            return False

        # Wall check
        test_rect = pygame.Rect(pos.x - ENEMY_SIZE/2, pos.y - ENEMY_SIZE/2, ENEMY_SIZE, ENEMY_SIZE)
        for wall in self.game.walls:
            if wall.rect.colliderect(test_rect):
                return False

        return True

    def evaluate_dodge_position(self, pos, incoming_projectiles):
        """Evaluate how safe a position is from all incoming projectiles. Higher score = safer"""
        safety_score = 100  # Start with base safety

        for threat in incoming_projectiles:
            projectile = threat['projectile']

            if not hasattr(projectile, 'vel') or not hasattr(projectile, 'rect'):
                continue

            # Calculate distance from this position to the projectile
            proj_pos = vec(projectile.rect.centerx, projectile.rect.centery)
            distance_to_proj = (pos - proj_pos).length()

            # Calculate if projectile path will intersect this position
            projectile_dir = projectile.vel.normalize() if projectile.vel.length() > 0 else vec(0, 0)
            to_pos = pos - proj_pos

            # Project position onto projectile path
            if projectile_dir.length() > 0:
                projection = to_pos.dot(projectile_dir)

                if projection > 0:  # Position is ahead of projectile
                    # Calculate perpendicular distance to projectile path
                    closest_point_on_path = proj_pos + projectile_dir * projection
                    perpendicular_distance = (pos - closest_point_on_path).length()

                    # Danger zone is within ENEMY_SIZE * 2
                    danger_threshold = ENEMY_SIZE * 2
                    if perpendicular_distance < danger_threshold:
                        # This position is in the projectile's path
                        danger_factor = 1.0 - (perpendicular_distance / danger_threshold)
                        safety_score -= 80 * danger_factor  # Heavy penalty

            # Penalty for being close to any projectile
            if distance_to_proj < 100:
                proximity_penalty = (100 - distance_to_proj) / 100 * 40
                safety_score -= proximity_penalty

        return safety_score
    
    def update(self):
        now = pygame.time.get_ticks()
        
        # LOGIC LOD: Check distance to player
        # If far away, skip expensive logic (pathfinding, dodging, collision precise checks)
        dist_sq_to_player = (self.pos - self.game.player.pos).length_squared()
        
        # 2000^2 = 4,000,000. If > 2000px away, do minimal update
        if dist_sq_to_player > 4000000:
            # Just move towards player simply, no pathfinding, no dodging
            # Update direction only every 2 seconds to save sqrt calls
            if now % 2000 < 50: 
                dir = (self.game.player.pos - self.pos)
                if dir.length_squared() > 0:
                    self.vel = dir.normalize() * ENEMY_SPEED
            
            # Simple movement
            self.pos += self.vel * self.game.dt
            self.rect.center = self.pos
            # Boundary checks only (fast)
            if self.pos.x < 0: self.pos.x = 0
            if self.pos.x > MAP_WIDTH - ENEMY_SIZE: self.pos.x = MAP_WIDTH - ENEMY_SIZE
            if self.pos.y < 0: self.pos.y = 0
            if self.pos.y > MAP_HEIGHT - ENEMY_SIZE: self.pos.y = MAP_HEIGHT - ENEMY_SIZE
            return # SKIP REST OF UPDATE
            
        # Check if currently in a dodge maneuver

        # Check if currently in a dodge maneuver
        dodge_velocity = None
        currently_dodging = False

        if self.dodge_direction and (now - self.dodge_start_time) < self.dodge_duration:
            # Continue current dodge with stored speed multiplier
            currently_dodging = True
            speed_multiplier = getattr(self, 'dodge_speed_multiplier', 3.0)
            dodge_velocity = self.dodge_direction.normalize() * (ENEMY_SPEED * speed_multiplier)
        else:
            # Dodge finished, reset
            self.dodge_direction = None
            self.dodge_speed_multiplier = 3.0

            # Check for new projectile dodging (uses separate dodge difficulty setting)
            dodge_difficulty = self.game.ai_dodge_difficulty

            # Only dodge if difficulty allows it
            if dodge_difficulty != 'easy':
                incoming_projectiles = self.detect_incoming_projectiles()

                if incoming_projectiles:
                    # Dodge chance based on dodge difficulty (not aim difficulty)
                    if dodge_difficulty == 'hardcore':
                        dodge_chance = 1.0  # Always dodge (100% chance)
                    elif dodge_difficulty == 'hard':
                        dodge_chance = 0.8  # 80% chance
                    else:
                        dodge_chance = 0.5  # 50% chance (normal)

                    if random.random() < dodge_chance:
                        dodge_dir = self.calculate_dodge_direction(incoming_projectiles)

                        if dodge_dir:
                            # Calculate adaptive dodge speed based on most dangerous threat
                            primary_threat = incoming_projectiles[0]
                            time_to_impact = primary_threat['time_to_impact']

                            # Adaptive speed multiplier based on urgency
                            if time_to_impact < 0.2:  # Extremely urgent
                                self.dodge_speed_multiplier = 4.5  # Very fast dodge
                            elif time_to_impact < 0.4:  # Very urgent
                                self.dodge_speed_multiplier = 3.5
                            elif time_to_impact < 0.7:  # Urgent
                                self.dodge_speed_multiplier = 3.0
                            else:  # Less urgent
                                self.dodge_speed_multiplier = 2.5

                            # Start new dodge
                            self.dodge_direction = dodge_dir
                            self.dodge_start_time = now
                            currently_dodging = True
                            dodge_velocity = dodge_dir.normalize() * (ENEMY_SPEED * self.dodge_speed_multiplier)
        
        
        
        # Stuck detection checks
        if now > self.reroute_end_time:
            # Check every 500ms if we moved enough
            if now - self.stuck_check_timer > 500:
                self.stuck_check_timer = now
                if (self.pos - self.last_pos_check).length() > 20:
                    self.last_move_time = now
                    self.last_pos_check = vec(self.pos.x, self.pos.y)
                elif now - self.last_move_time > 2000:
                    # Stuck for 2 seconds! 
                    # Try to destroy the wall blocking us (10 bullets)
                    # Enemy targets player
                    target_pos = self.game.player.pos
                    to_target = target_pos - self.pos
                    if to_target.length() > 0:
                        shoot_dir = to_target.normalize()
                        for _ in range(10):
                            spread = random.uniform(-15, 15)
                            vel = shoot_dir.rotate(spread)
                            # BuildingProjectile: damage=1, speed=10, lifetime=1000
                            BuildingProjectile(self.game, self.rect.centerx, self.rect.centery, vel.x, vel.y, 1, 10, 1000, (255, 165, 0))
                    
                    # Reset stuck timer so we don't spam instantly, but NO reroute movement
                    self.last_move_time = now
                    self.last_pos_check = vec(self.pos.x, self.pos.y)
                    # Record stuck position for repulsion logic
                    self.last_stuck_pos = vec(self.pos.x, self.pos.y)
                    self.last_stuck_time = now
        
        # AI behavior: Phases (Flanking -> Tactics -> Combat)
        target_pos = None
        
        # Override movement if rerouting
        if now < self.reroute_end_time:
            self.vel = self.reroute_dir * ENEMY_SPEED
        else:
            # PHASE 1: FLANKING (Start of match)
            if self.flanking_mode:
                if now - self.flanking_start_time > self.flanking_duration:
                    self.flanking_mode = False
                else:
                    target_pos = self.flanking_target
            
            # PHASE 2: TACTICS & COMBAT
            if not target_pos: # Only if not flanking or rerouting
                
                # Check for nearby upgrades (priority over combat)
                closest_upgrade = None
                closest_distance = 300  # Detection range
                
                for upgrade in self.game.upgrade_items:
                    dist = (vec(upgrade.rect.centerx, upgrade.rect.centery) - self.pos).length()
                    if dist < closest_distance:
                        closest_distance = dist
                        closest_upgrade = upgrade
                
                if closest_upgrade:
                    # Priority 1: Pick up upgrade
                    target_pos = vec(closest_upgrade.rect.centerx, closest_upgrade.rect.centery)
                else:
                    # Priority 2: Regrouping Logic (Teamwork)
                    # Check if isolated (no teammates within 100px)
                    # Use spatial hash for efficiency
                    nearby_objects = self.game.spatial_hash.get_nearby(self.rect.inflate(200, 200))
                    ally_count = 0
                    for obj in nearby_objects:
                        if isinstance(obj, Enemy) and obj != self:
                            dist = (self.pos - obj.pos).length()
                            if dist < 150: # Check 150px radius for allies
                                ally_count += 1
                                
                    if ally_count == 0:
                        # ISOLATED! Find nearest ally to regroup
                        nearest_ally = None
                        min_ally_dist = 99999
                        
                        # Find nearest ally (iterating all enemies - usually < 50, so cheap)
                        # Skip this frame if too many enemies to save CPU? No, 50 is fine.
                        for ally in self.game.enemies:
                            if ally != self:
                                d = (self.pos - ally.pos).length_squared()
                                if d < min_ally_dist:
                                    min_ally_dist = d
                                    nearest_ally = ally
                                    
                        if nearest_ally:
                            # Move towards ally
                            target_pos = nearest_ally.pos
                            # Optional: Don't shoot while regrouping to focus on movement? 
                            # self.last_shot = now # Suppress fire? Maybe not, keep shooting.
                    
                    if not target_pos:
                        # Priority 3: Attack Player
                        target_pos = self.game.player.pos
        
        # Move towards target (or dodge if necessary)
        if dodge_velocity:
            # Dodging takes priorityover normal movement
            self.vel = dodge_velocity
        else:
            # Pathfinding-based movement
            # Update path if needed (target changed significantly or path recalc timeout)
            should_recalc = False
            
            if self.path_target_pos is None or target_pos is None:
                should_recalc = True
            elif (target_pos - self.path_target_pos).length() > 100:  # Target moved >100px
               should_recalc = True
            elif now - self.path_recalc_timer > 1000:  # Recalc every 1 second
                should_recalc = True
            
            if should_recalc and target_pos and hasattr(self.game, 'pathfinding_grid'):
                from pathfinding import find_path
                self.path = find_path((self.pos.x, self.pos.y), (target_pos.x, target_pos.y), 
                                     self.game.pathfinding_grid)
                self.path_target_pos = target_pos.copy() if hasattr(target_pos, 'copy') else vec(target_pos[0], target_pos[1])
                self.path_recalc_timer = now
                self.current_waypoint_index = 0
            
            # Follow path if it exists
            if self.path and len(self.path) > 0:
                # Get current waypoint
                if self.current_waypoint_index < len(self.path):
                    waypoint = self.path[self.current_waypoint_index]
                    waypoint_vec = vec(waypoint[0], waypoint[1])
                    
                    # Check if reached current waypoint
                    dist_to_waypoint = (self.pos - waypoint_vec).length()
                    if dist_to_waypoint < 30:  # Reached waypoint (within 30px)
                        self.current_waypoint_index += 1
                        if self.current_waypoint_index >= len(self.path):
                            # Reached end of path, clear it
                            self.path = []
                            self.current_waypoint_index = 0
                    
                    # Move towards current waypoint
                    if self.current_waypoint_index < len(self.path):
                        waypoint = self.path[self.current_waypoint_index]
                        waypoint_vec = vec(waypoint[0], waypoint[1])
                        dir = waypoint_vec - self.pos
                    else:
                        # No more waypoints, move directly to target
                        dir = target_pos - self.pos if target_pos else vec(0, 0)
                else:
                    # Path completed
                    dir = target_pos - self.pos if target_pos else vec(0, 0)
            else:
                # No path, move directly (fallback)
                dir = target_pos - self.pos if target_pos else vec(0, 0)
            
            # Avoid last stuck position if recent (within 5 seconds)
            if self.last_stuck_pos and (now - self.last_stuck_time) < 5000:
                 dist_to_stuck = (self.pos - self.last_stuck_pos).length()
                 if dist_to_stuck < 200:
                      # Add repulsion vector away from stuck position
                      repulsion = self.pos - self.last_stuck_pos
                      if repulsion.length() > 0:
                          repulsion = repulsion.normalize()
                          # Blend normal direction with repulsion
                          if dir.length() > 0:
                              dir = (dir.normalize() + repulsion * 2.0).normalize() # Strong repulsion
                          else:
                              dir = repulsion

            if dir.length() > 0:
                self.vel = dir.normalize() * ENEMY_SPEED
            else:
                self.vel = vec(0, 0)
            
        self.pos += self.vel * self.game.dt
        
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')
        
        # Boundary checks
        if self.pos.x < 0: self.pos.x = 0
        if self.pos.x > MAP_WIDTH - ENEMY_SIZE: self.pos.x = MAP_WIDTH - ENEMY_SIZE
        if self.pos.y < 0: self.pos.y = 0
        if self.pos.y > MAP_HEIGHT - ENEMY_SIZE: self.pos.y = MAP_HEIGHT - ENEMY_SIZE
        
        # Sync rect with pos after boundary checks
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        
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
            # Calculate predicted target position
            predicted_target = self.calculate_predicted_target()
            
            # Only shoot if we have line of sight
            if self.has_line_of_sight(predicted_target):
                self.game.shoot(self, predicted_target)

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

        # Trigger dodge reaction when hit (if dodge difficulty allows)
        dodge_difficulty = self.game.ai_dodge_difficulty
        if dodge_difficulty != 'easy' and self.hp > 0:
            # Set dodge chance based on difficulty
            if dodge_difficulty == 'hardcore':
                dodge_chance = 1.0  # Always dodge when hit
            elif dodge_difficulty == 'hard':
                dodge_chance = 0.9  # 90% chance to dodge when hit
            else:  # normal
                dodge_chance = 0.7  # 70% chance to dodge when hit

            # Activate dodge if chance succeeds and not already dodging
            if random.random() < dodge_chance:
                now = pygame.time.get_ticks()
                # Only start new dodge if not currently dodging
                if not self.dodge_direction or (now - self.dodge_start_time) >= self.dodge_duration:
                    # Find nearby projectiles to dodge away from
                    incoming_projectiles = self.detect_incoming_projectiles()

                    if incoming_projectiles:
                        # Dodge away from detected projectiles with adaptive speed
                        dodge_dir = self.calculate_dodge_direction(incoming_projectiles)

                        # Set adaptive speed based on threat
                        primary_threat = incoming_projectiles[0]
                        time_to_impact = primary_threat['time_to_impact']

                        if time_to_impact < 0.2:
                            self.dodge_speed_multiplier = 5.0  # Emergency dodge - very fast!
                        elif time_to_impact < 0.4:
                            self.dodge_speed_multiplier = 4.0
                        else:
                            self.dodge_speed_multiplier = 3.5
                    else:
                        # No projectiles detected, dodge in a random direction
                        # Use fast speed since we just got hit
                        random_angle = random.uniform(0, 2 * math.pi)
                        dodge_dir = vec(math.cos(random_angle), math.sin(random_angle))
                        self.dodge_speed_multiplier = 4.0  # Fast reactive dodge

                    if dodge_dir:
                        self.dodge_direction = dodge_dir
                        self.dodge_start_time = now

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


class TeamAI(pygame.sprite.Sprite):
    """AI teammate for 5v5 team mode"""
    def __init__(self, game, x, y, team='blue', member_index=0):
        self.groups = game.all_sprites, game.team_allies if team == 'blue' else game.team_enemies
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.team = team
        self.member_index = member_index
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        # Blue for allies, red for enemies
        self.image.fill((50, 50, 255) if team == 'blue' else (255, 50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.rect.topleft = (x, y)
        self.max_hp = 100  # Higher HP for team mode
        self.hp = self.max_hp
        self.last_shot = 0
        self.weapon = 'pistol'
        self.player_last_pos = None
        self.player_last_time = 0

        # Stuck detection
        self.last_move_time = pygame.time.get_ticks()
        self.last_pos_check = vec(x, y)
        self.stuck_check_timer = 0
        self.reroute_end_time = 0
        self.reroute_dir = vec(0, 0)

        self.reroute_end_time = 0
        self.reroute_dir = vec(0, 0)
        self.last_stuck_pos = None
        self.last_stuck_time = 0

        # Dodge state tracking (same as Enemy)
        self.dodge_start_time = 0
        self.dodge_direction = None
        self.dodge_duration = 400
        self.dodge_speed_multiplier = 3.0
        
        # Pathfinding attributes
        self.path = []  # List of waypoint positions [(x,y), ...]
        self.path_target_pos = None  # Target position for current path
        self.path_recalc_timer = 0  # Timer to limit path recalculations
        self.current_waypoint_index = 0  # Index of current waypoint in path

    def has_line_of_sight(self, target_pos):
        """Check if there's a clear line of sight to target position"""
        start = vec(self.rect.centerx, self.rect.centery)
        end = vec(target_pos[0], target_pos[1])

        direction = end - start
        distance = direction.length()

        if distance == 0:
            return True

        direction = direction.normalize()

        steps = int(distance / 20) + 1
        for i in range(1, steps):
            check_pos = start + direction * (i * 20)
            check_rect = pygame.Rect(check_pos.x - 5, check_pos.y - 5, 10, 10)

            for wall in self.game.walls:
                if wall.rect.colliderect(check_rect):
                    return False

        return True

    def find_closest_enemy(self):
        """Find the closest enemy from the opposing team"""
        closest_enemy = None
        closest_distance = float('inf')

        # Get the opposing team group
        enemy_group = self.game.team_enemies if self.team == 'blue' else self.game.team_allies

        for enemy in enemy_group:
            dist = (vec(enemy.rect.centerx, enemy.rect.centery) - self.pos).length()
            if dist < closest_distance:
                closest_distance = dist
                closest_enemy = enemy

        return closest_enemy

    def calculate_predicted_target(self, target):
        """Calculate where to aim based on target movement"""
        now = pygame.time.get_ticks()
        target_vel = vec(0, 0)

        if self.player_last_pos is not None and (now - self.player_last_time) > 0:
            time_delta = (now - self.player_last_time) / 1000.0
            target_vel = (target.pos - self.player_last_pos) / time_delta

        self.player_last_pos = target.pos.copy()
        self.player_last_time = now

        weapon_stats = WEAPONS[self.weapon]
        projectile_speed = weapon_stats['speed']

        to_target = target.pos - self.pos
        distance = to_target.length()

        if distance == 0 or projectile_speed == 0:
            return (target.rect.centerx, target.rect.centery)

        travel_time = distance / projectile_speed
        predicted_pos = target.pos + target_vel * travel_time

        # Add some inaccuracy based on difficulty
        difficulty = self.game.ai_aim_difficulty
        max_distance = 1000
        if difficulty == 'hardcore':
            max_inaccuracy = 0
        elif difficulty == 'hard':
            max_inaccuracy = min(25, (distance / max_distance) * 25)
        else:
            max_inaccuracy = min(50, (distance / max_distance) * 50)

        offset_x = random.uniform(-max_inaccuracy, max_inaccuracy)
        offset_y = random.uniform(-max_inaccuracy, max_inaccuracy)

        predicted_pos.x += offset_x
        predicted_pos.y += offset_y

        predicted_pos.x = max(0, min(MAP_WIDTH, predicted_pos.x))
        predicted_pos.y = max(0, min(MAP_HEIGHT, predicted_pos.y))

        return (predicted_pos.x, predicted_pos.y)

    def update(self):
        now = pygame.time.get_ticks()

        # Stuck detection checks
        if now > self.reroute_end_time:
            # Check every 500ms if we moved enough
            if now - self.stuck_check_timer > 500:
                self.stuck_check_timer = now
                if (self.pos - self.last_pos_check).length() > 20:
                    self.last_move_time = now
                    self.last_pos_check = vec(self.pos.x, self.pos.y)
                elif now - self.last_move_time > 2000:
                    # Stuck for 2 seconds! 
                    # Try to destroy the wall blocking us (10 bullets)
                    # TeamAI targets closest enemy
                    target = self.find_closest_enemy()
                    if target:
                        target_pos = target.pos
                        to_target = target_pos - self.pos
                        if to_target.length() > 0:
                            shoot_dir = to_target.normalize()
                            for _ in range(10):
                                spread = random.uniform(-15, 15)
                                vel = shoot_dir.rotate(spread)
                                # BuildingProjectile: damage=1, speed=10, lifetime=1000
                                BuildingProjectile(self.game, self.rect.centerx, self.rect.centery, vel.x, vel.y, 1, 10, 1000, (255, 165, 0))
                    
                    # Reset stuck timer so we don't spam instantly
                    self.last_move_time = now
                    self.last_pos_check = vec(self.pos.x, self.pos.y)
                    # Record stuck position for repulsion logic
                    self.last_stuck_pos = vec(self.pos.x, self.pos.y)
                    self.last_stuck_time = now

        # Find closest enemy to attack
        target = self.find_closest_enemy()

        if target:
            # Move towards target with tactical positioning
            target_pos = target.pos
            
            # TACTICAL: Calculate encirclement offset based on member_index
            # Each unit (0-4) takes a different angle around the target
            angle = self.member_index * (360 / 5)
            offset_dist = 250 # Distance to maintain from target
            tactical_offset = vec(offset_dist, 0).rotate(angle)
            tactical_target = target_pos + tactical_offset
            
            # Direction towards the tactical spot
            # Use pathfinding to navigate to tactical target
            should_recalc = False
            
            if self.path_target_pos is None:
                should_recalc = True
            elif (tactical_target - self.path_target_pos).length() > 100:  # Target moved >100px
                should_recalc = True
            elif now - self.path_recalc_timer > 1000:  # Recalc every 1 second
                should_recalc = True
            
            if should_recalc and hasattr(self.game, 'pathfinding_grid'):
                from pathfinding import find_path
                self.path = find_path((self.pos.x, self.pos.y), (tactical_target.x, tactical_target.y),
                                     self.game.pathfinding_grid)
                self.path_target_pos = tactical_target.copy()
                self.path_recalc_timer = now
                self.current_waypoint_index = 0
            
            # Follow path if it exists
            if self.path and len(self.path) > 0:
                if self.current_waypoint_index < len(self.path):
                    waypoint = self.path[self.current_waypoint_index]
                    waypoint_vec = vec(waypoint[0], waypoint[1])
                    
                    # Check if reached waypoint
                    dist_to_waypoint = (self.pos - waypoint_vec).length()
                    if dist_to_waypoint < 30:
                        self.current_waypoint_index += 1
                        if self.current_waypoint_index >= len(self.path):
                            self.path = []
                            self.current_waypoint_index = 0
                    
                    # Move to waypoint
                    if self.current_waypoint_index < len(self.path):
                        waypoint = self.path[self.current_waypoint_index]
                        waypoint_vec = vec(waypoint[0], waypoint[1])
                        dir = waypoint_vec - self.pos
                    else:
                        dir = tactical_target - self.pos
                else:
                    dir = tactical_target - self.pos
            else:
                # Fallback to direct movement
                dir = tactical_target - self.pos
            
            # SPACING: Avoid crowding other teammates
            teammates = self.game.team_allies if self.team == 'blue' else self.game.team_enemies
            spacing_force = vec(0, 0)
            for teammate in teammates:
                if teammate != self:
                    dist_to_teammate = (self.pos - teammate.pos).length()
                    if 0 < dist_to_teammate < 80: # Too close
                        # Push away from teammate
                        spacing_force += (self.pos - teammate.pos).normalize() * (80 - dist_to_teammate)
            
            # Combine direct interest with spacing
            if spacing_force.length() > 0:
                dir = (dir.normalize() + spacing_force.normalize() * 0.5).normalize()

            # Avoid last stuck position if recent (within 5 seconds)
            if self.last_stuck_pos and (now - self.last_stuck_time) < 5000:
                 dist_to_stuck = (self.pos - self.last_stuck_pos).length()
                 if dist_to_stuck < 200:
                      # Add repulsion vector away from stuck position
                      repulsion = self.pos - self.last_stuck_pos
                      if repulsion.length() > 0:
                          repulsion = repulsion.normalize()
                          # Blend normal direction with repulsion
                          if dir.length() > 0:
                              dir = (dir.normalize() + repulsion * 2.0).normalize()
                          else:
                              dir = repulsion

            if dir.length() > 0:
                self.vel = dir.normalize() * ENEMY_SPEED
            else:
                self.vel = vec(0, 0)

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

            # Shooting AI
            fire_rate = WEAPONS[self.weapon]['rate']
            if now - self.last_shot > fire_rate:
                predicted_target = self.calculate_predicted_target(target)

                if self.has_line_of_sight(predicted_target):
                    self.game.shoot_team(self, predicted_target, self.team)

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
        print(f"DEBUG: {self.team} TeamAI.take_damage called! Amount: {amount}, HP before: {self.hp}")
        self.hp -= amount
        print(f"DEBUG: {self.team} TeamAI HP after: {self.hp}")
        if self.hp <= 0:
            print(f"DEBUG: {self.team} TeamAI died! Scheduling respawn...")
            # Schedule respawn instead of permanent death
            spawn_x = MAP_WIDTH - 200 if self.team == 'blue' else 100
            spawn_y = MAP_HEIGHT - 200 if self.team == 'blue' else 100
            self.game.schedule_team_respawn(self.team, spawn_x, spawn_y)
            self.kill()


class Civilian(pygame.sprite.Sprite):
    """Peaceful civilian that wanders around. Triggers uprising if hit."""
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.civilians
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        # Visual: White with white dot
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill((255, 255, 255))  # White
        # Draw white dot in center
        pygame.draw.circle(self.image, (255, 255, 255), (PLAYER_SIZE // 2, PLAYER_SIZE // 2), 5)
        # Draw gray border to make it visible against white background
        pygame.draw.rect(self.image, (200, 200, 200), self.image.get_rect(), 2)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.pos = vec(x, y)
        self.vel = vec(0, 0)

        # Health same as enemies
        self.max_hp = 50
        self.hp = self.max_hp

        # Random wandering behavior
        self.wander_timer = pygame.time.get_ticks()
        self.wander_direction = vec(random.uniform(-1, 1), random.uniform(-1, 1))
        if self.wander_direction.length() > 0:
            self.wander_direction = self.wander_direction.normalize()
        self.wander_speed = ENEMY_SPEED * 0.3  # Slower than enemies

    def update(self):
        now = pygame.time.get_ticks()

        # Change direction every 3-5 seconds
        if now - self.wander_timer > random.randint(3000, 5000):
            self.wander_timer = now
            self.wander_direction = vec(random.uniform(-1, 1), random.uniform(-1, 1))
            if self.wander_direction.length() > 0:
                self.wander_direction = self.wander_direction.normalize()

        # Move in wander direction
        self.vel = self.wander_direction * self.wander_speed
        self.pos += self.vel * self.game.dt

        # Collision with walls
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')

        # Boundary checks
        if self.pos.x < 0:
            self.pos.x = 0
            self.wander_direction.x *= -1  # Bounce off edge
        if self.pos.x > MAP_WIDTH - PLAYER_SIZE:
            self.pos.x = MAP_WIDTH - PLAYER_SIZE
            self.wander_direction.x *= -1
        if self.pos.y < 0:
            self.pos.y = 0
            self.wander_direction.y *= -1
        if self.pos.y > MAP_HEIGHT - PLAYER_SIZE:
            self.pos.y = MAP_HEIGHT - PLAYER_SIZE
            self.wander_direction.y *= -1

        # Sync rect with pos
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - self.rect.width
                if self.vel.x < 0:
                    self.pos.x = hits[0].rect.right
                self.vel.x = 0
                self.wander_direction.x *= -1  # Bounce off wall
                self.rect.x = self.pos.x
        if dir == 'y':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.rect.height
                if self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                self.wander_direction.y *= -1  # Bounce off wall
                self.rect.y = self.pos.y

    def take_damage(self, amount, attacker):
        """Take damage and trigger uprising"""
        self.hp -= amount

        if self.hp <= 0:
            # Show hit marker
            HitMarker(self.game, self.rect.centerx, self.rect.centery)

            # TRIGGER UPRISING: Spawn 20 aggressive civilians
            print(f"[UPRISING] Civilian killed by {attacker}! Spawning 20 aggressive civilians!")
            self.game.trigger_uprising(attacker, self.pos)

            self.kill()


class UprisingCivilian(pygame.sprite.Sprite):
    """Aggressive civilian spawned during uprising. Attacks the perpetrator."""
    def __init__(self, game, x, y, target):
        self.groups = game.all_sprites, game.uprising_civilians
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.target = target  # Who to attack (player or enemy)

        # Visual: White with red dot (angry civilian)
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill((255, 255, 255))  # White
        # Draw red dot in center (angry)
        pygame.draw.circle(self.image, (255, 0, 0), (PLAYER_SIZE // 2, PLAYER_SIZE // 2), 5)
        # Draw red border
        pygame.draw.rect(self.image, (255, 0, 0), self.image.get_rect(), 2)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.pos = vec(x, y)
        self.vel = vec(0, 0)

        # Health - stronger than regular enemies for revenge!
        self.max_hp = 100  # Double health to be more threatening
        self.hp = self.max_hp

        # Combat attributes
        self.last_shot = 0
        # Give them a shotgun for more damage output
        self.weapon = random.choice(['shotgun', 'machinegun', 'pistol'])  # Mix of weapons
        self.player_last_pos = None
        self.player_last_time = 0

        # Pathfinding
        self.path = []
        self.path_target_pos = None
        self.path_recalc_timer = 0
        self.current_waypoint_index = 0

    def has_line_of_sight(self, target_pos):
        """Check if there's a clear line of sight to target"""
        start = vec(self.rect.centerx, self.rect.centery)
        end = vec(target_pos[0], target_pos[1])

        direction = end - start
        distance = direction.length()

        if distance == 0:
            return True

        direction = direction.normalize()

        steps = int(distance / 20) + 1
        for i in range(1, steps):
            check_pos = start + direction * (i * 20)
            check_rect = pygame.Rect(check_pos.x - 5, check_pos.y - 5, 10, 10)

            for wall in self.game.walls:
                if wall.rect.colliderect(check_rect):
                    return False

        return True

    def update(self):
        # Check if target still exists
        if self.target not in self.game.all_sprites:
            # Target is dead - find a new enemy target if uprising was against an enemy
            from sprites import Enemy
            if isinstance(self.target, Enemy) or not isinstance(self.target, Player):
                # Find nearest enemy as new target
                nearest_enemy = None
                nearest_dist = float('inf')
                for enemy in self.game.enemies:
                    dist = (enemy.pos - self.pos).length()
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest_enemy = enemy

                if nearest_enemy:
                    self.target = nearest_enemy
                    print(f"[UPRISING] Civilian switched to new enemy target!")
                else:
                    # No more enemies, mission accomplished
                    self.kill()
                    return
            else:
                # Target was player and died - despawn
                self.kill()
                return

        now = pygame.time.get_ticks()
        target_pos = self.target.pos

        # Pathfinding-based movement towards target
        should_recalc = False

        if self.path_target_pos is None:
            should_recalc = True
        elif (target_pos - self.path_target_pos).length() > 100:
            should_recalc = True
        elif now - self.path_recalc_timer > 1000:
            should_recalc = True

        if should_recalc and hasattr(self.game, 'pathfinding_grid'):
            from pathfinding import find_path
            self.path = find_path((self.pos.x, self.pos.y), (target_pos.x, target_pos.y),
                                 self.game.pathfinding_grid)
            self.path_target_pos = target_pos.copy()
            self.path_recalc_timer = now
            self.current_waypoint_index = 0

        # Follow path
        if self.path and len(self.path) > 0:
            if self.current_waypoint_index < len(self.path):
                waypoint = self.path[self.current_waypoint_index]
                waypoint_vec = vec(waypoint[0], waypoint[1])

                dist_to_waypoint = (self.pos - waypoint_vec).length()
                if dist_to_waypoint < 30:
                    self.current_waypoint_index += 1
                    if self.current_waypoint_index >= len(self.path):
                        self.path = []
                        self.current_waypoint_index = 0

                if self.current_waypoint_index < len(self.path):
                    waypoint = self.path[self.current_waypoint_index]
                    waypoint_vec = vec(waypoint[0], waypoint[1])
                    dir = waypoint_vec - self.pos
                else:
                    dir = target_pos - self.pos
            else:
                dir = target_pos - self.pos
        else:
            dir = target_pos - self.pos

        if dir.length() > 0:
            self.vel = dir.normalize() * ENEMY_SPEED
        else:
            self.vel = vec(0, 0)

        self.pos += self.vel * self.game.dt

        # Collision
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')

        # Boundary checks
        if self.pos.x < 0: self.pos.x = 0
        if self.pos.x > MAP_WIDTH - PLAYER_SIZE: self.pos.x = MAP_WIDTH - PLAYER_SIZE
        if self.pos.y < 0: self.pos.y = 0
        if self.pos.y > MAP_HEIGHT - PLAYER_SIZE: self.pos.y = MAP_HEIGHT - PLAYER_SIZE

        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

        # Shooting AI - more aggressive
        fire_rate = WEAPONS[self.weapon]['rate']
        # Shoot faster than normal enemies
        fire_rate = max(300, fire_rate - 200)  # Much faster shooting

        if now - self.last_shot > fire_rate:
            # Simple aim at target
            predicted_target = (target_pos.x, target_pos.y)

            if self.has_line_of_sight(predicted_target):
                self.game.shoot(self, predicted_target)
                print(f"[DEBUG] UprisingCivilian shooting at target! Weapon: {self.weapon}")

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
        """Take damage from projectiles"""
        self.hp -= amount

        if self.hp <= 0:
            # Show hit marker
            HitMarker(self.game, self.rect.centerx, self.rect.centery)
            # Give score
            if hasattr(self.game, 'score'):
                self.game.score += 50
            self.kill()
