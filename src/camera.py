"""
Camera system for the flight simulator supporting multiple view modes.
Includes cockpit view, chase camera, and external views.
"""

import pygame
import math
from enum import Enum
from typing import Tuple, Optional
from aircraft import Aircraft

class CameraMode(Enum):
    """Available camera modes"""
    COCKPIT = "Cockpit View"
    CHASE = "Chase Camera"
    EXTERNAL = "External View"
    TOP_DOWN = "Top Down"
    SIDE = "Side View"

class Camera:
    """Camera system for different viewing modes of the aircraft"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.mode = CameraMode.CHASE
        self.x = 0.0
        self.y = 0.0
        self.z = 100.0  # Altitude for 3D-like perspective
        self.zoom = 1.0
        self.smooth_factor = 0.1  # Camera smoothing (0-1, higher = more responsive)
        
        # Chase camera specific settings
        self.chase_distance = 150.0
        self.chase_height = 50.0
        
        # External camera settings
        self.external_angle = 0.0  # Angle around aircraft
        self.external_distance = 200.0
        self.external_height = 100.0
        
        # Target position for smooth following
        self.target_x = 0.0
        self.target_y = 0.0
        
    def set_mode(self, mode: CameraMode):
        """Change camera mode"""
        self.mode = mode
        
    def cycle_mode(self):
        """Cycle through available camera modes"""
        modes = list(CameraMode)
        current_index = modes.index(self.mode)
        next_index = (current_index + 1) % len(modes)
        self.mode = modes[next_index]
        
    def update(self, aircraft: Aircraft, dt: float):
        """Update camera position based on aircraft and current mode"""
        if self.mode == CameraMode.COCKPIT:
            self._update_cockpit_view(aircraft, dt)
        elif self.mode == CameraMode.CHASE:
            self._update_chase_view(aircraft, dt)
        elif self.mode == CameraMode.EXTERNAL:
            self._update_external_view(aircraft, dt)
        elif self.mode == CameraMode.TOP_DOWN:
            self._update_top_down_view(aircraft, dt)
        elif self.mode == CameraMode.SIDE:
            self._update_side_view(aircraft, dt)
            
    def _update_cockpit_view(self, aircraft: Aircraft, dt: float):
        """Update cockpit (first-person) view"""
        # Camera is at aircraft position with slight forward offset
        offset_distance = 20.0
        heading_rad = math.radians(aircraft.heading - 90)
        
        self.target_x = aircraft.x + offset_distance * math.cos(heading_rad)
        self.target_y = aircraft.y + offset_distance * math.sin(heading_rad)
        
        # Smooth camera movement (using dt for frame-independent movement)
        smooth_speed = self.smooth_factor * dt * 60  # Normalize for 60 FPS
        self.x += (self.target_x - self.x) * smooth_speed
        self.y += (self.target_y - self.y) * smooth_speed
        
        # Set zoom for cockpit view
        self.zoom = 2.0
        
    def _update_chase_view(self, aircraft: Aircraft, dt: float):
        """Update chase camera (third-person behind aircraft)"""
        # Position camera behind the aircraft
        heading_rad = math.radians(aircraft.heading - 90)
        
        # Calculate offset position behind aircraft
        offset_x = -self.chase_distance * math.cos(heading_rad)
        offset_y = -self.chase_distance * math.sin(heading_rad)
        
        self.target_x = aircraft.x + offset_x
        self.target_y = aircraft.y + offset_y
        
        # Smooth camera movement (using dt for frame-independent movement)
        smooth_speed = self.smooth_factor * dt * 60  # Normalize for 60 FPS
        self.x += (self.target_x - self.x) * smooth_speed
        self.y += (self.target_y - self.y) * smooth_speed
        
        # Adjust height based on aircraft altitude
        self.z = aircraft.altitude + self.chase_height
        
        # Set zoom for chase view
        self.zoom = 1.5
        
    def _update_external_view(self, aircraft: Aircraft, dt: float):
        """Update external view (orbiting around aircraft)"""
        # Slowly rotate around the aircraft
        self.external_angle += 30 * dt  # 30 degrees per second
        if self.external_angle >= 360:
            self.external_angle -= 360
            
        # Calculate camera position in orbit around aircraft
        angle_rad = math.radians(self.external_angle)
        self.target_x = aircraft.x + self.external_distance * math.cos(angle_rad)
        self.target_y = aircraft.y + self.external_distance * math.sin(angle_rad)
        
        # Smooth camera movement
        self.x += (self.target_x - self.x) * self.smooth_factor * 2  # Faster for external view
        self.y += (self.target_y - self.y) * self.smooth_factor * 2
        
        self.z = aircraft.altitude + self.external_height
        self.zoom = 1.0
        
    def _update_top_down_view(self, aircraft: Aircraft, dt: float):
        """Update top-down view"""
        self.target_x = aircraft.x
        self.target_y = aircraft.y
        
        # Smooth camera movement (using dt for frame-independent movement)
        smooth_speed = self.smooth_factor * dt * 60  # Normalize for 60 FPS
        self.x += (self.target_x - self.x) * smooth_speed
        self.y += (self.target_y - self.y) * smooth_speed
        
        # High altitude for top-down view
        self.z = aircraft.altitude + 500
        self.zoom = 0.5
        
    def _update_side_view(self, aircraft: Aircraft, dt: float):
        """Update side view"""
        # Position camera to the side of aircraft
        heading_rad = math.radians(aircraft.heading)
        side_offset = 150.0
        
        # 90 degrees offset for side view
        side_angle = heading_rad + math.pi / 2
        
        self.target_x = aircraft.x + side_offset * math.cos(side_angle)
        self.target_y = aircraft.y + side_offset * math.sin(side_angle)
        
        # Smooth camera movement (using dt for frame-independent movement)
        smooth_speed = self.smooth_factor * dt * 60  # Normalize for 60 FPS
        self.x += (self.target_x - self.x) * smooth_speed
        self.y += (self.target_y - self.y) * smooth_speed
        
        self.z = aircraft.altitude + 50
        self.zoom = 1.2
        
    def get_world_to_screen_transform(self) -> Tuple[float, float, float]:
        """Get transformation values for world-to-screen conversion"""
        return self.x, self.y, self.zoom
        
    def screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates"""
        world_x = ((screen_x - self.screen_width // 2) / self.zoom) + self.x
        world_y = ((screen_y - self.screen_height // 2) / self.zoom) + self.y
        return world_x, world_y
        
    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        screen_x = int((world_x - self.x) * self.zoom + self.screen_width // 2)
        screen_y = int((world_y - self.y) * self.zoom + self.screen_height // 2)
        return screen_x, screen_y
        
    def is_visible(self, world_x: float, world_y: float, margin: float = 100) -> bool:
        """Check if a world position is visible on screen"""
        screen_x, screen_y = self.world_to_screen(world_x, world_y)
        return (-margin <= screen_x <= self.screen_width + margin and 
                -margin <= screen_y <= self.screen_height + margin)
                
    def get_view_info(self, aircraft: Aircraft) -> dict:
        """Get information about the current view for HUD display"""
        info = {
            "mode": self.mode.value,
            "zoom": f"{self.zoom:.1f}x",
            "altitude": f"{self.z:.0f} ft"
        }
        
        if self.mode == CameraMode.CHASE:
            info["distance"] = f"{self.chase_distance:.0f} ft"
        elif self.mode == CameraMode.EXTERNAL:
            info["angle"] = f"{self.external_angle:.0f}°"
        elif self.mode == CameraMode.COCKPIT:
            # Calculate relative position to aircraft
            dx = aircraft.x - self.x
            dy = aircraft.y - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            info["offset"] = f"{distance:.0f} ft"
            
        return info
        
    def draw_camera_info(self, screen: pygame.Surface, aircraft: Aircraft):
        """Draw camera information on screen"""
        info = self.get_view_info(aircraft)
        
        # Create semi-transparent background
        info_surface = pygame.Surface((200, 100), pygame.SRCALPHA)
        info_surface.fill((0, 0, 0, 128))
        
        font = pygame.font.Font(None, 24)
        y_offset = 10
        
        for key, value in info.items():
            text = font.render(f"{key.title()}: {value}", True, (255, 255, 255))
            info_surface.blit(text, (10, y_offset))
            y_offset += 25
            
        # Position in top-right corner
        screen.blit(info_surface, (screen.get_width() - 210, 10))
        
    def set_zoom(self, zoom: float):
        """Set camera zoom level"""
        self.zoom = max(0.1, min(zoom, 5.0))  # Clamp between 0.1x and 5x
        
    def zoom_in(self, factor: float = 1.2):
        """Zoom in by a factor"""
        self.set_zoom(self.zoom * factor)
        
    def zoom_out(self, factor: float = 1.2):
        """Zoom out by a factor"""
        self.set_zoom(self.zoom / factor)
        
    def reset_external_angle(self):
        """Reset external camera angle to 0"""
        self.external_angle = 0.0