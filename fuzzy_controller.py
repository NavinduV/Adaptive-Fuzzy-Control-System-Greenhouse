import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Input variables
temperature = ctrl.Antecedent(np.arange(0, 51, 1), 'temperature')
humidity = ctrl.Antecedent(np.arange(0, 101, 1), 'humidity')

# Output variables
fan = ctrl.Consequent(np.arange(0, 101, 1), 'fan')
mist = ctrl.Consequent(np.arange(0, 101, 1), 'mist')

# Temperature membership functions
temperature['very_cold'] = fuzz.trapmf(temperature.universe, [0, 0, 5, 10])
temperature['cold'] = fuzz.trimf(temperature.universe, [5, 10, 20])
temperature['normal'] = fuzz.trimf(temperature.universe, [15, 25, 35])
temperature['warm'] = fuzz.trimf(temperature.universe, [30, 35, 40])
temperature['hot'] = fuzz.trapmf(temperature.universe, [35, 40, 50, 50])

# Humidity membership functions
humidity['very_dry'] = fuzz.trapmf(humidity.universe, [0, 0, 10, 20])
humidity['dry'] = fuzz.trimf(humidity.universe, [10, 30, 50])
humidity['normal'] = fuzz.trimf(humidity.universe, [40, 55, 70])
humidity['humid'] = fuzz.trimf(humidity.universe, [60, 75, 90])
humidity['very_humid'] = fuzz.trapmf(humidity.universe, [80, 90, 100, 100])

# Fan output
fan['low'] = fuzz.trimf(fan.universe, [0, 20, 40])
fan['medium'] = fuzz.trimf(fan.universe, [30, 50, 70])
fan['high'] = fuzz.trimf(fan.universe, [60, 80, 100])

# Mist output
mist['low'] = fuzz.trimf(mist.universe, [0, 20, 40])
mist['medium'] = fuzz.trimf(mist.universe, [30, 50, 70])
mist['high'] = fuzz.trimf(mist.universe, [60, 80, 100])

# Rules (simple subset for GUI)
rules = [
    ctrl.Rule(temperature['hot'], fan['high']),
    ctrl.Rule(temperature['normal'], fan['medium']),
    ctrl.Rule(temperature['cold'], fan['low']),

    ctrl.Rule(humidity['very_dry'], mist['high']),
    ctrl.Rule(humidity['normal'], mist['medium']),
    ctrl.Rule(humidity['very_humid'], mist['low'])
]

system = ctrl.ControlSystem(rules)
simulation = ctrl.ControlSystemSimulation(system)

def run_fuzzy(temp, hum):
    simulation.input['temperature'] = temp
    simulation.input['humidity'] = hum
    simulation.compute()

    return simulation.output['fan'], simulation.output['mist']
