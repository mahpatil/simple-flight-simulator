"""
Airport definitions and flight route management for the flight simulator.
Includes major international airports with runway information and coordinates.
"""

import pygame
import math
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional

@dataclass
class Runway:
    """Runway information for an airport"""
    number: str  # e.g., "09L/27R"
    length: float  # feet
    width: float  # feet
    heading: float  # degrees (magnetic)
    x_offset: float  # offset from airport center
    y_offset: float  # offset from airport center

@dataclass
class Airport:
    """Airport information and properties"""
    code: str  # IATA code (e.g., "JFK")
    name: str  # Full airport name
    city: str  # City name
    country: str  # Country name
    x: float  # World X coordinate (simplified)
    y: float  # World Y coordinate (simplified)
    elevation: float  # feet above sea level
    runways: List[Runway]
    color: Tuple[int, int, int]  # RGB color for display
    
    def get_primary_runway(self) -> Runway:
        """Get the primary (longest) runway"""
        return max(self.runways, key=lambda r: r.length)
    
    def get_runway_start_position(self, runway: Runway) -> Tuple[float, float]:
        """Get the starting position of a specific runway"""
        return (self.x + runway.x_offset, self.y + runway.y_offset)
    
    def distance_to(self, other_airport: 'Airport') -> float:
        """Calculate distance to another airport in nautical miles (simplified)"""
        dx = other_airport.x - self.x
        dy = other_airport.y - self.y
        distance_pixels = math.sqrt(dx * dx + dy * dy)
        # Convert pixels to nautical miles (simplified conversion)
        return distance_pixels * 0.01
    
    def bearing_to(self, other_airport: 'Airport') -> float:
        """Calculate bearing to another airport in degrees"""
        dx = other_airport.x - self.x
        dy = other_airport.y - self.y
        bearing = math.degrees(math.atan2(dx, -dy))  # Note: -dy for screen coordinates
        return (bearing + 360) % 360  # Normalize to 0-360
    
    def draw_airport(self, screen: pygame.Surface, camera_x: float, camera_y: float, scale: float = 1.0):
        """Draw the airport and its runways"""
        screen_x = int((self.x - camera_x) * scale + screen.get_width() // 2)
        screen_y = int((self.y - camera_y) * scale + screen.get_height() // 2)
        
        # Draw airport terminal (simple square)
        terminal_size = max(8, int(20 * scale))
        terminal_rect = pygame.Rect(
            screen_x - terminal_size // 2,
            screen_y - terminal_size // 2,
            terminal_size,
            terminal_size
        )
        pygame.draw.rect(screen, self.color, terminal_rect)
        
        # Draw runways
        for runway in self.runways:
            runway_x = screen_x + int(runway.x_offset * scale)
            runway_y = screen_y + int(runway.y_offset * scale)
            runway_length = max(20, int(runway.length * scale * 0.01))
            runway_width = max(3, int(runway.width * scale * 0.01))
            
            # Create runway surface
            runway_surface = pygame.Surface((runway_length, runway_width))
            runway_surface.fill((100, 100, 100))  # Gray runway
            
            # Rotate runway based on heading
            rotated_surface = pygame.transform.rotate(runway_surface, -runway.heading)
            rotated_rect = rotated_surface.get_rect(center=(runway_x, runway_y))
            
            screen.blit(rotated_surface, rotated_rect)
        
        # Draw airport code
        font = pygame.font.Font(None, max(16, int(24 * scale)))
        text = font.render(self.code, True, (255, 255, 255))
        text_rect = text.get_rect(center=(screen_x, screen_y + terminal_size + 10))
        screen.blit(text, text_rect)

# Define major international airports
JFK_AIRPORT = Airport(
    code="JFK",
    name="John F. Kennedy International Airport",
    city="New York",
    country="United States",
    x=0,  # Reference point
    y=0,
    elevation=13,
    runways=[
        Runway("04L/22R", 12079, 200, 40, -100, 0),
        Runway("04R/22L", 11351, 200, 40, 100, 0),
        Runway("08L/26R", 10000, 150, 80, 0, -100),
        Runway("08R/26L", 8400, 150, 80, 0, 100)
    ],
    color=(0, 150, 255)
)

LAX_AIRPORT = Airport(
    code="LAX",
    name="Los Angeles International Airport",
    city="Los Angeles",
    country="United States",
    x=-3000,  # West coast
    y=800,
    elevation=125,
    runways=[
        Runway("06L/24R", 10885, 200, 60, -80, 0),
        Runway("06R/24L", 8926, 200, 60, 80, 0),
        Runway("07L/25R", 12091, 200, 70, 0, -90),
        Runway("07R/25L", 11095, 200, 70, 0, 90)
    ],
    color=(255, 200, 0)
)

LHR_AIRPORT = Airport(
    code="LHR",
    name="London Heathrow Airport",
    city="London",
    country="United Kingdom",
    x=4000,  # Across the Atlantic
    y=-500,
    elevation=83,
    runways=[
        Runway("09L/27R", 12799, 164, 90, -100, 0),
        Runway("09R/27L", 12008, 164, 90, 100, 0)
    ],
    color=(0, 255, 100)
)

CDG_AIRPORT = Airport(
    code="CDG",
    name="Charles de Gaulle Airport",
    city="Paris",
    country="France",
    x=4200,  # Near London
    y=200,
    elevation=392,
    runways=[
        Runway("08L/26R", 13123, 197, 80, -120, 0),
        Runway("08R/26L", 13780, 197, 80, 120, 0),
        Runway("09/27", 8858, 197, 90, 0, -150),
        Runway("10/28", 9843, 197, 100, 0, 150)
    ],
    color=(255, 100, 255)
)

NRT_AIRPORT = Airport(
    code="NRT",
    name="Narita International Airport",
    city="Tokyo",
    country="Japan",
    x=8000,  # Far east
    y=1000,
    elevation=135,
    runways=[
        Runway("16L/34R", 13123, 197, 160, -100, 0),
        Runway("16R/34L", 8202, 197, 160, 100, 0)
    ],
    color=(255, 0, 150)
)

# Dictionary of all airports
AIRPORTS = {
    "JFK": JFK_AIRPORT,
    "LAX": LAX_AIRPORT,
    "LHR": LHR_AIRPORT,
    "CDG": CDG_AIRPORT,
    "NRT": NRT_AIRPORT
}

@dataclass
class FlightRoute:
    """Flight route between two airports"""
    departure: Airport
    arrival: Airport
    distance: float  # nautical miles
    duration: float  # hours (at cruise speed)
    waypoints: List[Tuple[float, float]]  # intermediate points
    
    def __post_init__(self):
        """Calculate route properties after initialization"""
        self.distance = self.departure.distance_to(self.arrival)
        # Estimate duration based on average commercial aircraft cruise speed (450 knots)
        self.duration = self.distance / 450.0
        
        # Generate simple waypoints (straight line for now)
        if not self.waypoints:
            self.waypoints = [
                (self.departure.x, self.departure.y),
                (self.arrival.x, self.arrival.y)
            ]

class RouteManager:
    """Manages flight routes between airports"""
    
    def __init__(self):
        self.routes: Dict[Tuple[str, str], FlightRoute] = {}
        self._generate_all_routes()
    
    def _generate_all_routes(self):
        """Generate routes between all airport pairs"""
        airport_codes = list(AIRPORTS.keys())
        for i, dep_code in enumerate(airport_codes):
            for arr_code in airport_codes[i+1:]:
                dep_airport = AIRPORTS[dep_code]
                arr_airport = AIRPORTS[arr_code]
                
                # Create route in both directions
                route_forward = FlightRoute(dep_airport, arr_airport, 0, 0, [])
                route_backward = FlightRoute(arr_airport, dep_airport, 0, 0, [])
                
                self.routes[(dep_code, arr_code)] = route_forward
                self.routes[(arr_code, dep_code)] = route_backward
    
    def get_route(self, departure_code: str, arrival_code: str) -> Optional[FlightRoute]:
        """Get a route between two airports"""
        return self.routes.get((departure_code, arrival_code))
    
    def get_all_destinations(self, departure_code: str) -> List[str]:
        """Get all possible destinations from a departure airport"""
        destinations = []
        for (dep, arr) in self.routes.keys():
            if dep == departure_code and arr != departure_code:
                destinations.append(arr)
        return destinations
    
    def draw_route(self, screen: pygame.Surface, route: FlightRoute, 
                   camera_x: float, camera_y: float, scale: float = 1.0):
        """Draw a flight route on the screen"""
        points = []
        for wp_x, wp_y in route.waypoints:
            screen_x = int((wp_x - camera_x) * scale + screen.get_width() // 2)
            screen_y = int((wp_y - camera_y) * scale + screen.get_height() // 2)
            points.append((screen_x, screen_y))
        
        if len(points) >= 2:
            pygame.draw.lines(screen, (255, 255, 255), False, points, 2)
            
            # Draw distance and duration info
            mid_point = points[len(points) // 2]
            font = pygame.font.Font(None, 24)
            info_text = f"{route.distance:.0f} nm, {route.duration:.1f}h"
            text_surface = font.render(info_text, True, (255, 255, 255))
            screen.blit(text_surface, mid_point)

def get_airport(code: str) -> Optional[Airport]:
    """Get airport by IATA code"""
    return AIRPORTS.get(code.upper())

def get_airport_codes() -> List[str]:
    """Get list of all airport codes"""
    return list(AIRPORTS.keys())