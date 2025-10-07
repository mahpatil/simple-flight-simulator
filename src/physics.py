"""
Flight physics and control system for the flight simulator.
Handles realistic aircraft movement, controls, and flight mechanics.
"""

import pygame
import math
from enum import Enum
from aircraft import Aircraft
from airports import Airport

class FlightPhase(Enum):
    """Current phase of flight"""
    GROUND = "Ground"
    TAKEOFF = "Takeoff"
    CLIMB = "Climb"
    CRUISE = "Cruise"
    DESCENT = "Descent"
    APPROACH = "Approach"
    LANDING = "Landing"

class FlightControls:
    """Manages flight controls and input handling"""
    
    def __init__(self):
        # Control inputs (-1.0 to +1.0)
        self.pitch_input = 0.0      # W/S keys - nose up/down
        self.yaw_input = 0.0        # A/D keys - nose left/right
        self.roll_input = 0.0       # Q/E keys - bank left/right
        self.throttle_input = 0.0   # R/F keys - power up/down
        
        # Control states
        self.gear_toggle = False
        self.autopilot = False
        self.brakes = False
        
        # Input sensitivity
        self.pitch_sensitivity = 1.0
        self.yaw_sensitivity = 1.0
        self.roll_sensitivity = 1.0
        self.throttle_sensitivity = 0.5
        
    def update_from_keyboard(self, keys):
        """Update controls based on keyboard input"""
        # Pitch controls (W/S)
        if keys[pygame.K_w]:
            self.pitch_input = min(1.0, self.pitch_input + 0.02)
        elif keys[pygame.K_s]:
            self.pitch_input = max(-1.0, self.pitch_input - 0.02)
        else:
            self.pitch_input *= 0.95  # Gradual return to center
            
        # Yaw controls (A/D)
        if keys[pygame.K_a]:
            self.yaw_input = min(1.0, self.yaw_input + 0.02)
        elif keys[pygame.K_d]:
            self.yaw_input = max(-1.0, self.yaw_input - 0.02)
        else:
            self.yaw_input *= 0.95  # Gradual return to center
            
        # Roll controls (Q/E)
        if keys[pygame.K_q]:
            self.roll_input = min(1.0, self.roll_input + 0.02)
        elif keys[pygame.K_e]:
            self.roll_input = max(-1.0, self.roll_input - 0.02)
        else:
            self.roll_input *= 0.95  # Gradual return to center
            
        # Throttle controls (R/F)
        if keys[pygame.K_r]:
            self.throttle_input = min(1.0, self.throttle_input + 0.02)  # Faster throttle response
        elif keys[pygame.K_f]:
            self.throttle_input = max(0.0, self.throttle_input - 0.02)
            
        # Brakes (Shift)
        self.brakes = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
    def handle_key_press(self, key):
        """Handle discrete key press events"""
        if key == pygame.K_SPACE:
            self.gear_toggle = not self.gear_toggle
        elif key == pygame.K_p:
            self.autopilot = not self.autopilot
        elif key == pygame.K_g:
            # Emergency gear toggle
            self.gear_toggle = not self.gear_toggle

class FlightPhysics:
    """Handles realistic flight physics simulation"""
    
    def __init__(self):
        self.phase = FlightPhase.GROUND
        self.ground_elevation = 0.0
        self.wind_speed = 0.0
        self.wind_direction = 0.0
        self.turbulence = 0.0
        
        # Physics constants
        self.gravity = 32.2  # ft/s²
        self.air_density_sea_level = 0.002378  # slug/ft³
        
    def update_aircraft_physics(self, aircraft: Aircraft, controls: FlightControls, dt: float):
        """Update aircraft state based on physics and controls"""
        # Update engine state
        aircraft.engine_on = controls.throttle_input > 0.05
        
        # Update throttle
        aircraft.throttle = controls.throttle_input * 100
        
        # Update landing gear
        aircraft.gear_down = controls.gear_toggle
        
        # Calculate air density based on altitude
        air_density = self._calculate_air_density(aircraft.altitude)
        
        # Update flight controls
        self._update_flight_controls(aircraft, controls, air_density, dt)
        
        # Update flight phase
        self._update_flight_phase(aircraft)
        
        # Apply physics
        self._apply_aerodynamics(aircraft, air_density, dt)
        self._apply_engine_thrust(aircraft, air_density, dt)
        self._apply_gravity_and_lift(aircraft, air_density, dt)
        
        # Update position and consume fuel
        aircraft.update_position(dt)
        aircraft.update_altitude(dt)
        aircraft.update_fuel(dt)
        
        # Ground collision detection
        self._handle_ground_collision(aircraft)
        
    def _calculate_air_density(self, altitude: float) -> float:
        """Calculate air density based on altitude"""
        # Simplified atmosphere model
        if altitude < 36000:  # Troposphere
            temperature_ratio = 1 - 0.0065 * altitude / 288.15
            return self.air_density_sea_level * (temperature_ratio ** 4.256)
        else:  # Stratosphere (simplified)
            return self.air_density_sea_level * 0.297
            
    def _update_flight_controls(self, aircraft: Aircraft, controls: FlightControls, 
                               air_density: float, dt: float):
        """Update aircraft attitude based on control inputs"""
        # Allow basic controls even at low speeds, but reduce effectiveness
        if aircraft.specs.stall_speed > 0:
            speed_ratio = aircraft.speed / aircraft.specs.stall_speed
            control_effectiveness = max(0.3, min(1.0, speed_ratio))  # Minimum 30% effectiveness
        else:
            control_effectiveness = 1.0
        
        # Ground controls - allow steering even when stationary for taxi
        ground_control_effectiveness = 1.0 if aircraft.altitude < 10 else control_effectiveness
        
        # Pitch control
        pitch_rate = controls.pitch_input * controls.pitch_sensitivity * control_effectiveness
        max_pitch_rate = 10.0  # degrees per second
        aircraft.pitch += pitch_rate * max_pitch_rate * dt
        aircraft.pitch = max(-30, min(30, aircraft.pitch))  # Limit pitch
        
        # Yaw control (affects heading)
        # Use ground controls when on ground, air controls when flying
        yaw_effectiveness = ground_control_effectiveness if aircraft.altitude < 10 else control_effectiveness
        yaw_rate = controls.yaw_input * controls.yaw_sensitivity * yaw_effectiveness
        max_yaw_rate = aircraft.specs.turn_rate if aircraft.altitude >= 10 else 30.0  # Faster turning on ground
        aircraft.heading += yaw_rate * max_yaw_rate * dt
        aircraft.heading = aircraft.heading % 360  # Wrap around
        
        # Roll control
        roll_rate = controls.roll_input * controls.roll_sensitivity * control_effectiveness
        max_roll_rate = 20.0  # degrees per second
        aircraft.roll += roll_rate * max_roll_rate * dt
        aircraft.roll = max(-45, min(45, aircraft.roll))  # Limit roll
        
        # Roll affects turn rate
        if abs(aircraft.roll) > 5:
            turn_rate = (aircraft.roll / 45.0) * aircraft.specs.turn_rate * 0.5
            aircraft.heading += turn_rate * dt
            aircraft.heading = aircraft.heading % 360
            
    def _update_flight_phase(self, aircraft: Aircraft):
        """Update current flight phase based on aircraft state"""
        if aircraft.altitude < 5:
            if aircraft.speed < 10:
                self.phase = FlightPhase.GROUND
            elif aircraft.speed < aircraft.specs.stall_speed:
                self.phase = FlightPhase.TAKEOFF
        elif aircraft.altitude < 1000:
            if aircraft.pitch > 5:
                self.phase = FlightPhase.CLIMB
            elif aircraft.pitch < -5:
                self.phase = FlightPhase.APPROACH
            else:
                self.phase = FlightPhase.CLIMB
        elif aircraft.altitude > 10000:
            if abs(aircraft.pitch) < 3:
                self.phase = FlightPhase.CRUISE
            elif aircraft.pitch > 3:
                self.phase = FlightPhase.CLIMB
            else:
                self.phase = FlightPhase.DESCENT
        else:
            if aircraft.pitch > 3:
                self.phase = FlightPhase.CLIMB
            elif aircraft.pitch < -3:
                self.phase = FlightPhase.DESCENT
            else:
                self.phase = FlightPhase.CRUISE
                
    def _apply_aerodynamics(self, aircraft: Aircraft, air_density: float, dt: float):
        """Apply aerodynamic forces"""
        # Drag force reduces speed
        if aircraft.speed > 0:
            # Simplified drag calculation
            drag_coefficient = 0.02 + (0.001 * abs(aircraft.pitch))  # Increased drag at high pitch
            drag_force = 0.5 * air_density * (aircraft.speed ** 2) * drag_coefficient
            speed_reduction = drag_force * dt * 0.1  # Simplified
            aircraft.speed = max(0, aircraft.speed - speed_reduction)
            
        # Stall conditions
        if aircraft.speed < aircraft.specs.stall_speed and aircraft.altitude > 0:
            # Stall - rapid altitude loss
            stall_sink_rate = (aircraft.specs.stall_speed - aircraft.speed) * 10
            aircraft.altitude -= stall_sink_rate * dt
            aircraft.pitch -= 20 * dt  # Nose drops in stall
            
    def _apply_engine_thrust(self, aircraft: Aircraft, air_density: float, dt: float):
        """Apply engine thrust"""
        if aircraft.engine_on and aircraft.fuel > 0:
            # Thrust decreases with altitude
            altitude_factor = air_density / self.air_density_sea_level
            max_thrust_speed = aircraft.specs.max_speed * altitude_factor
            
            # Thrust based on throttle setting
            thrust_factor = (aircraft.throttle / 100.0) * altitude_factor
            target_speed = max_thrust_speed * thrust_factor
            
            # Improved acceleration - better at low speeds
            speed_diff = target_speed - aircraft.speed
            
            # Base acceleration that works well from zero speed
            base_acceleration = 50.0 * (aircraft.throttle / 100.0)  # knots per second
            
            # Additional acceleration based on speed difference
            differential_acceleration = speed_diff * 1.0 * dt
            
            total_acceleration = (base_acceleration + differential_acceleration) * dt
            aircraft.speed += total_acceleration
            
            # Ensure we don't exceed target speed too much
            if aircraft.speed > target_speed:
                aircraft.speed = target_speed
            
    def _apply_gravity_and_lift(self, aircraft: Aircraft, air_density: float, dt: float):
        """Apply gravity and lift forces"""
        if aircraft.altitude > 0:
            # Lift depends on speed and angle of attack
            if aircraft.speed >= aircraft.specs.stall_speed:
                # Generate lift
                lift_factor = (aircraft.speed / aircraft.specs.cruise_speed) ** 2
                lift_factor *= air_density / self.air_density_sea_level
                
                # Pitch affects vertical speed
                climb_rate = aircraft.pitch * lift_factor * 20  # ft/min
                aircraft.altitude += (climb_rate / 60) * dt  # Convert to ft/s
            else:
                # Insufficient lift - gravity wins
                sink_rate = 500 * (1 - aircraft.speed / aircraft.specs.stall_speed)  # ft/min
                aircraft.altitude -= (sink_rate / 60) * dt
                
    def _handle_ground_collision(self, aircraft: Aircraft):
        """Handle aircraft interaction with ground"""
        if aircraft.altitude <= self.ground_elevation:
            aircraft.altitude = self.ground_elevation
            
            # Landing/crash logic
            if aircraft.speed > 80 or abs(aircraft.pitch) > 10:
                # Hard landing or crash
                aircraft.speed *= 0.8  # Reduce speed
                aircraft.pitch = 0
                aircraft.roll = 0
            elif aircraft.speed > 40:
                # Normal landing rollout
                aircraft.speed *= 0.95  # Gradual deceleration
                aircraft.pitch = 0
                aircraft.roll = 0
            else:
                # Stopped on ground
                if aircraft.throttle < 10:
                    aircraft.speed = max(0, aircraft.speed - 20 * 0.016)  # Friction
                    
    def get_flight_info(self, aircraft: Aircraft) -> dict:
        """Get flight information for display"""
        return {
            "phase": self.phase.value,
            "vertical_speed": aircraft.pitch * (aircraft.speed / aircraft.specs.cruise_speed) * 1000 if aircraft.specs.cruise_speed > 0 else 0,
            "ground_speed": aircraft.speed,
            "true_airspeed": aircraft.speed,  # Simplified
            "mach_number": aircraft.speed / 661.5 if aircraft.altitude > 30000 else 0,  # Simplified
            "angle_of_attack": aircraft.pitch,
            "bank_angle": aircraft.roll
        }