"""
Main game interface and entry point for the Simple Flight Simulator.
Handles game loop, menus, and overall game state management.
"""

import pygame
import sys
from enum import Enum
from typing import Optional, Tuple

# Import our modules
from aircraft import Aircraft, create_aircraft, AIRCRAFT_MODELS
from airports import AIRPORTS, get_airport_codes, RouteManager
from camera import Camera, CameraMode
from physics import FlightControls, FlightPhysics
from hud import HUD

class GameState(Enum):
    """Game states"""
    MAIN_MENU = "main_menu"
    AIRCRAFT_SELECT = "aircraft_select"
    AIRPORT_SELECT = "airport_select"
    FLIGHT = "flight"
    PAUSED = "paused"

class FlightSimulator:
    """Main flight simulator game class"""
    
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        
        # Screen setup
        self.SCREEN_WIDTH = 1200
        self.SCREEN_HEIGHT = 800
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Simple Flight Simulator")
        
        # Game clock
        self.clock = pygame.time.Clock()
        self.FPS = 60
        
        # Game state
        self.state = GameState.MAIN_MENU
        self.running = True
        self.paused = False
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (0, 100, 200)
        self.GREEN = (0, 150, 50)
        self.RED = (200, 50, 0)
        self.GRAY = (128, 128, 128)
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Game components
        self.aircraft: Optional[Aircraft] = None
        self.departure_airport = None
        self.destination_airport = None
        self.route_manager = RouteManager()
        self.current_route = None
        
        # Systems
        self.camera = Camera(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.controls = FlightControls()
        self.physics = FlightPhysics()
        self.hud = HUD(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # Menu selections
        self.selected_aircraft_index = 0
        self.selected_departure_index = 0
        self.selected_destination_index = 0
        
        # Background
        self.background_color = (50, 150, 255)  # Sky blue
        
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(self.FPS) / 1000.0  # Delta time in seconds
            
            self.handle_events()
            self.update(dt)
            self.draw()
            
        pygame.quit()
        sys.exit()
        
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)
                
    def handle_keydown(self, key):
        """Handle keydown events"""
        if key == pygame.K_ESCAPE:
            if self.state == GameState.FLIGHT:
                self.state = GameState.PAUSED
            elif self.state == GameState.PAUSED:
                self.state = GameState.FLIGHT
            else:
                self.running = False
                
        elif key == pygame.K_c and self.state == GameState.FLIGHT:
            self.camera.cycle_mode()
            
        elif key == pygame.K_h and self.state == GameState.FLIGHT:
            self.hud.toggle_hud()
            
        elif self.state == GameState.MAIN_MENU:
            if key == pygame.K_RETURN or key == pygame.K_SPACE:
                self.state = GameState.AIRCRAFT_SELECT
                
        elif self.state == GameState.AIRCRAFT_SELECT:
            if key == pygame.K_UP:
                self.selected_aircraft_index = (self.selected_aircraft_index - 1) % len(AIRCRAFT_MODELS)
            elif key == pygame.K_DOWN:
                self.selected_aircraft_index = (self.selected_aircraft_index + 1) % len(AIRCRAFT_MODELS)
            elif key == pygame.K_RETURN:
                self.state = GameState.AIRPORT_SELECT
                
        elif self.state == GameState.AIRPORT_SELECT:
            airport_codes = get_airport_codes()
            if key == pygame.K_UP:
                self.selected_departure_index = (self.selected_departure_index - 1) % len(airport_codes)
            elif key == pygame.K_DOWN:
                self.selected_departure_index = (self.selected_departure_index + 1) % len(airport_codes)
            elif key == pygame.K_LEFT:
                self.selected_destination_index = (self.selected_destination_index - 1) % len(airport_codes)
            elif key == pygame.K_RIGHT:
                self.selected_destination_index = (self.selected_destination_index + 1) % len(airport_codes)
            elif key == pygame.K_RETURN:
                self.start_flight()
                
        # Pass key events to controls during flight
        if self.state == GameState.FLIGHT:
            self.controls.handle_key_press(key)
            
    def start_flight(self):
        """Initialize and start the flight"""
        # Get selected aircraft model
        aircraft_names = list(AIRCRAFT_MODELS.keys())
        selected_aircraft_name = aircraft_names[self.selected_aircraft_index]
        
        # Get selected airports
        airport_codes = get_airport_codes()
        departure_code = airport_codes[self.selected_departure_index]
        destination_code = airport_codes[self.selected_destination_index]
        
        # Ensure different airports
        if departure_code == destination_code:
            destination_code = airport_codes[(self.selected_destination_index + 1) % len(airport_codes)]
            
        self.departure_airport = AIRPORTS[departure_code]
        self.destination_airport = AIRPORTS[destination_code]
        
        # Create aircraft at departure airport
        runway = self.departure_airport.get_primary_runway()
        start_x, start_y = self.departure_airport.get_runway_start_position(runway)
        
        self.aircraft = create_aircraft(selected_aircraft_name, start_x, start_y, self.departure_airport.elevation)
        self.aircraft.heading = runway.heading
        
        # Get route
        self.current_route = self.route_manager.get_route(departure_code, destination_code)
        
        # Initialize camera
        self.camera.mode = CameraMode.CHASE
        
        # Start flight
        self.state = GameState.FLIGHT
        
    def update(self, dt: float):
        """Update game state"""
        if self.state == GameState.FLIGHT and not self.paused:
            # Update controls from keyboard
            keys = pygame.key.get_pressed()
            self.controls.update_from_keyboard(keys)
            
            # Update aircraft physics
            if self.aircraft:
                self.physics.update_aircraft_physics(self.aircraft, self.controls, dt)
                self.camera.update(self.aircraft, dt)
                
    def draw(self):
        """Draw the game"""
        self.screen.fill(self.background_color)
        
        if self.state == GameState.MAIN_MENU:
            self.draw_main_menu()
        elif self.state == GameState.AIRCRAFT_SELECT:
            self.draw_aircraft_select()
        elif self.state == GameState.AIRPORT_SELECT:
            self.draw_airport_select()
        elif self.state == GameState.FLIGHT:
            self.draw_flight()
        elif self.state == GameState.PAUSED:
            self.draw_flight()  # Draw flight scene
            self.draw_pause_menu()
            
        pygame.display.flip()
        
    def draw_main_menu(self):
        """Draw main menu"""
        title = self.font_large.render("Simple Flight Simulator", True, self.WHITE)
        title_rect = title.get_rect(center=(self.SCREEN_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font_medium.render("Press ENTER or SPACE to start", True, self.WHITE)
        subtitle_rect = subtitle.get_rect(center=(self.SCREEN_WIDTH // 2, 300))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Instructions
        instructions = [
            "Features:",
            "• 5 Different Aircraft Models",
            "• 5 International Airports", 
            "• Realistic Flight Physics",
            "• Multiple Camera Views",
            "• Full Flight Instruments"
        ]
        
        y_offset = 400
        for instruction in instructions:
            text = self.font_small.render(instruction, True, self.WHITE)
            text_rect = text.get_rect(center=(self.SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30
            
    def draw_aircraft_select(self):
        """Draw aircraft selection menu"""
        title = self.font_large.render("Select Aircraft", True, self.WHITE)
        title_rect = title.get_rect(center=(self.SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Aircraft list
        aircraft_names = list(AIRCRAFT_MODELS.keys())
        y_offset = 200
        
        for i, aircraft_name in enumerate(aircraft_names):
            color = self.GREEN if i == self.selected_aircraft_index else self.WHITE
            text = self.font_medium.render(aircraft_name, True, color)
            text_rect = text.get_rect(center=(self.SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            
            # Show selected aircraft specs
            if i == self.selected_aircraft_index:
                specs = AIRCRAFT_MODELS[aircraft_name]
                spec_texts = [
                    f"Max Speed: {specs.max_speed:.0f} knots",
                    f"Cruise Speed: {specs.cruise_speed:.0f} knots", 
                    f"Max Altitude: {specs.max_altitude:.0f} feet",
                    f"Wingspan: {specs.wingspan:.1f} feet"
                ]
                
                spec_y = y_offset + 40
                for spec_text in spec_texts:
                    spec_surface = self.font_small.render(spec_text, True, self.GRAY)
                    spec_rect = spec_surface.get_rect(center=(self.SCREEN_WIDTH // 2, spec_y))
                    self.screen.blit(spec_surface, spec_rect)
                    spec_y += 20
                    
            y_offset += 100
            
        # Instructions
        instructions = self.font_small.render("Use UP/DOWN arrows to select, ENTER to confirm", True, self.WHITE)
        instructions_rect = instructions.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 50))
        self.screen.blit(instructions, instructions_rect)
        
    def draw_airport_select(self):
        """Draw airport selection menu"""
        title = self.font_large.render("Select Airports", True, self.WHITE)
        title_rect = title.get_rect(center=(self.SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Departure airport
        dep_title = self.font_medium.render("Departure Airport:", True, self.WHITE)
        self.screen.blit(dep_title, (100, 150))
        
        airport_codes = get_airport_codes()
        dep_airport_code = airport_codes[self.selected_departure_index]
        dep_airport = AIRPORTS[dep_airport_code]
        dep_text = f"{dep_airport.code} - {dep_airport.name}"
        dep_surface = self.font_medium.render(dep_text, True, self.GREEN)
        self.screen.blit(dep_surface, (100, 180))
        
        # Destination airport
        dest_title = self.font_medium.render("Destination Airport:", True, self.WHITE)
        self.screen.blit(dest_title, (100, 250))
        
        dest_airport_code = airport_codes[self.selected_destination_index]
        dest_airport = AIRPORTS[dest_airport_code]
        dest_text = f"{dest_airport.code} - {dest_airport.name}"
        dest_surface = self.font_medium.render(dest_text, True, self.GREEN)
        self.screen.blit(dest_surface, (100, 280))
        
        # Distance info
        if dep_airport_code != dest_airport_code:
            distance = dep_airport.distance_to(dest_airport)
            distance_text = f"Distance: {distance:.0f} nautical miles"
            distance_surface = self.font_small.render(distance_text, True, self.WHITE)
            self.screen.blit(distance_surface, (100, 320))
            
        # Instructions
        instructions = [
            "UP/DOWN: Change departure airport",
            "LEFT/RIGHT: Change destination airport", 
            "ENTER: Start flight"
        ]
        
        y_offset = self.SCREEN_HEIGHT - 100
        for instruction in instructions:
            text = self.font_small.render(instruction, True, self.WHITE)
            self.screen.blit(text, (100, y_offset))
            y_offset += 20
            
    def draw_flight(self):
        """Draw flight simulation"""
        # Get camera transform
        camera_x, camera_y, zoom = self.camera.get_world_to_screen_transform()
        
        # Draw world objects
        if self.departure_airport:
            self.departure_airport.draw_airport(self.screen, camera_x, camera_y, zoom)
            
        if self.destination_airport:
            self.destination_airport.draw_airport(self.screen, camera_x, camera_y, zoom)
            
        # Draw flight route
        if self.current_route:
            self.route_manager.draw_route(self.screen, self.current_route, camera_x, camera_y, zoom)
            
        # Draw aircraft
        if self.aircraft:
            self.aircraft.draw_aircraft(self.screen, camera_x, camera_y, zoom)
            
        # Draw HUD
        if self.aircraft:
            self.hud.draw_hud(self.screen, self.aircraft, self.physics, 
                             self.destination_airport, self.current_route)
            
        # Draw camera info
        if self.aircraft:
            self.camera.draw_camera_info(self.screen, self.aircraft)
            
    def draw_pause_menu(self):
        """Draw pause menu overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.font_large.render("PAUSED", True, self.WHITE)
        pause_rect = pause_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(pause_text, pause_rect)
        
        # Instructions
        instructions = [
            "ESC - Resume Flight",
            "C - Change Camera View",
            "H - Toggle HUD"
        ]
        
        y_offset = self.SCREEN_HEIGHT // 2 + 20
        for instruction in instructions:
            text = self.font_medium.render(instruction, True, self.WHITE)
            text_rect = text.get_rect(center=(self.SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30

def main():
    """Main entry point"""
    simulator = FlightSimulator()
    simulator.run()

if __name__ == "__main__":
    main()