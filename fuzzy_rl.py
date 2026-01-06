import numpy as np
import pickle
import os
from skfuzzy import control as ctrl

class FuzzyRLAgent:
    def __init__(self, sugeno_controller):
        self.controller = sugeno_controller
        # Extract Fuzzy Sets for state discretization
        self.temp_mf = self.controller.temperature
        self.hum_mf = self.controller.humidity
        self.fan_out = self.controller.fan
        self.mist_out = self.controller.mist
        
        # Define State Space (Indices of MFs)
        self.temp_labels = ['very_cold', 'cold', 'normal', 'warm', 'hot']
        self.hum_labels = ['very_dry', 'dry', 'normal', 'humid', 'very_humid']
        
        # Define Action Space 
        # (Fan Level Index, Mist Level Index) -> 0=Low, 1=Medium, 2=High
        # Actually in Sugeno check definitions:
        # Fan: low, medium, high
        # Mist: low, medium, high
        self.output_labels = ['low', 'medium', 'high']
        
        # Q-Table: [Temp_State, Hum_State, Fan_Action, Mist_Action]
        # Dimensions: 5 x 5 x 3 x 3
        self.q_table_file = 'q_table.pkl'
        self.load_q_table()
        
        # Hyperparameters
        self.alpha = 0.1  # Learning Rate
        self.gamma = 0.9  # Discount Factor
        self.epsilon = 1.0 # Exploration Rate
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01

    def load_q_table(self):
        if os.path.exists(self.q_table_file):
            with open(self.q_table_file, 'rb') as f:
                self.q_table = pickle.load(f)
        else:
            self.q_table = np.zeros((5, 5, 3, 3))

    def save_q_table(self):
        with open(self.q_table_file, 'wb') as f:
            pickle.dump(self.q_table, f)

    def get_state(self, temp, hum):
        # Discretize continuous input into fuzzy state based on max membership
        # Ideally we compute membership for each and take argmax
        t_mfs = [fuzz.interp_membership(self.temp_mf.universe, self.controller.temperature[label].mf, temp) for label in self.temp_labels]
        h_mfs = [fuzz.interp_membership(self.hum_mf.universe, self.controller.humidity[label].mf, hum) for label in self.hum_labels]
        
        t_idx = np.argmax(t_mfs)
        h_idx = np.argmax(h_mfs)
        return t_idx, h_idx

    def choose_action(self, t_idx, h_idx):
        if np.random.random() < self.epsilon:
            fan_idx = np.random.randint(0, 3)
            mist_idx = np.random.randint(0, 3)
        else:
            # Flatten the action space for argmax retrieval
            # We want indices (fan, mist) with max Q
            best_action_flat = np.argmax(self.q_table[t_idx, h_idx])
            fan_idx = best_action_flat // 3
            mist_idx = best_action_flat % 3
        return fan_idx, mist_idx

    def update(self, state, action, reward, next_state):
        t_idx, h_idx = state
        fan_idx, mist_idx = action
        nt_idx, nh_idx = next_state
        
        best_next_q = np.max(self.q_table[nt_idx, nh_idx])
        current_q = self.q_table[t_idx, h_idx, fan_idx, mist_idx]
        
        new_q = current_q + self.alpha * (reward + self.gamma * best_next_q - current_q)
        self.q_table[t_idx, h_idx, fan_idx, mist_idx] = new_q

    def train(self, env, episodes=1000):
        print(f"Starting training for {episodes} episodes...")
        for ep in range(episodes):
            state_vals = env.reset()
            t_idx, h_idx = self.get_state(state_vals[0], state_vals[1])
            
            for _ in range(50): # Steps per episode
                fan_idx, mist_idx = self.choose_action(t_idx, h_idx)
                
                # Convert action indices to control values (for environment)
                # Low=20, Medium=50, High=80 approx
                fan_pwm = [20, 50, 80][fan_idx]
                mist_pwm = [20, 50, 80][mist_idx]
                
                next_vals, reward, _, _ = env.step(fan_pwm, mist_pwm)
                nt_idx, nh_idx = self.get_state(next_vals[0], next_vals[1])
                
                self.update((t_idx, h_idx), (fan_idx, mist_idx), reward, (nt_idx, nh_idx))
                
                t_idx, h_idx = nt_idx, nh_idx
            
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay
                
            if (ep+1) % 100 == 0:
                print(f"Episode {ep+1}: Epsilon={self.epsilon:.2f}")
        
        self.save_q_table()
        print("Training complete. Q-Table saved.")

    def evolve_rules(self):
        """Generates a new rule set for the Sugeno controller based on the learned Q-Table."""
        new_rules = []
        print("Evolving rules based on learned policy...")
        
        for t_idx, t_label in enumerate(self.temp_labels):
            for h_idx, h_label in enumerate(self.hum_labels):
                # Find best action for this fuzzy state
                best_action_flat = np.argmax(self.q_table[t_idx, h_idx])
                fan_idx = best_action_flat // 3
                mist_idx = best_action_flat % 3
                
                fan_label = self.output_labels[fan_idx]
                mist_label = self.output_labels[mist_idx]
                
                # Create Rule: IF temp IS t_label AND hum IS h_label THEN fan IS fan_label, mist IS mist_label
                # Note: skfuzzy ControlSystem usually takes 1 consequent per rule or multiple ANDed.
                # It's cleaner to create separate rules or compound consequents.
                # Sugeno in skfuzzy is usually 1 output. 
                # We will create 1 rule that maps Antecedents to Consequents.
                
                rule = ctrl.Rule(
                    self.controller.temperature[t_label] & self.controller.humidity[h_label],
                    (self.controller.fan[fan_label], self.controller.mist[mist_label])
                )
                new_rules.append(rule)
        
        self.controller.update_rules(new_rules)
        print("Fuzzy Rules Evolved!")

# Helper needed for skfuzzy interp_membership
import skfuzzy as fuzz
