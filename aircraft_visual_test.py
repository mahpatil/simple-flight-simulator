"""
Visual test for the improved aircraft rendering.
Shows all aircraft models with their new detailed appearance.
"""

import pygame
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from aircraft import create_aircraft, AIRCRAFT_MODELS

def test_aircraft_visuals():
    """Test the visual appearance of all aircraft"""
    pygame.init()
    
    # Set up display
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 700
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Aircraft Visual Test - Press ESC to exit")
    
    # Colors
    SKY_BLUE = (135, 206, 235)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    
    # Fonts
    font_large = pygame.font.Font(None, 36)
    font_medium = pygame.font.Font(None, 24)
    
    # Create aircraft instances
    aircraft_list = []
    aircraft_names = list(AIRCRAFT_MODELS.keys())
    
    # Position aircraft in a grid
    positions = [
        (200, 150), (500, 150), (800, 150),
        (350, 350), (650, 350)
    ]
    
    for i, name in enumerate(aircraft_names):
        if i < len(positions):
            x, y = positions[i]
            aircraft = create_aircraft(name, x, y, 5000)
            aircraft.heading = 45  # Angled for better view
            aircraft_list.append(aircraft)
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
               (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
        
        # Clear screen with sky color
        screen.fill(SKY_BLUE)
        
        # Draw title
        title = font_large.render("Aircraft Models - Improved Visuals", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 30))
        
        # Draw black outline for title
        for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            title_outline = font_large.render("Aircraft Models - Improved Visuals", True, BLACK)
            screen.blit(title_outline, (title_rect.x + dx, title_rect.y + dy))
        
        screen.blit(title, title_rect)
        
        # Draw each aircraft
        for aircraft in aircraft_list:
            # Draw aircraft with no camera offset (static display)
            aircraft.draw_aircraft(screen, 0, 0, 2.0)  # 2x scale for better visibility
            
            # Draw aircraft name below
            name_text = font_medium.render(aircraft.specs.name, True, BLACK)
            name_rect = name_text.get_rect(center=(aircraft.x, aircraft.y + 60))
            
            # White background for text
            bg_rect = name_rect.inflate(10, 5)
            pygame.draw.rect(screen, WHITE, bg_rect)
            pygame.draw.rect(screen, BLACK, bg_rect, 2)
            
            screen.blit(name_text, name_rect)
            
            # Draw specifications
            specs_text = [
                f"Max Speed: {aircraft.specs.max_speed:.0f} kts",
                f"Wingspan: {aircraft.specs.wingspan:.0f} ft"
            ]
            
            spec_y = aircraft.y + 85
            for spec in specs_text:
                spec_surface = font_medium.render(spec, True, BLACK)
                spec_rect = spec_surface.get_rect(center=(aircraft.x, spec_y))
                
                # White background for specs
                spec_bg = spec_rect.inflate(6, 3)
                pygame.draw.rect(screen, WHITE, spec_bg)
                screen.blit(spec_surface, spec_rect)
                spec_y += 20
        
        # Instructions
        instruction_text = "Press ESC to exit - Aircraft now have wings, fuselage, engines, and landing gear!"
        instruction = font_medium.render(instruction_text, True, BLACK)
        instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        
        # White background for instructions
        inst_bg = instruction_rect.inflate(10, 5)
        pygame.draw.rect(screen, WHITE, inst_bg)
        screen.blit(instruction, instruction_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    print("Starting Aircraft Visual Test...")
    print("This will show all aircraft models with improved detailed graphics!")
    test_aircraft_visuals()