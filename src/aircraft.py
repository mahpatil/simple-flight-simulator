"""
Aircraft models and specifications for the flight simulator.
Each aircraft has unique flight characteristics and performance data.
"""

import pygame
import math
from dataclasses import dataclass
from typing import Tuple

@dataclass
class AircraftSpecs:
    """Aircraft specifications and performance characteristics"""
    name: str
    max_speed: float  # knots
    cruise_speed: float  # knots
    max_altitude: float  # feet
    fuel_capacity: float  # gallons
    wingspan: float  # feet
    length: float  # feet
    weight: float  # pounds
    climb_rate: float  # feet per minute
    turn_rate: float  # degrees per second
    stall_speed: float  # knots
    takeoff_distance: float  # feet
    landing_distance: float  # feet
    color: Tuple[int, int, int]  # RGB color for display

class Aircraft:
    """Base aircraft class with common properties and methods"""
    
    def __init__(self, specs: AircraftSpecs, x: float = 0, y: float = 0, altitude: float = 0):
        self.specs = specs
        self.x = x
        self.y = y
        self.altitude = altitude
        self.heading = 0  # degrees (0 = North, 90 = East, 180 = South, 270 = West)
        self.speed = 0  # knots
        self.throttle = 0  # 0-100%
        self.pitch = 0  # degrees (-90 to +90)
        self.roll = 0  # degrees (-180 to +180)
        self.fuel = specs.fuel_capacity  # current fuel
        self.gear_down = True
        self.engine_on = False
        
    def update_position(self, dt: float):
        """Update aircraft position based on current speed and heading"""
        if self.speed > 0:
            # Convert speed from knots to pixels per second (simplified)
            speed_pixels_per_sec = self.speed * 0.1
            
            # Convert heading to radians (pygame uses different coordinate system)
            heading_rad = math.radians(self.heading - 90)
            
            # Update position
            self.x += speed_pixels_per_sec * math.cos(heading_rad) * dt
            self.y += speed_pixels_per_sec * math.sin(heading_rad) * dt
            
    def update_altitude(self, dt: float):
        """Update altitude based on pitch and speed"""
        if self.speed > self.specs.stall_speed:
            climb_rate = self.pitch * 10 * (self.speed / self.specs.cruise_speed)
            self.altitude += climb_rate * dt
            
            # Ensure altitude doesn't go below ground
            self.altitude = max(0, min(self.altitude, self.specs.max_altitude))
            
    def update_fuel(self, dt: float):
        """Update fuel consumption based on throttle and altitude"""
        if self.engine_on and self.fuel > 0:
            # Simplified fuel consumption model
            consumption_rate = (self.throttle / 100) * 0.1 + 0.05  # gallons per second
            self.fuel -= consumption_rate * dt
            self.fuel = max(0, self.fuel)
            
    def draw_aircraft(self, screen: pygame.Surface, camera_x: float, camera_y: float, scale: float = 1.0):
        """Draw a detailed representation of the aircraft"""
        screen_x = int((self.x - camera_x) * scale + screen.get_width() // 2)
        screen_y = int((self.y - camera_y) * scale + screen.get_height() // 2)
        
        # Scale aircraft size based on specs and zoom level
        base_length = max(20, int(self.specs.length * scale * 0.15))
        base_width = max(4, int(base_length * 0.2))  # Fuselage width
        wing_span = max(16, int(self.specs.wingspan * scale * 0.12))
        wing_width = max(3, int(wing_span * 0.15))
        
        # Create aircraft surface (larger to accommodate wings)
        surface_size = max(base_length + 20, wing_span + 20)
        aircraft_surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
        center = surface_size // 2
        
        # Colors
        fuselage_color = self.specs.color
        wing_color = tuple(max(0, c - 30) for c in fuselage_color)  # Darker wings
        engine_color = (80, 80, 80)  # Dark gray for engines
        
        # Draw main fuselage (elongated ellipse)
        fuselage_rect = pygame.Rect(
            center - base_length // 2,
            center - base_width // 2,
            base_length,
            base_width
        )
        pygame.draw.ellipse(aircraft_surface, fuselage_color, fuselage_rect)
        
        # Draw cockpit (smaller circle at front)
        cockpit_radius = max(2, base_width // 3)
        cockpit_x = center + base_length // 2 - cockpit_radius
        pygame.draw.circle(aircraft_surface, (200, 200, 255), (cockpit_x, center), cockpit_radius)
        
        # Draw main wings (horizontal)
        wing_rect = pygame.Rect(
            center - wing_width // 2,
            center - wing_span // 2,
            wing_width,
            wing_span
        )
        pygame.draw.rect(aircraft_surface, wing_color, wing_rect)
        
        # Draw wing tips (rounded ends)
        pygame.draw.circle(aircraft_surface, wing_color, 
                          (center, center - wing_span // 2), wing_width // 2)
        pygame.draw.circle(aircraft_surface, wing_color, 
                          (center, center + wing_span // 2), wing_width // 2)
        
        # Draw tail (vertical stabilizer)
        tail_height = max(6, base_length // 3)
        tail_width = max(2, base_width // 2)
        tail_x = center - base_length // 2 + tail_width // 2
        tail_rect = pygame.Rect(
            tail_x - tail_width // 2,
            center - tail_height // 2,
            tail_width,
            tail_height
        )
        pygame.draw.rect(aircraft_surface, wing_color, tail_rect)
        
        # Draw horizontal stabilizer (smaller horizontal tail)
        h_stab_width = max(3, wing_span // 4)
        h_stab_height = max(1, tail_width // 2)
        h_stab_rect = pygame.Rect(
            tail_x - h_stab_height // 2,
            center - h_stab_width // 2,
            h_stab_height,
            h_stab_width
        )
        pygame.draw.rect(aircraft_surface, wing_color, h_stab_rect)
        
        # Draw engines (for larger aircraft)
        if self.specs.max_speed > 400:  # Commercial aircraft
            engine_size = max(2, base_width // 3)
            engine_offset = wing_span // 3
            
            # Left engine
            engine1_x = center - wing_width // 4
            engine1_y = center - engine_offset
            pygame.draw.circle(aircraft_surface, engine_color, (engine1_x, engine1_y), engine_size)
            
            # Right engine
            engine2_x = center - wing_width // 4
            engine2_y = center + engine_offset
            pygame.draw.circle(aircraft_surface, engine_color, (engine2_x, engine2_y), engine_size)
        
        # Add aircraft registration/identifier
        if scale > 0.8:  # Only show when zoomed in enough
            font = pygame.font.Font(None, max(12, int(16 * scale)))
            reg_text = font.render(f"{self.specs.name[:3].upper()}", True, (255, 255, 255))
            text_rect = reg_text.get_rect(center=(center, center + base_width + 8))
            aircraft_surface.blit(reg_text, text_rect)
        
        # Rotate aircraft based on heading
        rotated_surface = pygame.transform.rotate(aircraft_surface, -self.heading)
        rotated_rect = rotated_surface.get_rect(center=(screen_x, screen_y))
        
        screen.blit(rotated_surface, rotated_rect)
        
        # Draw altitude indicator with shadow effect
        if self.altitude > 0:
            shadow_offset = max(1, int(self.altitude / 1000))
            # Shadow
            pygame.draw.circle(screen, (100, 100, 0), 
                             (screen_x + shadow_offset, screen_y + shadow_offset), 4)
            # Main indicator
            pygame.draw.circle(screen, (255, 255, 0), (screen_x, screen_y), 4)
            
        # Draw landing gear (if deployed and on ground or low altitude)
        if self.gear_down and self.altitude < 100:
            gear_color = (150, 150, 150)
            gear_size = max(1, int(2 * scale))
            # Main gear
            pygame.draw.circle(screen, gear_color, (screen_x - 8, screen_y + 6), gear_size)
            pygame.draw.circle(screen, gear_color, (screen_x + 8, screen_y + 6), gear_size)
            # Nose gear
            pygame.draw.circle(screen, gear_color, (screen_x + 12, screen_y), gear_size)

# Aircraft specifications
BOEING_737 = AircraftSpecs(
    name="Boeing 737-800",
    max_speed=544,
    cruise_speed=453,
    max_altitude=41000,
    fuel_capacity=6875,
    wingspan=112.7,
    length=129.5,
    weight=174200,
    climb_rate=2500,
    turn_rate=3.0,
    stall_speed=132,
    takeoff_distance=7200,
    landing_distance=4800,
    color=(0, 100, 200)
)

AIRBUS_A320 = AircraftSpecs(
    name="Airbus A320",
    max_speed=537,
    cruise_speed=447,
    max_altitude=39800,
    fuel_capacity=6400,
    wingspan=117.5,
    length=123.3,
    weight=166400,
    climb_rate=2400,
    turn_rate=3.2,
    stall_speed=127,
    takeoff_distance=6900,
    landing_distance=4600,
    color=(150, 0, 0)
)

BOEING_777 = AircraftSpecs(
    name="Boeing 777-300ER",
    max_speed=590,
    cruise_speed=490,
    max_altitude=43100,
    fuel_capacity=45220,
    wingspan=212.7,
    length=242.4,
    weight=775000,
    climb_rate=2000,
    turn_rate=2.0,
    stall_speed=156,
    takeoff_distance=10400,
    landing_distance=6200,
    color=(100, 50, 150)
)

CESSNA_172 = AircraftSpecs(
    name="Cessna 172",
    max_speed=163,
    cruise_speed=122,
    max_altitude=14200,
    fuel_capacity=56,
    wingspan=36.0,
    length=27.2,
    weight=2550,
    climb_rate=720,
    turn_rate=15.0,
    stall_speed=47,
    takeoff_distance=960,
    landing_distance=1335,
    color=(255, 255, 0)
)

EMBRAER_E190 = AircraftSpecs(
    name="Embraer E190",
    max_speed=487,
    cruise_speed=459,
    max_altitude=41000,
    fuel_capacity=3284,
    wingspan=94.3,
    length=118.99,
    weight=114640,
    climb_rate=2800,
    turn_rate=4.0,
    stall_speed=108,
    takeoff_distance=4685,
    landing_distance=4199,
    color=(0, 150, 100)
)

# Dictionary of all available aircraft
AIRCRAFT_MODELS = {
    "Boeing 737-800": BOEING_737,
    "Airbus A320": AIRBUS_A320,
    "Boeing 777-300ER": BOEING_777,
    "Cessna 172": CESSNA_172,
    "Embraer E190": EMBRAER_E190
}

def create_aircraft(model_name: str, x: float = 0, y: float = 0, altitude: float = 0) -> Aircraft:
    """Create an aircraft instance from model specifications"""
    if model_name not in AIRCRAFT_MODELS:
        raise ValueError(f"Unknown aircraft model: {model_name}")
    
    specs = AIRCRAFT_MODELS[model_name]
    return Aircraft(specs, x, y, altitude)