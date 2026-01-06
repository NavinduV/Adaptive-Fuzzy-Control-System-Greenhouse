import sys
import tkinter as tk
from gui import GreenhouseControlGUI
from simulation import run_full_simulation
from adaptive_logic import AdaptiveLogic
from fuzzy_rl import FuzzyRLAgent
from rl_env import GreenhouseEnv
from sugeno_controller import SugenoController

def print_menu():
    print("\n==================================================")
    print("Greenhouse Fuzzy Control System")
    print("1. View Rules")
    print("2. Run Simulation Loop")
    print("3. Analyze Mamdani Controller")
    print("4. Analyze Sugeno Controller")
    print("5. Train RL Agent & Evolve Rules (NEW)")
    print("7. Test Adaptive Parameters")
    print("8. Launch GUI")
    print("9. Exit")
    print("--------------------------------------------------")

def main():
    adaptive = AdaptiveLogic()
    
    while True:
        print_menu()
        choice = input("Enter choice (1-9): ")
        
        if choice == '1':
            print("Displaying rules... (Placeholder)")
        elif choice == '2':
             print("--------------------------------------------------")
             run_full_simulation()
        elif choice == '5':
             print("Initializing RL Training...")
             env = GreenhouseEnv()
             sugeno = SugenoController()
             agent = FuzzyRLAgent(sugeno)
             
             episodes = input("Enter number of episodes (default 200): ")
             if not episodes.isdigit(): episodes = 200
             else: episodes = int(episodes)
             
             agent.train(env, episodes=episodes)
             agent.evolve_rules()
             
             print("Rules updated in memory. Launch GUI to test new rules.")
        elif choice == '7':
             print("Testing Adaptive Parameters...")
             adaptive.adjust_parameters("High Humidity detected")
        elif choice == '8':
            print("Launching GUI...")
            root = tk.Tk()
            app = GreenhouseControlGUI(root)
            root.mainloop()
        elif choice == '9':
            print("Exiting...")
            sys.exit()
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
