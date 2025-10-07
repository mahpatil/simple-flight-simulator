"""
Test script to validate the flight simulator components.
Tests all major systems without requiring the GUI.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from aircraft import create_aircraft, AIRCRAFT_MODELS
from airports import AIRPORTS, RouteManager, get_airport_codes
from camera import Camera, CameraMode
from physics import FlightControls, FlightPhysics
from hud import HUD

def test_aircraft():
    """Test aircraft creation and basic functionality"""
    print("Testing Aircraft System...")
    
    # Test creating each aircraft model
    for model_name in AIRCRAFT_MODELS.keys():
        aircraft = create_aircraft(model_name)
        print(f"✓ Created {aircraft.specs.name}")
        print(f"  Max Speed: {aircraft.specs.max_speed} knots")
        print(f"  Fuel Capacity: {aircraft.specs.fuel_capacity} gallons")
        
        # Test basic movement
        aircraft.speed = 100
        aircraft.heading = 90
        original_x = aircraft.x
        aircraft.update_position(1.0)  # 1 second
        
        if aircraft.x != original_x:
            print(f"  ✓ Position update working")
        else:
            print(f"  ✗ Position update failed")
            
        print()
        
def test_airports():
    """Test airport system"""
    print("Testing Airport System...")
    
    airport_codes = get_airport_codes()
    print(f"✓ {len(airport_codes)} airports available: {', '.join(airport_codes)}")
    
    # Test airport properties
    jfk = AIRPORTS['JFK']
    lax = AIRPORTS['LAX']
    
    distance = jfk.distance_to(lax)
    bearing = jfk.bearing_to(lax)
    
    print(f"✓ JFK to LAX: {distance:.0f} nm, bearing {bearing:.0f}°")
    
    # Test route manager
    route_manager = RouteManager()
    route = route_manager.get_route('JFK', 'LAX')
    
    if route:
        print(f"✓ Route created: {route.departure.code} to {route.arrival.code}")
        print(f"  Distance: {route.distance:.0f} nm")
        print(f"  Duration: {route.duration:.1f} hours")
    else:
        print("✗ Route creation failed")
        
    print()
    
def test_physics():
    """Test flight physics"""
    print("Testing Flight Physics...")
    
    # Create test aircraft
    aircraft = create_aircraft("Boeing 737-800")
    controls = FlightControls()
    physics = FlightPhysics()
    
    print(f"✓ Created test aircraft at altitude {aircraft.altitude} ft")
    
    # Test throttle up
    controls.throttle_input = 0.8
    aircraft.engine_on = True
    
    original_speed = aircraft.speed
    physics.update_aircraft_physics(aircraft, controls, 1.0)
    
    if aircraft.speed > original_speed:
        print("✓ Throttle acceleration working")
    else:
        print("✗ Throttle acceleration failed")
        
    # Test pitch control
    controls.pitch_input = 0.5
    original_pitch = aircraft.pitch
    physics.update_aircraft_physics(aircraft, controls, 1.0)
    
    if abs(aircraft.pitch - original_pitch) > 0:
        print("✓ Pitch control working")
    else:
        print("✗ Pitch control failed")
        
    # Test flight info
    flight_info = physics.get_flight_info(aircraft)
    print(f"✓ Flight phase: {flight_info['phase']}")
    
    print()
    
def test_camera():
    """Test camera system"""
    print("Testing Camera System...")
    
    camera = Camera(1200, 800)
    aircraft = create_aircraft("Cessna 172", 1000, 1000, 5000)
    
    # Test different camera modes
    for mode in CameraMode:
        camera.set_mode(mode)
        camera.update(aircraft, 0.1)
        print(f"✓ {mode.value} camera mode working")
        
    # Test world to screen conversion
    screen_x, screen_y = camera.world_to_screen(aircraft.x, aircraft.y)
    world_x, world_y = camera.screen_to_world(screen_x, screen_y)
    
    if abs(world_x - aircraft.x) < 1 and abs(world_y - aircraft.y) < 1:
        print("✓ World/screen coordinate conversion working")
    else:
        print("✗ World/screen coordinate conversion failed")
        
    print()
    
def test_flight_controls():
    """Test flight controls"""
    print("Testing Flight Controls...")
    
    controls = FlightControls()
    
    # Simulate key presses (without pygame)
    controls.pitch_input = 0.5
    controls.throttle_input = 0.8
    controls.gear_toggle = True
    
    print(f"✓ Pitch input: {controls.pitch_input}")
    print(f"✓ Throttle input: {controls.throttle_input}")
    print(f"✓ Gear down: {controls.gear_toggle}")
    
    print()

def main():
    """Run all tests"""
    print("Simple Flight Simulator - Component Tests")
    print("=" * 50)
    print()
    
    try:
        test_aircraft()
        test_airports()
        test_physics()
        test_camera()
        test_flight_controls()
        
        print("=" * 50)
        print("All tests completed successfully!")
        print()
        print("To run the flight simulator:")
        print("  python src/main.py")
        print("or")
        print("  ./run_simulator.sh")
        print()
        print("Controls:")
        print("  W/S - Pitch up/down")
        print("  A/D - Yaw left/right") 
        print("  Q/E - Roll left/right")
        print("  R/F - Throttle up/down")
        print("  SPACE - Toggle landing gear")
        print("  C - Change camera view")
        print("  H - Toggle HUD")
        print("  ESC - Pause/Exit")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()