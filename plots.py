import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Required for 3D plotting
import numpy as np

class PlotManager:
    def __init__(self, fig):
        self.fig = fig
        self.axes = self.fig.subplots(2, 2)
        self.fig.tight_layout(pad=3.0)

    def update_plots(self, temp, hum, fan, mist, temp_mf, hum_mf, opt_temp, opt_hum):
        # Clear axes
        for ax_row in self.axes:
            for ax in ax_row:
                ax.clear()

        ax_inputs = self.axes[0, 0]
        ax_outputs = self.axes[0, 1]
        ax_temp_mf = self.axes[1, 0]
        ax_hum_mf = self.axes[1, 1]

        # 1. Current Inputs Bar Chart
        labels = ['Temperature\n(normalized)', 'Humidity']
        # Normalize temp to 0-100 scale for visualization alongside humidity if desired, 
        # or just show raw values. The screenshot shows "Value (%)". 
        # Temp is 0-50, Hum is 0-100. The bar for Temp (red) is around 20 (height).
        # It says "Temperature (normalized)". 
        # If temp is 10, normalized (say to 50 max) is 20%. 
        # But let's just plot raw if the axis supports it or normalize. 
        # The y-axis is 0-100. So we should normalize temperature (x/50 * 100).
        
        temp_norm = (temp / 50) * 100
        values = [temp_norm, hum]
        colors = ['red', 'blue']
        
        ax_inputs.bar(labels, values, color=colors, alpha=0.7)
        ax_inputs.set_ylim(0, 100)
        ax_inputs.set_ylabel('Value (%)')
        ax_inputs.set_title('Current Inputs')
        
        # Optimal lines (dashed)
        # Opt Temp also normalized
        opt_temp_norm = (opt_temp / 50) * 100
        ax_inputs.axhline(y=opt_temp_norm, color='red', linestyle='--', label='Opt Temp', alpha=0.5)
        ax_inputs.axhline(y=opt_hum, color='blue', linestyle='--', label='Opt Hum', alpha=0.5)
        ax_inputs.legend()

        # 2. Control Outputs Bar Chart
        out_labels = ['Fan Power', 'Misting']
        out_values = [fan, mist]
        out_colors = ['orange', 'cyan']
        
        ax_outputs.bar(out_labels, out_values, color=out_colors, alpha=0.7)
        ax_outputs.set_ylim(0, 100)
        ax_outputs.set_ylabel('Output (%)')
        ax_outputs.set_title('Control Outputs')

        # 3. Temperature MF
        # We need the fuzzy variable object to plot
        # temp_mf is the control.Antecedent object
        for label in temp_mf.terms:
            ax_temp_mf.plot(temp_mf.universe, temp_mf[label].mf, label=label)
        
        ax_temp_mf.set_title('Temperature MF')
        ax_temp_mf.set_xlabel('Temperature (°C)')
        ax_temp_mf.set_ylabel('Membership')
        ax_temp_mf.legend(loc='upper right', fontsize='small')
        
        # Current Value Line
        ax_temp_mf.axvline(x=temp, color='black', linestyle='--', label='Current')

        # 4. Humidity MF
        for label in hum_mf.terms:
            ax_hum_mf.plot(hum_mf.universe, hum_mf[label].mf, label=label)
            
        ax_hum_mf.set_title('Humidity MF')
        ax_hum_mf.set_xlabel('Humidity (%)')
        ax_hum_mf.set_ylabel('Membership')
        ax_hum_mf.legend(loc='upper right', fontsize='small')
        
        # Current Value Line
        ax_hum_mf.axvline(x=hum, color='black', linestyle='--', label='Current')

        self.fig.canvas.draw()


def plot_membership_functions(controller):
    """
    Plots all membership functions (Inputs and Outputs) in a single figure.
    Matching the user's requested style.
    """
    temp, hum, fan, mist = controller.get_variables()
    
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Fuzzy Membership Functions', fontsize=16, fontweight='bold')
    
    # Helper to plot on axis
    def plot_var(ax, var, title, xlabel):
        for label in var.terms:
            ax.plot(var.universe, var[label].mf, label=label, linewidth=2)
            # Fill under curve for aesthetics
            ax.fill_between(var.universe, var[label].mf, alpha=0.2)
            
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel('Membership Degree')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1.05)

    plot_var(axs[0, 0], temp, 'Temperature Membership Functions', 'Temperature (°C)')
    plot_var(axs[0, 1], hum, 'Humidity Membership Functions', 'Humidity (%)')
    plot_var(axs[1, 0], fan, 'Fan Power Output Membership Functions', 'Fan Power (%)')
    plot_var(axs[1, 1], mist, 'Misting Intensity Output Membership Functions', 'Misting Intensity (%)') # Fixed key

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

def plot_control_surfaces(controller):
    """
    Plots 3D control surfaces and contour plots for Fan and Mist outputs.
    """
    print("Calculating control surfaces... (High Resolution)")
    
    # 1. Define range
    x_range = np.linspace(0, 50, 50)   # Temperature
    y_range = np.linspace(0, 100, 50)  # Humidity
    X, Y = np.meshgrid(x_range, y_range)
    
    Z_fan = np.zeros_like(X)
    Z_mist = np.zeros_like(X)
    
    # 2. Compute values
    # Note: Iterating element-by-element is necessary for fuzzy systems generally
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            fan_val, mist_val = controller.compute(X[i, j], Y[i, j])
            Z_fan[i, j] = fan_val
            Z_mist[i, j] = mist_val
            
    # 3. Plot Fan Surface
    fig1 = plt.figure(figsize=(16, 6))
    
    # 3D Plot
    ax1 = fig1.add_subplot(1, 2, 1, projection='3d')
    surf1 = ax1.plot_surface(X, Y, Z_fan, cmap='viridis', edgecolor='none', alpha=0.9)
    ax1.set_title('3D Control Surface: Fan Power', weight='bold')
    ax1.set_xlabel('Temperature (°C)')
    ax1.set_ylabel('Humidity (%)')
    ax1.set_zlabel('Fan Power (%)')
    fig1.colorbar(surf1, ax=ax1, shrink=0.5, aspect=10, label='Fan Power (%)')
    
    # Contour Plot
    ax2 = fig1.add_subplot(1, 2, 2)
    cont1 = ax2.contourf(X, Y, Z_fan, cmap='viridis', levels=20)
    ax2.set_title('Contour Plot: Fan Power', weight='bold')
    ax2.set_xlabel('Temperature (°C)')
    ax2.set_ylabel('Humidity (%)')
    fig1.colorbar(cont1, ax=ax2, label='Fan Power (%)')
    
    plt.tight_layout()
    plt.show()
    
    # 4. Plot Mist Surface
    fig2 = plt.figure(figsize=(16, 6))
    
    # 3D Plot
    ax3 = fig2.add_subplot(1, 2, 1, projection='3d')
    surf2 = ax3.plot_surface(X, Y, Z_mist, cmap='viridis', edgecolor='none', alpha=0.9)
    ax3.set_title('3D Control Surface: Misting Intensity', weight='bold')
    ax3.set_xlabel('Temperature (°C)')
    ax3.set_ylabel('Humidity (%)')
    ax3.set_zlabel('Misting Intensity (%)')
    fig2.colorbar(surf2, ax=ax3, shrink=0.5, aspect=10, label='Misting Intensity (%)')
    
    # Contour Plot
    ax4 = fig2.add_subplot(1, 2, 2)
    cont2 = ax4.contourf(X, Y, Z_mist, cmap='viridis', levels=20)
    ax4.set_title('Contour Plot: Misting Intensity', weight='bold')
    ax4.set_xlabel('Temperature (°C)')
    ax4.set_ylabel('Humidity (%)')
    fig2.colorbar(cont2, ax=ax4, label='Misting Intensity (%)')
    
    plt.tight_layout()
    plt.show()
