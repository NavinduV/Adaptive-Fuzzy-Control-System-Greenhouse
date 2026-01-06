import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mamdani_controller import MamdaniController
from sugeno_controller import SugenoController
from plots import PlotManager

# Plant Optimal Conditions Database
PLANT_DATA = {
    "cucumber": {
        "Vegetative": {"temp": 25.0, "hum": 75.0},
        "Flowering": {"temp": 24.0, "hum": 70.0},
        "Fruiting": {"temp": 26.0, "hum": 80.0}
    },
    "tomato": {
        "Vegetative": {"temp": 22.0, "hum": 65.0},
        "Flowering": {"temp": 23.0, "hum": 60.0},
        "Fruiting": {"temp": 24.0, "hum": 70.0}
    }
}

class GreenhouseControlGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Greenhouse Fuzzy Control System 🌱")
        self.root.geometry("1280x850")
        self.root.minsize(1100, 750)
        self.root.configure(bg="#f0f0f0") # Standard light gray or use #e3f2fd as in snippet

        # Controllers
        self.mamdani = MamdaniController()
        self.sugeno = SugenoController()
        self.current_controller = self.mamdani
        self.controller_name = "Mamdani"

        # State variables
        self.temp_var = tk.DoubleVar(value=25.0)
        self.hum_var = tk.DoubleVar(value=60.0)
        self.fan_output = tk.DoubleVar(value=0.0)
        self.mist_output = tk.DoubleVar(value=0.0)
        
        self.species_var = tk.StringVar(value="cucumber")
        self.stage_var = tk.StringVar(value="Vegetative")
        
        self.controller_type_var = tk.StringVar(value="Mamdani")

        # Layout
        self.setup_ui()
        
    def setup_ui(self):
        # Main container with 2 columns
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Panel (Control Panel)
        left_panel = tk.Frame(main_frame, bg="#f0f0f0", width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # Right Panel (Visualization)
        right_panel = tk.Frame(main_frame, bg="white", relief=tk.SUNKEN, bd=1)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Left Panel Content ---
        tk.Label(left_panel, text="Control Panel", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(anchor="w", pady=(0, 10))

        # 1. Controller Type
        ctrl_frame = tk.LabelFrame(left_panel, text="Controller Type", bg="#f0f0f0", padx=10, pady=10)
        ctrl_frame.pack(fill=tk.X, pady=5)
        
        tk.Radiobutton(ctrl_frame, text="Mamdani", variable=self.controller_type_var, value="Mamdani", command=self.update_controller_mode, bg="#f0f0f0").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(ctrl_frame, text="Sugeno", variable=self.controller_type_var, value="Sugeno", command=self.update_controller_mode, bg="#f0f0f0").pack(side=tk.LEFT, padx=10)

        # 2. Plant Settings
        plant_frame = tk.LabelFrame(left_panel, text="Plant Settings", bg="#f0f0f0", padx=10, pady=10)
        plant_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(plant_frame, text="Species:", bg="#f0f0f0").grid(row=0, column=0, sticky="w", pady=2)
        species_cb = ttk.Combobox(plant_frame, textvariable=self.species_var, values=list(PLANT_DATA.keys()), state="readonly")
        species_cb.grid(row=0, column=1, sticky="ew", pady=2)
        species_cb.bind("<<ComboboxSelected>>", self.update_optimal_display)

        tk.Label(plant_frame, text="Growth Stage:", bg="#f0f0f0").grid(row=1, column=0, sticky="w", pady=2)
        stage_cb = ttk.Combobox(plant_frame, textvariable=self.stage_var, values=["Vegetative", "Flowering", "Fruiting"], state="readonly")
        stage_cb.grid(row=1, column=1, sticky="ew", pady=2)
        stage_cb.bind("<<ComboboxSelected>>", self.update_optimal_display)

        # 3. Temperature Input
        temp_frame = tk.LabelFrame(left_panel, text="Temperature (°C)", bg="#f0f0f0", padx=10, pady=10)
        temp_frame.pack(fill=tk.X, pady=5)
        
        self.temp_slider = tk.Scale(temp_frame, from_=0, to=50, orient=tk.HORIZONTAL, variable=self.temp_var, bg="#f0f0f0", highlightthickness=0)
        self.temp_slider.pack(fill=tk.X)
        self.temp_value_label = tk.Label(temp_frame, textvariable=self.temp_var, font=("Arial", 10, "bold"), bg="#f0f0f0")
        self.temp_value_label.pack(anchor="e")
        
        # Ranges hints (Visual only, simple buttons effectively)
        temp_btns_frame = tk.Frame(temp_frame, bg="#f0f0f0")
        temp_btns_frame.pack(fill=tk.X, pady=2)
        for t in [10, 20, 25, 30, 40]:
            tk.Button(temp_btns_frame, text=f"{t}°C", command=lambda v=t: self.temp_var.set(v), font=("Arial", 8)).pack(side=tk.LEFT, padx=2)

        # 4. Humidity Input
        hum_frame = tk.LabelFrame(left_panel, text="Humidity (%)", bg="#f0f0f0", padx=10, pady=10)
        hum_frame.pack(fill=tk.X, pady=5)
        
        self.hum_slider = tk.Scale(hum_frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.hum_var, bg="#f0f0f0", highlightthickness=0)
        self.hum_slider.pack(fill=tk.X)
        self.hum_value_label = tk.Label(hum_frame, textvariable=self.hum_var, font=("Arial", 10, "bold"), bg="#f0f0f0")
        self.hum_value_label.pack(anchor="e")

        hum_btns_frame = tk.Frame(hum_frame, bg="#f0f0f0")
        hum_btns_frame.pack(fill=tk.X, pady=2)
        for h in [20, 40, 60, 80, 95]:
            tk.Button(hum_btns_frame, text=f"{h}%", command=lambda v=h: self.hum_var.set(v), font=("Arial", 8)).pack(side=tk.LEFT, padx=2)

        # 5. Control Outputs Display
        out_frame = tk.LabelFrame(left_panel, text="Control Outputs", bg="#f0f0f0", padx=10, pady=10)
        out_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(out_frame, text="Fan Power:", bg="#f0f0f0").grid(row=0, column=0, sticky="w")
        self.fan_progress = ttk.Progressbar(out_frame, orient=tk.HORIZONTAL, length=150, mode='determinate', variable=self.fan_output)
        self.fan_progress.grid(row=0, column=1, sticky="w", padx=5)
        tk.Label(out_frame, textvariable=self.fan_output, bg="#f0f0f0").grid(row=0, column=2, sticky="e") # Needs formatting in callback
        
        tk.Label(out_frame, text="Misting:", bg="#f0f0f0").grid(row=1, column=0, sticky="w", pady=5)
        self.mist_progress = ttk.Progressbar(out_frame, orient=tk.HORIZONTAL, length=150, mode='determinate', variable=self.mist_output)
        self.mist_progress.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        tk.Label(out_frame, textvariable=self.mist_output, bg="#f0f0f0").grid(row=1, column=2, sticky="e")

        # 6. Optimal Conditions Display
        self.opt_frame = tk.LabelFrame(left_panel, text="Optimal Conditions", bg="#f0f0f0", padx=10, pady=10)
        self.opt_frame.pack(fill=tk.X, pady=5)
        self.opt_temp_label = tk.Label(self.opt_frame, text="Optimal Temp: -", bg="#f0f0f0")
        self.opt_temp_label.pack(anchor="w")
        self.opt_hum_label = tk.Label(self.opt_frame, text="Optimal Humidity: -", bg="#f0f0f0")
        self.opt_hum_label.pack(anchor="w")

        # 7. Action Buttons
        btn_frame = tk.Frame(left_panel, bg="#f0f0f0")
        btn_frame.pack(fill=tk.X, pady=20)
        
        tk.Button(btn_frame, text="Run Simulation", command=self.run_simulation, bg="#e0e0e0").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_frame, text="Show Surfaces", command=self.show_surfaces, bg="#e0e0e0").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_frame, text="Reset", command=self.reset_simulation, bg="#e0e0e0").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # --- Right Panel Content ---
        tk.Label(right_panel, text="Visualization", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=10, pady=5)
        
        self.title_label = tk.Label(right_panel, text="Simulation", font=("Arial", 14, "bold"), bg="white")
        self.title_label.pack(pady=5)

        # Initial Plot
        self.fig = plt.Figure(figsize=(8, 6), dpi=100)
        self.plot_manager = PlotManager(self.fig)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_panel)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initialize
        self.update_optimal_display()
        self.run_simulation()

    def update_controller_mode(self):
        mode = self.controller_type_var.get()
        if mode == "Mamdani":
            self.current_controller = self.mamdani
        else:
            self.current_controller = self.sugeno
        self.controller_name = mode
        self.run_simulation()

    def update_optimal_display(self, event=None):
        species = self.species_var.get()
        stage = self.stage_var.get()
        
        if species in PLANT_DATA and stage in PLANT_DATA[species]:
            data = PLANT_DATA[species][stage]
            self.opt_temp = data["temp"]
            self.opt_hum = data["hum"]
            self.opt_temp_label.config(text=f"Optimal Temp: {self.opt_temp} °C")
            self.opt_hum_label.config(text=f"Optimal Humidity: {self.opt_hum} %")
        else:
            self.opt_temp = 25.0
            self.opt_hum = 60.0
            self.opt_temp_label.config(text="Optimal Temp: -")
            self.opt_hum_label.config(text="Optimal Humidity: -")
            
        self.run_simulation()

    def run_simulation(self):
        temp = self.temp_var.get()
        hum = self.hum_var.get()
        
        try:
            fan, mist = self.current_controller.compute(temp, hum)
            
            # Update output vars
            self.fan_output.set(fan)
            self.mist_output.set(mist)
            
            # Update Title
            species = self.species_var.get().capitalize()
            stage = self.stage_var.get()
            self.title_label.config(text=f"{self.controller_name} Controller - {species} ({stage})")
            
            # Update Plots
            temp_mf, hum_mf, _, _ = self.current_controller.get_variables()
            self.plot_manager.update_plots(temp, hum, fan, mist, temp_mf, hum_mf, self.opt_temp, self.opt_hum)
            
        except Exception as e:
            print(f"Error computing fuzzy logic: {e}")

    def show_surfaces(self):
        messagebox.showinfo("Info", "3D Surface viewing is not embedded in this window. (Placeholder for pop-up)")
        # In a real app we would launch plt.show() with the surface

    def reset_simulation(self):
        self.temp_var.set(25.0)
        self.hum_var.set(60.0)
        self.species_var.set("cucumber")
        self.stage_var.set("Vegetative")
        self.update_optimal_display()

if __name__ == "__main__":
    root = tk.Tk()
    app = GreenhouseControlGUI(root)
    root.mainloop()
