import pygame
import sys
import random
import subprocess
import threading
import time
from network import ensure_server, GameClient, get_local_ip
from settings import *
from sprites import *

class MenuManager:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.clock = game.clock
        
        # Fonts
        self.font = game.font
        self.medium_font = game.medium_font
        self.large_font = game.large_font
        self.small_font = game.small_font

    def draw_text(self, text, x, y, color=WHITE, align="topleft"):
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "topleft":
            text_rect.topleft = (x, y)
        elif align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def show_start_screen(self):
        if self.game.menu_music_loaded and self.game.menu_music:
            self.game.menu_music.play(-1)
            
        # Button setup
        button_width = 300
        button_height = 50
        button_spacing = 20
        
        buttons_x = SCREEN_WIDTH // 2 - button_width // 2
        buttons_start_y = 170  # Adjusted to fit 6 buttons + start button on 720p screen

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
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 30))
            
            # Total Score Display
            total_score_text = self.large_font.render(f"Gesamtpunkte: {self.game.total_score:,}", True, (255, 215, 0))
            total_score_rect = total_score_text.get_rect(center=(SCREEN_WIDTH // 2, 110))
            # Background box for total score
            box_rect = pygame.Rect(total_score_rect.x - 20, total_score_rect.y - 10, 
                                   total_score_rect.width + 40, total_score_rect.height + 20)
            pygame.draw.rect(self.screen, (50, 50, 50), box_rect)
            pygame.draw.rect(self.screen, (255, 215, 0), box_rect, 3)
            self.screen.blit(total_score_text, total_score_rect)
            
            # Game Mode button
            mode_names = {'classic': 'Klassisch', 'survival': 'Überlebens-Modus', 'team5v5': '5vs5 Team'}
            mode_colors = {'classic': (100, 200, 100), 'survival': (255, 100, 50), 'team5v5': (100, 100, 255)}
            current_mode_name = mode_names[self.game.game_mode]
            current_mode_color = mode_colors[self.game.game_mode]

            pygame.draw.rect(self.screen, current_mode_color, game_mode_button)
            pygame.draw.rect(self.screen, WHITE, game_mode_button, 3)
            mode_text = self.medium_font.render(f"Modus: {current_mode_name}", True, WHITE)
            mode_text_rect = mode_text.get_rect(center=game_mode_button.center)
            self.screen.blit(mode_text, mode_text_rect)

            # Enemy count button
            pygame.draw.rect(self.screen, LIGHT_GREY, enemy_button)
            pygame.draw.rect(self.screen, WHITE, enemy_button, 3)
            enemy_text = self.medium_font.render(f"Gegner: {self.game.max_enemies}", True, WHITE)
            enemy_text_rect = enemy_text.get_rect(center=enemy_button.center)
            self.screen.blit(enemy_text, enemy_text_rect)
            
            # AI Aiming difficulty button
            difficulty_names = {'easy': 'Einfach', 'normal': 'Normal', 'hard': 'Schwer', 'hardcore': 'HARDCORE'}
            difficulty_colors = {'easy': (50, 200, 50), 'normal': (255, 200, 50), 'hard': (255, 50, 50), 'hardcore': (200, 0, 200)}
            current_difficulty_name = difficulty_names[self.game.ai_aim_difficulty]
            current_difficulty_color = difficulty_colors[self.game.ai_aim_difficulty]
            
            pygame.draw.rect(self.screen, current_difficulty_color, ai_aim_button)
            pygame.draw.rect(self.screen, WHITE, ai_aim_button, 3)
            ai_aim_text = self.medium_font.render(f"KI-Aiming: {current_difficulty_name}", True, WHITE)
            ai_aim_text_rect = ai_aim_text.get_rect(center=ai_aim_button.center)
            self.screen.blit(ai_aim_text, ai_aim_text_rect)
            
            # AI Dodge difficulty button
            dodge_difficulty_name = difficulty_names[self.game.ai_dodge_difficulty]
            dodge_difficulty_color = difficulty_colors[self.game.ai_dodge_difficulty]
            
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
                        if self.game.game_mode == 'classic':
                            self.game.game_mode = 'survival'
                        elif self.game.game_mode == 'survival':
                            self.game.game_mode = 'team5v5'
                        else:
                            self.game.game_mode = 'classic'
                        self.game.save_total_score()  # Save the setting
                    elif enemy_button.collidepoint(event.pos):
                        # Ask for enemy count
                        new_count = self.get_text_input("ANZAHL GEGNER:", str(self.game.max_enemies), max_length=5)
                        if new_count and new_count.isdigit():
                            count = int(new_count)
                            if count > 0:
                                self.game.max_enemies = count
                    elif ai_aim_button.collidepoint(event.pos):
                        # Cycle through difficulties: easy -> normal -> hard -> hardcore -> easy
                        if self.game.ai_aim_difficulty == 'easy':
                            self.game.ai_aim_difficulty = 'normal'
                        elif self.game.ai_aim_difficulty == 'normal':
                            self.game.ai_aim_difficulty = 'hard'
                        elif self.game.ai_aim_difficulty == 'hard':
                            self.game.ai_aim_difficulty = 'hardcore'
                        else:
                            self.game.ai_aim_difficulty = 'easy'
                        self.game.save_total_score()  # Save the setting
                    elif ai_dodge_button.collidepoint(event.pos):
                        # Cycle through difficulties: easy -> normal -> hard -> hardcore -> easy
                        if self.game.ai_dodge_difficulty == 'easy':
                            self.game.ai_dodge_difficulty = 'normal'
                        elif self.game.ai_dodge_difficulty == 'normal':
                            self.game.ai_dodge_difficulty = 'hard'
                        elif self.game.ai_dodge_difficulty == 'hard':
                            self.game.ai_dodge_difficulty = 'hardcore'
                        else:
                            self.game.ai_dodge_difficulty = 'easy'
                        self.game.save_total_score()  # Save the setting
                    elif tutorial_button.collidepoint(event.pos):
                        # Show tutorial
                        self.show_tutorial()
                    elif shop_button.collidepoint(event.pos):
                        self.show_unified_shop()
                    elif multiplayer_button.collidepoint(event.pos):
                        self.show_multiplayer_menu()
                    elif start_button.collidepoint(event.pos):
                        return

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
            score_text = self.font.render(f"Verfügbare Punkte: {self.game.total_score:,}", True, (255, 215, 0))
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
            score_text = self.font.render(f"Verfügbare Punkte: {self.game.total_score:,}", True, (255, 215, 0))
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
            current_cost = math.ceil(self.game.base_upgrade_cost * (1.01 ** self.game.total_upgrades_purchased))
            
            # Title
            title_text = self.large_font.render("WAFFEN-SHOP", True, (255, 215, 0))
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - 150, 50))
            
            # Current score
            self.draw_text(f"Verfügbare Punkte: {self.game.total_score:,}", SCREEN_WIDTH // 2 - 100, 120)
            self.draw_text(f"Upgrade-Kosten: {current_cost}", SCREEN_WIDTH // 2 - 80, 150)
            self.draw_text(f"Gekaufte Upgrades: {self.game.total_upgrades_purchased}", SCREEN_WIDTH // 2 - 90, 175)
            
            # Random upgrade offer
            self.draw_text("Zufälliges Upgrade-Angebot:", SCREEN_WIDTH // 2 - 100, 210)
            weapon_text = self.font.render(f"Waffe: {selected_weapon.upper()}", True, WEAPONS[selected_weapon]['color'])
            self.screen.blit(weapon_text, (SCREEN_WIDTH // 2 - 80, 250))
            self.draw_text(f"Upgrade: {upgrade_names[selected_upgrade]}", SCREEN_WIDTH // 2 - 80, 290)
            self.draw_text(upgrade_descriptions[selected_upgrade], SCREEN_WIDTH // 2 - 100, 330)
            
            # Current upgrade level
            current_level = self.game.weapon_upgrades[selected_weapon][selected_upgrade]
            self.draw_text(f"Aktuelle Stufe: {current_level}", SCREEN_WIDTH // 2 - 80, 370)
            
            # Buy button
            can_afford = self.game.total_score >= current_cost
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
                        self.game.total_score -= current_cost
                        self.game.weapon_upgrades[selected_weapon][selected_upgrade] += 1
                        self.game.total_upgrades_purchased += 1  # Increment purchase counter
                        self.game.save_total_score()
                        message = f"Upgrade gekauft! Neue Stufe: {self.game.weapon_upgrades[selected_weapon][selected_upgrade]}"
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
        available_colors = {k: v for k, v in self.game.character_colors.items() 
                           if k not in self.game.owned_colors and k != 'white'}
        
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
            self.draw_text(f"Verfügbare Punkte: {self.game.total_score:,}", SCREEN_WIDTH // 2 - 100, 100)
            self.draw_text(f"Farbenpreis: 15.000 (Spezial teurer)", SCREEN_WIDTH // 2 - 120, 130)
            
            # Draw color buttons
            for color_id, button_rect in color_buttons.items():
                color_data = self.game.character_colors[color_id]
                can_afford = self.game.total_score >= color_data['cost']
                
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
                            color_data = self.game.character_colors[color_id]
                            if self.game.total_score >= color_data['cost']:
                                # Purchase color
                                self.game.total_score -= color_data['cost']
                                self.game.owned_colors.append(color_id)
                                self.game.save_total_score()
                                message = f"{color_data['name']} gekauft!"
                                message_color = (100, 255, 100)
                                # Remove from available colors
                                del color_buttons[color_id]
                                
                                # Rebuild buttons
                                color_buttons.clear()
                                row = 0
                                col = 0
                                available_colors = {k: v for k, v in self.game.character_colors.items() 
                                                   if k not in self.game.owned_colors and k != 'white'}
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
        for color_id in self.game.owned_colors:
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
            current_color_name = self.game.character_colors[self.game.selected_color]['name']
            self.draw_text(f"Aktuelle Farbe: {current_color_name}", SCREEN_WIDTH // 2 - 100, 100)
            self.draw_text(f"Punkte: {self.game.total_score:,}", SCREEN_WIDTH // 2 - 60, 130)
            
            # Draw color buttons
            for color_id, button_rect in color_buttons.items():
                color_data = self.game.character_colors[color_id]
                
                # Button background
                pygame.draw.rect(self.screen, color_data['rgb'], button_rect)
                
                # Highlight selected color
                border_width = 5 if color_id == self.game.selected_color else 2
                border_color = (255, 215, 0) if color_id == self.game.selected_color else WHITE
                pygame.draw.rect(self.screen, border_color, button_rect, border_width)
                
                # Text
                text_color = BLACK if sum(color_data['rgb']) > 400 else WHITE
                name_surface = self.font.render(color_data['name'], True, text_color)
                # Center text
                text_rect = name_surface.get_rect(center=button_rect.center)
                self.screen.blit(name_surface, text_rect)
            
            # Draw sell buttons
            for color_id, sell_button_rect in sell_buttons.items():
                color_data = self.game.character_colors[color_id]
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
                            color_data = self.game.character_colors[color_id]
                            sell_price = color_data['cost'] // 2
                            
                            # Sell the color
                            self.game.total_score += sell_price
                            self.game.owned_colors.remove(color_id)
                            
                            # If selling the currently selected color, switch to white
                            if self.game.selected_color == color_id:
                                self.game.selected_color = 'white'
                            
                            self.game.save_total_score()
                            message = f"{color_data['name']} verkauft für {sell_price:,} Punkte!"
                            message_color = (255, 215, 0)
                            
                            # Rebuild buttons
                            color_buttons.clear()
                            sell_buttons.clear()
                            row = 0
                            col = 0
                            
                            for new_color_id in self.game.owned_colors:
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
                            self.game.selected_color = color_id
                            self.game.save_total_score()
                            color_name = self.game.character_colors[color_id]['name']
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
        available_colors = {k: v for k, v in self.game.bullet_colors.items() 
                           if k not in self.game.owned_bullet_colors and k != 'white'}
        
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
            self.draw_text(f"Verfügbare Punkte: {self.game.total_score:,}", SCREEN_WIDTH // 2 - 100, 100)
            self.draw_text(f"Farbenpreise wie im Charakter-Shop", SCREEN_WIDTH // 2 - 140, 130)
            
            # Draw color buttons
            for color_id, button_rect in color_buttons.items():
                color_data = self.game.bullet_colors[color_id]
                can_afford = self.game.total_score >= color_data['cost']
                
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
                            color_data = self.game.bullet_colors[color_id]
                            if self.game.total_score >= color_data['cost']:
                                # Purchase color
                                self.game.total_score -= color_data['cost']
                                self.game.owned_bullet_colors.append(color_id)
                                self.game.save_total_score()
                                message = f"{color_data['name']} gekauft!"
                                message_color = (100, 255, 100)
                                # Remove from available colors
                                del color_buttons[color_id]
                                
                                # Rebuild buttons
                                color_buttons.clear()
                                row = 0
                                col = 0
                                available_colors = {k: v for k, v in self.game.bullet_colors.items() 
                                                   if k not in self.game.owned_bullet_colors and k != 'white'}
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
        for color_id in self.game.owned_bullet_colors:
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
            current_color_name = self.game.bullet_colors[self.game.selected_bullet_color]['name']
            self.draw_text(f"Aktuelle Farbe: {current_color_name}", SCREEN_WIDTH // 2 - 100, 100)
            self.draw_text(f"Punkte: {self.game.total_score:,}", SCREEN_WIDTH // 2 - 60, 130)
            
            # Draw color buttons
            for color_id, button_rect in color_buttons.items():
                color_data = self.game.bullet_colors[color_id]
                
                # Button background
                pygame.draw.rect(self.screen, color_data['rgb'], button_rect)
                
                # Highlight selected color
                border_width = 5 if color_id == self.game.selected_bullet_color else 2
                border_color = (255, 215, 0) if color_id == self.game.selected_bullet_color else WHITE
                pygame.draw.rect(self.screen, border_color, button_rect, border_width)
                
                # Text
                text_color = BLACK if sum(color_data['rgb']) > 400 else WHITE
                name_surface = self.font.render(color_data['name'], True, text_color)
                # Center text
                text_rect = name_surface.get_rect(center=button_rect.center)
                self.screen.blit(name_surface, text_rect)
            
            # Draw sell buttons
            for color_id, sell_button_rect in sell_buttons.items():
                color_data = self.game.bullet_colors[color_id]
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
                            color_data = self.game.bullet_colors[color_id]
                            sell_price = color_data['cost'] // 2
                            
                            # Sell the color
                            self.game.total_score += sell_price
                            self.game.owned_bullet_colors.remove(color_id)
                            
                            # If selling the currently selected color, switch to white
                            if self.game.selected_bullet_color == color_id:
                                self.game.selected_bullet_color = 'white'
                            
                            self.game.save_total_score()
                            message = f"{color_data['name']} verkauft für {sell_price:,} Punkte!"
                            message_color = (255, 215, 0)
                            
                            # Rebuild buttons
                            color_buttons.clear()
                            sell_buttons.clear()
                            row = 0
                            col = 0
                            
                            for new_color_id in self.game.owned_bullet_colors:
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
                            self.game.selected_bullet_color = color_id
                            self.game.save_total_score()
                            color_name = self.game.bullet_colors[color_id]['name']
                            message = f"Farbe gewählt: {color_name}"
                            message_color = (100, 255, 100)
                            break

    def show_kill_animation_shop(self):
        """Shop screen for buying kill animations"""
        back_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 40)
        
        # Create a grid 
        items_per_row = 2
        button_width = 300
        button_height = 60
        button_spacing = 20
        start_x = SCREEN_WIDTH // 2 - (items_per_row * button_width + (items_per_row - 1) * button_spacing) // 2
        start_y = 180
        
        anim_buttons = {}
        row = 0
        col = 0
        
        # Create buttons for animations not yet owned
        available_anims = {k: v for k, v in self.game.kill_animations.items() 
                          if k not in self.game.owned_kill_animations and k != 'none'}
        
        for anim_id, anim_data in available_anims.items():
            x = start_x + col * (button_width + button_spacing)
            y = start_y + row * (button_height + button_spacing)
            anim_buttons[anim_id] = pygame.Rect(x, y, button_width, button_height)
            col += 1
            if col >= items_per_row:
                col = 0
                row += 1
        
        message = ""
        message_color = WHITE
        
        while True:
            self.screen.fill(DARK_GREY)
            
            # Title
            title_text = self.large_font.render("KILL-ANIMATIONEN SHOP", True, (150, 50, 150))
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - 250, 40))
            
            # Current score
            self.draw_text(f"Verfügbare Punkte: {self.game.total_score:,}", SCREEN_WIDTH // 2 - 100, 100)
            
            # Draw buttons
            for anim_id, button_rect in anim_buttons.items():
                anim_data = self.game.kill_animations[anim_id]
                can_afford = self.game.total_score >= anim_data['cost']
                
                # Button background
                button_color = (100, 200, 100) if can_afford else (60, 60, 60)
                pygame.draw.rect(self.screen, button_color, button_rect)
                pygame.draw.rect(self.screen, WHITE, button_rect, 3)
                
                # Text
                name_surface = self.font.render(anim_data['name'], True, WHITE if can_afford else (120, 120, 120))
                price_surface = self.font.render(f"{anim_data['cost']:,}", True, WHITE if can_afford else (120, 120, 120))
                
                self.screen.blit(name_surface, (button_rect.x + 10, button_rect.y + 15))
                self.screen.blit(price_surface, (button_rect.right - price_surface.get_width() - 10, button_rect.y + 15))
            
            # If no animations available
            if not anim_buttons:
                no_anims_text = self.medium_font.render("Alle Animationen gekauft!", True, (100, 255, 100))
                self.screen.blit(no_anims_text, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 - 30))
            
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
                    
                    # Check button clicks
                    for anim_id, button_rect in anim_buttons.items():
                        if button_rect.collidepoint(event.pos):
                            anim_data = self.game.kill_animations[anim_id]
                            if self.game.total_score >= anim_data['cost']:
                                # Purchase
                                self.game.total_score -= anim_data['cost']
                                self.game.owned_kill_animations.append(anim_id)
                                self.game.save_total_score()
                                message = f"{anim_data['name']} gekauft!"
                                message_color = (100, 255, 100)
                                # Remove from available
                                del anim_buttons[anim_id]
                                
                                # Rebuild buttons
                                anim_buttons.clear()
                                row = 0
                                col = 0
                                available_anims = {k: v for k, v in self.game.kill_animations.items() 
                                                  if k not in self.game.owned_kill_animations and k != 'none'}
                                for new_id, new_data in available_anims.items():
                                    x = start_x + col * (button_width + button_spacing)
                                    y = start_y + row * (button_height + button_spacing)
                                    anim_buttons[new_id] = pygame.Rect(x, y, button_width, button_height)
                                    col += 1
                                    if col >= items_per_row:
                                        col = 0
                                        row += 1
                                break
                            else:
                                message = "Nicht genug Punkte!"
                                message_color = (255, 100, 100)

    def show_kill_animation_wardrobe(self):
        """Wardrobe screen for selecting kill animations"""
        back_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 40)
        
        # Create a grid
        items_per_row = 2
        button_width = 300
        button_height = 60
        button_spacing = 20
        start_x = SCREEN_WIDTH // 2 - (items_per_row * button_width + (items_per_row - 1) * button_spacing) // 2
        start_y = 180
        
        anim_buttons = {}
        row = 0
        col = 0
        
        # Create buttons for owned animations
        for anim_id in self.game.owned_kill_animations:
            x = start_x + col * (button_width + button_spacing)
            y = start_y + row * (button_height + button_spacing)
            anim_buttons[anim_id] = pygame.Rect(x, y, button_width, button_height)
            col += 1
            if col >= items_per_row:
                col = 0
                row += 1
        
        message = ""
        message_color = WHITE
        
        while True:
            self.screen.fill(DARK_GREY)
            
            # Title
            title_text = self.large_font.render("KILL-ANIMATIONEN", True, (200, 100, 150))
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - 200, 40))
            
            # Current selection
            current_name = self.game.kill_animations[self.game.selected_kill_animation]['name']
            self.draw_text(f"Aktuell: {current_name}", SCREEN_WIDTH // 2 - 100, 100)
            
            # Draw buttons
            for anim_id, button_rect in anim_buttons.items():
                anim_data = self.game.kill_animations[anim_id]
                
                # Check if selected
                is_selected = (anim_id == self.game.selected_kill_animation)
                
                # Button background
                pygame.draw.rect(self.screen, (100, 50, 100), button_rect)
                border_color = (255, 215, 0) if is_selected else WHITE
                border_width = 4 if is_selected else 2
                pygame.draw.rect(self.screen, border_color, button_rect, border_width)
                
                # Text
                name_surface = self.font.render(anim_data['name'], True, WHITE)
                text_rect = name_surface.get_rect(center=button_rect.center)
                self.screen.blit(name_surface, text_rect)
            
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
                    
                    # Check button clicks
                    for anim_id, button_rect in anim_buttons.items():
                        if button_rect.collidepoint(event.pos):
                            self.game.selected_kill_animation = anim_id
                            self.game.save_total_score()
                            message = f"Animation gewählt: {self.game.kill_animations[anim_id]['name']}"
                            message_color = (100, 255, 100)
                            break

    def show_special_shop(self):
        """Shop for special items like Minimap"""
        back_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 40)
        buy_minimap_button = pygame.Rect(SCREEN_WIDTH // 2 - 150, 200, 300, 60)
        
        message = ""
        message_color = WHITE
        
        while True:
            self.screen.fill(DARK_GREY)
            
            # Title
            title_text = self.large_font.render("SPEZIAL-SHOP", True, (100, 100, 255))
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - 150, 50))
            
            # Current score
            self.draw_text(f"Verfügbare Punkte: {self.game.total_score:,}", SCREEN_WIDTH // 2 - 100, 120)
            
            # Minimap Button
            if not self.game.minimap_owned:
                can_afford = self.game.total_score >= self.game.special_minimap_cost
                color = (100, 200, 255) if can_afford else (100, 100, 100)
                pygame.draw.rect(self.screen, color, buy_minimap_button)
                pygame.draw.rect(self.screen, WHITE, buy_minimap_button, 3)
                
                text = self.font.render(f"Minimap kaufen ({self.game.special_minimap_cost:,})", True, WHITE)
                text_rect = text.get_rect(center=buy_minimap_button.center)
                self.screen.blit(text, text_rect)
            else:
                pygame.draw.rect(self.screen, (100, 255, 100), buy_minimap_button)
                pygame.draw.rect(self.screen, WHITE, buy_minimap_button, 3)
                text = self.font.render("Minimap im Besitz!", True, BLACK)
                text_rect = text.get_rect(center=buy_minimap_button.center)
                self.screen.blit(text, text_rect)
            
            # Description
            desc = self.medium_font.render("Zeigt Gegner auf einem Radar an", True, WHITE)
            self.screen.blit(desc, (SCREEN_WIDTH // 2 - 200, 280))
            
            # Back button
            pygame.draw.rect(self.screen, LIGHT_GREY, back_button)
            pygame.draw.rect(self.screen, WHITE, back_button, 2)
            self.draw_text("Zurück", back_button.x + 60, back_button.y + 10)
            
            # Message
            if message:
                self.draw_text(message, SCREEN_WIDTH // 2 - 150, 350, message_color)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if back_button.collidepoint(event.pos):
                        return
                    if buy_minimap_button.collidepoint(event.pos) and not self.game.minimap_owned:
                        if self.game.total_score >= self.game.special_minimap_cost:
                            self.game.total_score -= self.game.special_minimap_cost
                            self.game.minimap_owned = True
                            self.game.minimap_active = True
                            self.game.save_total_score()
                            message = "Minimap gekauft!"
                            message_color = (100, 255, 100)
                        else:
                            message = "Nicht genug Punkte!"
                            message_color = (255, 100, 100)

    def show_special_wardrobe(self):
        """Wardrobe for toggling special items"""
        back_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 40)
        toggle_minimap_button = pygame.Rect(SCREEN_WIDTH // 2 - 150, 200, 300, 60)
        
        message = ""
        message_color = WHITE
        
        while True:
            self.screen.fill(DARK_GREY)
            
            # Title
            title_text = self.large_font.render("SPEZIAL-AUSRÜSTUNG", True, (150, 100, 200))
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - 220, 50))
            
            # Minimap Toggle
            if self.game.minimap_owned:
                color = (100, 255, 100) if self.game.minimap_active else (200, 100, 100)
                status_text = "AKTIV" if self.game.minimap_active else "INAKTIV"
                
                pygame.draw.rect(self.screen, color, toggle_minimap_button)
                pygame.draw.rect(self.screen, WHITE, toggle_minimap_button, 3)
                
                text = self.font.render(f"Minimap: {status_text}", True, BLACK if self.game.minimap_active else WHITE)
                text_rect = text.get_rect(center=toggle_minimap_button.center)
                self.screen.blit(text, text_rect)
            else:
                pygame.draw.rect(self.screen, (100, 100, 100), toggle_minimap_button)
                pygame.draw.rect(self.screen, WHITE, toggle_minimap_button, 3)
                text = self.font.render("Minimap nicht im Besitz", True, (200, 200, 200))
                text_rect = text.get_rect(center=toggle_minimap_button.center)
                self.screen.blit(text, text_rect)
            
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
                    if toggle_minimap_button.collidepoint(event.pos) and self.game.minimap_owned:
                        self.game.minimap_active = not self.game.minimap_active
                        self.game.save_total_score()

    def show_go_screen(self):
        """Game Over screen"""
        # Buttons
        restart_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50)
        menu_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 110, 200, 50)
        shop_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 170, 200, 50)
        
        while True:
            self.screen.fill(BLACK)
            self.draw_text("GAME OVER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, RED, align="center")
            self.draw_text(f"Punkte: {self.game.score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, WHITE, align="center")
            self.draw_text(f"Gesamtpunkte: {self.game.total_score:,}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 25, (255, 215, 0), align="center")
            
            # Draw buttons
            pygame.draw.rect(self.screen, (50, 200, 50), restart_button)
            pygame.draw.rect(self.screen, WHITE, restart_button, 2)
            self.draw_text("Neustart", restart_button.centerx, restart_button.centery - 10, align="center")
            
            pygame.draw.rect(self.screen, (50, 50, 200), menu_button)
            pygame.draw.rect(self.screen, WHITE, menu_button, 2)
            self.draw_text("Hauptmenü", menu_button.centerx, menu_button.centery - 10, align="center")
            
            pygame.draw.rect(self.screen, (200, 150, 50), shop_button)
            pygame.draw.rect(self.screen, WHITE, shop_button, 2)
            self.draw_text("Shop", shop_button.centerx, shop_button.centery - 10, align="center")
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if restart_button.collidepoint(event.pos):
                        self.game.new()
                        return
                    if menu_button.collidepoint(event.pos):
                        self.show_start_screen()
                        return
                    if shop_button.collidepoint(event.pos):
                        self.show_unified_shop()
    
    def show_tutorial(self):
        """Displays the tutorial screen"""
        back_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 40)
        play_btn = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 140, 200, 40)
        
        while True:
            self.screen.fill(DARK_GREY)
            
            # Title
            title_text = self.large_font.render("SPIELANLEITUNG", True, (255, 215, 0))
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - 180, 40))
            
            instructions = [
                "WASD: Bewegen",
                "Maus: Zielen",
                "Linke Maustaste: Schießen",
                "R: Nachladen",
                "",
                "Ziel: Überlebe so lange wie möglich!",
                "Eliminiere Rote Gegner.",
                "Weiße Zivilisten NICHT töten (-500 Punkte)!",
                "Sammle Powerups und Punkte.",
                "",
                "Kaufe Upgrades und Farben im Shop."
            ]
            
            for i, line in enumerate(instructions):
                color = RED if "NICHT" in line else WHITE
                text = self.medium_font.render(line, True, color)
                rect = text.get_rect(center=(SCREEN_WIDTH // 2, 120 + i * 35))
                self.screen.blit(text, rect)
            
            # Play button
            pygame.draw.rect(self.screen, (50, 200, 50), play_btn)
            pygame.draw.rect(self.screen, WHITE, play_btn, 2)
            self.draw_text("SPIELEN", play_btn.centerx - 35, play_btn.centery - 10)
            
            # Back button
            pygame.draw.rect(self.screen, LIGHT_GREY, back_button)
            pygame.draw.rect(self.screen, WHITE, back_button, 2)
            self.draw_text("Zurück", back_button.x + 30, back_button.y + 10)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if back_button.collidepoint(event.pos):
                        return
                    if play_btn.collidepoint(event.pos):
                        self.game.new(tutorial_mode=True)
                        return
                        
    def get_text_input(self, prompt, default_text="", max_length=15):
        """Shows a popup to get text input from the user"""
        input_box = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 40)
        color_inactive = pygame.Color('lightskyblue3')
        color_active = pygame.Color('dodgerblue2')
        color = color_active
        text = default_text
        active = True
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return text
                    elif event.key == pygame.K_ESCAPE:
                        return None
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        if len(text) < max_length:
                            text += event.unicode
            
            # Draw
            # Overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            prompt_surface = self.font.render(prompt, True, WHITE)
            self.screen.blit(prompt_surface, (SCREEN_WIDTH // 2 - prompt_surface.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            
            txt_surface = self.font.render(text, True, color)
            width = max(200, txt_surface.get_width() + 10)
            input_box.w = width
            input_box.centerx = SCREEN_WIDTH // 2
            
            self.screen.blit(txt_surface, (input_box.x + 5, input_box.y + 10))
            pygame.draw.rect(self.screen, color, input_box, 2)
            
            pygame.display.flip()


    def show_multiplayer_menu(self):
        """Multiplayer host/join selection menu"""
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
            self.game.start_multiplayer_game(client, is_host=True)
    
    def multiplayer_join(self):
        """Join multiplayer game via room code"""
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
            self.game.start_multiplayer_game(client, is_host=False)
        else:
            self.show_message_box("Fehler", f"Raum '{room_code}' nicht gefunden!")
            client.close()

    def show_multiplayer_game_over(self, winner, client, is_host):
        """Show multiplayer game over screen with rematch option"""
        rematch_btn = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, 300, 60)
        menu_btn = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 130, 300, 60)
        
        waiting = True
        while waiting and client.connected:
            self.screen.fill(0) 
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
            
            stats_text = f"Mein Treffer: {self.game.player.hit_count} | Gegner Treffer: {self.game.network_player.hit_count}"
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
                    return 'rematch'
                if msg.get('type') == 'left':
                    return 'menu'

        return 'menu'
    
    # ... (Truncated due to length, would include all other shops and helper methods, making sure to use self.game.variable) ...
    # I will continue adding the rest of the methods in subsequent edits to avoid tool limit.
    # For now, I'll add the most important ones and then append.

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
