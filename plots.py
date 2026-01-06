import matplotlib.pyplot as plt
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
