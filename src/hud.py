"""
Heads-Up Display (HUD) system for the flight simulator.
Displays flight instruments, aircraft information, and navigation data.
"""

import pygame
import math
from typing import Tuple, Optional
from aircraft import Aircraft
from airports import Airport, FlightRoute
from physics import FlightPhysics, FlightPhase

class HUD:
    """Heads-Up Display for flight information"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Colors
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.WHITE = (255, 255, 255)
        self.YELLOW = (255, 255, 0)
        self.BLUE = (0, 150, 255)
        self.GRAY = (128, 128, 128)
        self.BLACK = (0, 0, 0)
        
        # Fonts
        pygame.font.init()
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # HUD visibility
        self.show_hud = True
        self.show_instruments = True
        self.show_navigation = True
        
    def draw_hud(self, screen: pygame.Surface, aircraft: Aircraft, physics: FlightPhysics, 
                 destination: Optional[Airport] = None, route: Optional[FlightRoute] = None):
        """Draw the complete HUD"""
        if not self.show_hud:
            return
            
        # Draw different HUD components
        if self.show_instruments:
            self._draw_flight_instruments(screen, aircraft, physics)
        
        if self.show_navigation and destination:
            self._draw_navigation_info(screen, aircraft, destination, route)
            
        self._draw_aircraft_info(screen, aircraft)
        self._draw_controls_help(screen)
        
    def _draw_flight_instruments(self, screen: pygame.Surface, aircraft: Aircraft, physics: FlightPhysics):
        """Draw primary flight instruments"""
        # Primary Flight Display (PFD) background
        pfd_rect = pygame.Rect(10, 10, 300, 200)
        pfd_surface = pygame.Surface((pfd_rect.width, pfd_rect.height), pygame.SRCALPHA)
        pfd_surface.fill((0, 0, 0, 180))
        
        # Attitude Indicator (Artificial Horizon)
        self._draw_attitude_indicator(pfd_surface, aircraft, 50, 50, 40)
        
        # Airspeed Indicator
        self._draw_airspeed_indicator(pfd_surface, aircraft, 10, 100)
        
        # Altimeter
        self._draw_altimeter(pfd_surface, aircraft, 250, 100)
        
        # Heading Indicator
        self._draw_heading_indicator(pfd_surface, aircraft, 150, 150)
        
        # Vertical Speed Indicator
        flight_info = physics.get_flight_info(aircraft)
        self._draw_vertical_speed(pfd_surface, flight_info.get("vertical_speed", 0), 280, 50)
        
        screen.blit(pfd_surface, pfd_rect)
        
        # Engine instruments
        self._draw_engine_instruments(screen, aircraft)
        
    def _draw_attitude_indicator(self, surface: pygame.Surface, aircraft: Aircraft, x: int, y: int, radius: int):
        """Draw artificial horizon attitude indicator"""
        # Background circle
        pygame.draw.circle(surface, self.GRAY, (x, y), radius, 2)
        
        # Horizon line based on pitch
        pitch_offset = aircraft.pitch * 2  # Scale pitch for display
        horizon_y = y + pitch_offset
        
        # Sky (above horizon)
        if horizon_y < y + radius:
            sky_points = [
                (x - radius, horizon_y),
                (x + radius, horizon_y),
                (x + radius, y - radius),
                (x - radius, y - radius)
            ]
            if len(sky_points) >= 3:
                pygame.draw.polygon(surface, self.BLUE, sky_points)
        
        # Ground (below horizon)
        if horizon_y > y - radius:
            ground_points = [
                (x - radius, horizon_y),
                (x + radius, horizon_y),
                (x + radius, y + radius),
                (x - radius, y + radius)
            ]
            if len(ground_points) >= 3:
                pygame.draw.polygon(surface, (139, 69, 19), ground_points)  # Brown for ground
        
        # Horizon line
        pygame.draw.line(surface, self.WHITE, (x - radius, horizon_y), (x + radius, horizon_y), 3)
        
        # Roll indicator (bank angle)
        roll_rad = math.radians(aircraft.roll)
        roll_line_length = radius - 5
        roll_x = x + roll_line_length * math.sin(roll_rad)
        roll_y = y - roll_line_length * math.cos(roll_rad)
        pygame.draw.line(surface, self.YELLOW, (x, y), (roll_x, roll_y), 3)
        
        # Center dot
        pygame.draw.circle(surface, self.WHITE, (x, y), 3)
        
    def _draw_airspeed_indicator(self, surface: pygame.Surface, aircraft: Aircraft, x: int, y: int):
        """Draw airspeed indicator"""
        speed_text = f"{aircraft.speed:.0f}"
        speed_surface = self.font_medium.render(f"IAS: {speed_text} kts", True, self.WHITE)
        surface.blit(speed_surface, (x, y))
        
        # Speed trend indicator
        stall_speed = aircraft.specs.stall_speed
        if aircraft.speed < stall_speed * 1.2:
            warning_surface = self.font_small.render("STALL WARNING", True, self.RED)
            surface.blit(warning_surface, (x, y + 25))
            
    def _draw_altimeter(self, surface: pygame.Surface, aircraft: Aircraft, x: int, y: int):
        """Draw altimeter"""
        alt_text = f"{aircraft.altitude:.0f}"
        alt_surface = self.font_medium.render(f"ALT: {alt_text} ft", True, self.WHITE)
        # Right-align the altimeter
        text_rect = alt_surface.get_rect()
        surface.blit(alt_surface, (x - text_rect.width, y))
        
    def _draw_heading_indicator(self, surface: pygame.Surface, aircraft: Aircraft, x: int, y: int):
        """Draw heading indicator (compass)"""
        heading_text = f"{aircraft.heading:.0f}°"
        heading_surface = self.font_medium.render(f"HDG: {heading_text}", True, self.WHITE)
        text_rect = heading_surface.get_rect(center=(x, y))
        surface.blit(heading_surface, text_rect)
        
    def _draw_vertical_speed(self, surface: pygame.Surface, vertical_speed: float, x: int, y: int):
        """Draw vertical speed indicator"""
        vs_text = f"{vertical_speed:.0f}"
        vs_surface = self.font_small.render(f"VS: {vs_text}", True, self.WHITE)
        text_rect = vs_surface.get_rect()
        surface.blit(vs_surface, (x - text_rect.width, y))
        
    def _draw_engine_instruments(self, screen: pygame.Surface, aircraft: Aircraft):
        """Draw engine instruments"""
        engine_rect = pygame.Rect(self.screen_width - 200, 10, 180, 120)
        engine_surface = pygame.Surface((engine_rect.width, engine_rect.height), pygame.SRCALPHA)
        engine_surface.fill((0, 0, 0, 180))
        
        y_offset = 10
        
        # Throttle
        throttle_text = f"THR: {aircraft.throttle:.0f}%"
        throttle_surface = self.font_small.render(throttle_text, True, self.WHITE)
        engine_surface.blit(throttle_surface, (10, y_offset))
        y_offset += 20
        
        # Fuel
        fuel_percent = (aircraft.fuel / aircraft.specs.fuel_capacity) * 100 if aircraft.specs.fuel_capacity > 0 else 0
        fuel_color = self.RED if fuel_percent < 10 else self.YELLOW if fuel_percent < 25 else self.WHITE
        fuel_text = f"FUEL: {fuel_percent:.1f}%"
        fuel_surface = self.font_small.render(fuel_text, True, fuel_color)
        engine_surface.blit(fuel_surface, (10, y_offset))
        y_offset += 20
        
        # Engine status
        engine_status = "ON" if aircraft.engine_on else "OFF"
        engine_color = self.GREEN if aircraft.engine_on else self.RED
        engine_text = f"ENG: {engine_status}"
        engine_surface = self.font_small.render(engine_text, True, engine_color)
        engine_surface.blit(engine_surface, (10, y_offset))
        y_offset += 20
        
        # Gear status
        gear_status = "DOWN" if aircraft.gear_down else "UP"
        gear_color = self.GREEN if aircraft.gear_down else self.WHITE
        gear_text = f"GEAR: {gear_status}"
        gear_surface = self.font_small.render(gear_text, True, gear_color)
        engine_surface.blit(gear_surface, (10, y_offset))
        
        screen.blit(engine_surface, engine_rect)
        
    def _draw_navigation_info(self, screen: pygame.Surface, aircraft: Aircraft, 
                             destination: Airport, route: Optional[FlightRoute]):
        """Draw navigation information"""
        nav_rect = pygame.Rect(10, self.screen_height - 150, 300, 140)
        nav_surface = pygame.Surface((nav_rect.width, nav_rect.height), pygame.SRCALPHA)
        nav_surface.fill((0, 0, 0, 180))
        
        y_offset = 10
        
        # Destination info
        dest_text = f"DEST: {destination.code} - {destination.name}"
        dest_surface = self.font_small.render(dest_text, True, self.WHITE)
        nav_surface.blit(dest_surface, (10, y_offset))
        y_offset += 20
        
        # Distance to destination
        distance = math.sqrt((destination.x - aircraft.x) ** 2 + (destination.y - aircraft.y) ** 2) * 0.01
        dist_text = f"DIST: {distance:.1f} nm"
        dist_surface = self.font_small.render(dist_text, True, self.WHITE)
        nav_surface.blit(dist_surface, (10, y_offset))
        y_offset += 20
        
        # Bearing to destination
        bearing = math.degrees(math.atan2(destination.x - aircraft.x, -(destination.y - aircraft.y)))
        bearing = (bearing + 360) % 360
        bearing_text = f"BRG: {bearing:.0f}°"
        bearing_surface = self.font_small.render(bearing_text, True, self.WHITE)
        nav_surface.blit(bearing_surface, (10, y_offset))
        y_offset += 20
        
        # ETA (estimated time of arrival)
        if aircraft.speed > 0:
            eta_hours = distance / aircraft.speed
            eta_minutes = (eta_hours % 1) * 60
            eta_text = f"ETA: {int(eta_hours)}h {int(eta_minutes)}m"
            eta_surface = self.font_small.render(eta_text, True, self.WHITE)
            nav_surface.blit(eta_surface, (10, y_offset))
        
        screen.blit(nav_surface, nav_rect)
        
    def _draw_aircraft_info(self, screen: pygame.Surface, aircraft: Aircraft):
        """Draw aircraft model information"""
        info_rect = pygame.Rect(self.screen_width - 250, self.screen_height - 80, 240, 70)
        info_surface = pygame.Surface((info_rect.width, info_rect.height), pygame.SRCALPHA)
        info_surface.fill((0, 0, 0, 180))
        
        # Aircraft name
        name_text = aircraft.specs.name
        name_surface = self.font_medium.render(name_text, True, self.WHITE)
        info_surface.blit(name_surface, (10, 10))
        
        # Max speed
        max_speed_text = f"Max Speed: {aircraft.specs.max_speed:.0f} kts"
        max_speed_surface = self.font_small.render(max_speed_text, True, self.WHITE)
        info_surface.blit(max_speed_surface, (10, 35))
        
        screen.blit(info_surface, info_rect)
        
    def _draw_controls_help(self, screen: pygame.Surface):
        """Draw controls help"""
        help_rect = pygame.Rect(self.screen_width - 300, 150, 280, 200)
        help_surface = pygame.Surface((help_rect.width, help_rect.height), pygame.SRCALPHA)
        help_surface.fill((0, 0, 0, 120))
        
        controls = [
            "CONTROLS:",
            "W/S - Pitch Up/Down",
            "A/D - Yaw Left/Right", 
            "Q/E - Roll Left/Right",
            "R/F - Throttle Up/Down",
            "SPACE - Toggle Gear",
            "C - Change Camera",
            "ESC - Exit"
        ]
        
        y_offset = 10
        for control in controls:
            color = self.YELLOW if control == "CONTROLS:" else self.WHITE
            font = self.font_small if control != "CONTROLS:" else self.font_medium
            control_surface = font.render(control, True, color)
            help_surface.blit(control_surface, (10, y_offset))
            y_offset += 20
            
        screen.blit(help_surface, help_rect)
        
    def toggle_hud(self):
        """Toggle HUD visibility"""
        self.show_hud = not self.show_hud
        
    def toggle_instruments(self):
        """Toggle instruments visibility"""
        self.show_instruments = not self.show_instruments
        
    def toggle_navigation(self):
        """Toggle navigation info visibility"""
        self.show_navigation = not self.show_navigation