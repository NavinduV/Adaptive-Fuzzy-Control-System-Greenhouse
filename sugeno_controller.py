import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class SugenoController:
    def __init__(self):
        # Input variables
        self.temperature = ctrl.Antecedent(np.arange(0, 51, 1), 'temperature')
        self.humidity = ctrl.Antecedent(np.arange(0, 101, 1), 'humidity')

        # Output variables (simulated Sugeno with singleton-like MFs)
        self.fan = ctrl.Consequent(np.arange(0, 101, 1), 'fan')
        self.mist = ctrl.Consequent(np.arange(0, 101, 1), 'mist')

        # Membership functions for Temperature (Same as Mamdani for inputs usually)
        self.temperature['very_cold'] = fuzz.trapmf(self.temperature.universe, [0, 0, 5, 10])
        self.temperature['cold'] = fuzz.trimf(self.temperature.universe, [5, 10, 20])
        self.temperature['normal'] = fuzz.trimf(self.temperature.universe, [15, 25, 35])
        self.temperature['warm'] = fuzz.trimf(self.temperature.universe, [30, 35, 40])
        self.temperature['hot'] = fuzz.trapmf(self.temperature.universe, [35, 40, 50, 50])

        # Membership functions for Humidity
        self.humidity['very_dry'] = fuzz.trapmf(self.humidity.universe, [0, 0, 10, 20])
        self.humidity['dry'] = fuzz.trimf(self.humidity.universe, [10, 30, 50])
        self.humidity['normal'] = fuzz.trimf(self.humidity.universe, [40, 55, 70])
        self.humidity['humid'] = fuzz.trimf(self.humidity.universe, [60, 75, 90])
        self.humidity['very_humid'] = fuzz.trapmf(self.humidity.universe, [80, 90, 100, 100])

        # Constant Outputs (Singletons approximation)
        # Low: 20, Medium: 50, High: 80
        self.fan['low'] = fuzz.trimf(self.fan.universe, [19, 20, 21])
        self.fan['medium'] = fuzz.trimf(self.fan.universe, [49, 50, 51])
        self.fan['high'] = fuzz.trimf(self.fan.universe, [79, 80, 81])

        self.mist['low'] = fuzz.trimf(self.mist.universe, [19, 20, 21])
        self.mist['medium'] = fuzz.trimf(self.mist.universe, [49, 50, 51])
        self.mist['high'] = fuzz.trimf(self.mist.universe, [79, 80, 81])

        # Rules
        self.rules = []
        self._create_default_rules()

        self.system = None
        self.simulation = None
        self._build_simulation()

    def _create_default_rules(self):
        self.rules = [
            ctrl.Rule(self.temperature['hot'], self.fan['high']),
            ctrl.Rule(self.temperature['warm'], self.fan['medium']),
            ctrl.Rule(self.temperature['normal'], self.fan['low']),
            ctrl.Rule(self.temperature['cold'], self.fan['low']),
            
            ctrl.Rule(self.humidity['very_dry'], self.mist['high']),
            ctrl.Rule(self.humidity['dry'], self.mist['medium']),
            ctrl.Rule(self.humidity['normal'], self.mist['low']),
            ctrl.Rule(self.humidity['humid'], self.mist['low']),
            ctrl.Rule(self.humidity['very_humid'], self.mist['low']),
        ]

    def _build_simulation(self):
        if self.rules:
            self.system = ctrl.ControlSystem(self.rules)
            self.simulation = ctrl.ControlSystemSimulation(self.system)
        else:
            self.simulation = None

    def update_rules(self, new_rules):
        """Replaces current rules with new ones."""
        self.rules = new_rules
        self._build_simulation()

    def compute(self, temp_input, hum_input):
        if not self.simulation:
            # Fallback if no rules
            return 0.0, 0.0
            
        self.simulation.input['temperature'] = temp_input
        self.simulation.input['humidity'] = hum_input
        try:
            self.simulation.compute()
            return self.simulation.output['fan'], self.simulation.output['mist']
        except:
             return 0.0, 0.0
    
    def get_variables(self):
        return self.temperature, self.humidity, self.fan, self.mist
