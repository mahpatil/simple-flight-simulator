# Simple Flight Simulator

A Python-based flight simulator with multiple aircraft and airports, featuring different camera views.

## Features
- 5 different commercial aircraft models with detailed visuals
- Realistic aircraft appearance with wings, fuselage, engines, and landing gear
- 5 international airports  
- Front and back view cameras
- Realistic flight physics
- Interactive GUI

## Requirements
- Python 3.8+
- pygame
- numpy

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python src/main.py

python controls_test.py
```

To test the improved aircraft visuals:
```bash
python aircraft_visual_test.py
```

## Controls
- W/S: Pitch up/down
- A/D: Yaw left/right  
- Q/E: Roll left/right
- R/F: Increase/decrease throttle
- Space: Toggle landing gear
- C: Change camera view
- ESC: Exit

## Aircraft Models
- Boeing 737-800
- Airbus A320
- Boeing 777-300ER
- Cessna 172
- Embraer E190

## Airports
- JFK (New York)
- LAX (Los Angeles)
- LHR (London Heathrow)
- CDG (Paris Charles de Gaulle)
- NRT (Tokyo Narita)