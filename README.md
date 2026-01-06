# Greenhouse Fuzzy Control System

A fuzzy logic based control system for a smart greenhouse.

## Features
- **Mamdani Controller**: Standard fuzzy logic inference for smooth control.
- **Sugeno Controller**: Optimized fuzzy control for precise output.
- **Interactive GUI**: Visualize membership functions and control surfaces.
- **Adaptive Logic**: Self-tuning parameters based on feedback.

## Setup
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Run the application:
   ```
   python main.py
   ```

## File Structure
- `main.py`: Entry point.
- `gui.py`: Graphical User Interface.
- `mamdani_controller.py`: Mamdani fuzzy logic implementation.
- `sugeno_controller.py`: Sugeno fuzzy logic implementation.
- `plots.py`: Matplotlib plotting utilities.
- `simulation.py`: Simulation logical loop.
- `adaptive_logic.py`: Adaptive parameter tuning.
