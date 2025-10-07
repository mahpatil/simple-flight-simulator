"""
Controls test for the flight simulator.
Tests keyboard input and aircraft response.
"""

import pygame
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from aircraft import create_aircraft
from physics import FlightControls, FlightPhysics

def test_controls():
    """Test aircraft controls interactively"""
    pygame.init()
    
    # Set up display
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Controls Test - Use WASD, QE, RF keys")
    
    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    BLUE = (0, 150, 255)
    
    # Font
    font = pygame.font.Font(None, 24)
    
    # Create test aircraft
    aircraft = create_aircraft("Boeing 737-800", 0, 0, 0)
    controls = FlightControls()
    physics = FlightPhysics()
    
    clock = pygame.time.Clock()
    running = True
    
    print("Controls Test Started!")
    print("Use these keys and watch the values change:")
    print("W/S - Pitch Up/Down")
    print("A/D - Yaw Left/Right")
    print("Q/E - Roll Left/Right")
    print("R/F - Throttle Up/Down")
    print("Space - Toggle Gear")
    print("ESC - Exit")
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    controls.handle_key_press(event.key)
        
        # Update controls from keyboard
        keys = pygame.key.get_pressed()
        controls.update_from_keyboard(keys)
        
        # Update aircraft physics
        physics.update_aircraft_physics(aircraft, controls, dt)
        
        # Clear screen
        screen.fill(BLACK)
        
        # Display current values
        y_offset = 50
        
        # Title
        title = font.render("Aircraft Controls Test", True, WHITE)
        screen.blit(title, (50, 20))
        
        # Control inputs
        controls_info = [
            f"Pitch Input (W/S): {controls.pitch_input:.2f}",
            f"Yaw Input (A/D): {controls.yaw_input:.2f}",
            f"Roll Input (Q/E): {controls.roll_input:.2f}",
            f"Throttle Input (R/F): {controls.throttle_input:.2f}",
            f"Gear Down (Space): {controls.gear_toggle}",
        ]
        
        for info in controls_info:
            color = GREEN if any(val != 0 and val != False for val in [
                controls.pitch_input, controls.yaw_input, 
                controls.roll_input, controls.throttle_input
            ]) else WHITE
            text = font.render(info, True, color)
            screen.blit(text, (50, y_offset))
            y_offset += 30
        
        y_offset += 20
        
        # Aircraft state
        aircraft_info = [
            f"Aircraft Speed: {aircraft.speed:.1f} knots",
            f"Aircraft Heading: {aircraft.heading:.1f}°",
            f"Aircraft Pitch: {aircraft.pitch:.1f}°",
            f"Aircraft Roll: {aircraft.roll:.1f}°",
            f"Aircraft Altitude: {aircraft.altitude:.1f} ft",
            f"Engine On: {aircraft.engine_on}",
            f"Throttle: {aircraft.throttle:.0f}%",
        ]
        
        for info in aircraft_info:
            color = BLUE
            text = font.render(info, True, color)
            screen.blit(text, (50, y_offset))
            y_offset += 25
        
        # Instructions
        y_offset += 20
        instructions = [
            "Press and hold keys to see changes:",
            "W - Pitch up (nose up)",
            "S - Pitch down (nose down)", 
            "A - Yaw left (turn left)",
            "D - Yaw right (turn right)",
            "Q - Roll left (bank left)",
            "E - Roll right (bank right)",
            "R - Throttle up (increase power)",
            "F - Throttle down (decrease power)",
            "Space - Toggle landing gear",
            "ESC - Exit test"
        ]
        
        for instruction in instructions:
            color = WHITE if instruction.startswith("Press") else WHITE
            text = font.render(instruction, True, color)
            screen.blit(text, (400, y_offset))
            y_offset += 20
        
        # Show active keys
        active_keys = []
        if keys[pygame.K_w]: active_keys.append("W")
        if keys[pygame.K_s]: active_keys.append("S")
        if keys[pygame.K_a]: active_keys.append("A")
        if keys[pygame.K_d]: active_keys.append("D")
        if keys[pygame.K_q]: active_keys.append("Q")
        if keys[pygame.K_e]: active_keys.append("E")
        if keys[pygame.K_r]: active_keys.append("R")
        if keys[pygame.K_f]: active_keys.append("F")
        
        if active_keys:
            active_text = f"Active Keys: {', '.join(active_keys)}"
            active_surface = font.render(active_text, True, GREEN)
            screen.blit(active_surface, (50, SCREEN_HEIGHT - 50))
        
        pygame.display.flip()
    
    pygame.quit()
    
    print("\nFinal Aircraft State:")
    print(f"Speed: {aircraft.speed:.1f} knots")
    print(f"Heading: {aircraft.heading:.1f}°")
    print(f"Pitch: {aircraft.pitch:.1f}°")
    print(f"Altitude: {aircraft.altitude:.1f} ft")

if __name__ == "__main__":
    test_controls()