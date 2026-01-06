import numpy as np

class GreenhouseEnv:
    def __init__(self):
        # State: [Temperature, Humidity]
        self.state = np.array([25.0, 60.0]) # Initial optimal-ish
        self.optimal_temp = 25.0
        self.optimal_hum = 70.0 # for cucumber/vegetative
        self.dt = 1 # Simulation time step

    def reset(self):
        # Random initialization
        t = np.random.uniform(10, 40)
        h = np.random.uniform(30, 90)
        self.state = np.array([t, h])
        return self.state

    def step(self, fan_power, mist_power):
        """
        fan_power: 0-100
        mist_power: 0-100
        """
        temp, hum = self.state
        
        # Physics approximation
        # External Environment (Assumed Hot & Dry for contrast)
        ext_temp = 35.0
        ext_hum = 40.0
        
        # Rate of change constants
        k_t_ext = 0.05  # Heat gain from outside
        k_h_ext = 0.05  # Moisture loss/gain from outside
        
        k_fan_t = 0.15   # Cooling effect of fan
        k_fan_h = 0.1   # Humidity removal of fan
        
        k_mist_t = 0.05  # Cooling effect of mist
        k_mist_h = 0.2   # Humidification
        
        # Calculate deltas
        # Temp changes: Moves towards external + Fan cools + Mist cools
        dt_dt = k_t_ext * (ext_temp - temp) - k_fan_t * (fan_power / 100.0 * 10) - k_mist_t * (mist_power / 100.0 * 5)
        
        # Humidity changes: Moves towards external - Fan dries + Mist wets
        dh_dt = k_h_ext * (ext_hum - hum) - k_fan_h * (fan_power / 100.0 * 10) + k_mist_h * (mist_power / 100.0 * 20)
        
        # Update state with noise
        temp += dt_dt + np.random.normal(0, 0.1)
        hum += dh_dt + np.random.normal(0, 0.1)
        
        # Clamp values
        temp = np.clip(temp, 0, 50)
        hum = np.clip(hum, 0, 100)
        self.state = np.array([temp, hum])
        
        # Calculate Reward
        # Negative distance from optimal
        err_t = abs(temp - self.optimal_temp)
        err_h = abs(hum - self.optimal_hum)
        
        # Reward: Higher is better. Max reward 0 (perfect).
        reward = -(err_t + err_h * 0.5) 
        
        done = False # Continuous task usually, but we can set limits if needed
        return self.state, reward, done, {}
