import pygame
import random
from settings import *
vec = pygame.math.Vector2

class UpgradeItem(pygame.sprite.Sprite):
    """Upgrade items that AI enemies can pick up"""
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.upgrade_items
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        # Random upgrade type
        self.upgrade_type = random.choice(['fire_rate', 'damage', 'health'])
        
        # Visual representation based on type
        self.image = pygame.Surface((30, 30))
        colors = {
            'fire_rate': (255, 200, 0),  # Yellow
            'damage': (255, 50, 50),      # Red
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
