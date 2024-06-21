import matplotlib.pyplot as plt
import numpy as np

class Fitting:
    def __init__(self):
        return None

    def plot_responses(self, data_file, magnitude, phase):
        def process_file(data_file):
            # Open and read the data file content
            with open(data_file, 'r') as file:
                lines = file.readlines()

            # Initialize empty lists for frequency, magnitude, and phase
            frequency_e = []
            magnitude_e = []
            phase_e = []

            for line in lines:
                # Skip comment lines
                if line.startswith('#') or not line.strip():
                    continue

                # Parse the data
                parts = line.split()
                if len(parts) == 3:
                    try:
                        freq = float(parts[0])
                        mag = float(parts[1])
                        phs = float(parts[2])

                        frequency_e.append(freq)
                        magnitude_e.append(mag)
                        phase_e.append(phs)
                    except ValueError as e:
                        print(f"Error parsing line: {line}, Error: {e}")
            return frequency_e, magnitude_e, phase_e

        frequency_e, magnitude_e, phase_e = process_file(data_file)

        # Create a figure with residuals plots
        fig, ((s1, s2), (r1, r2)) = plt.subplots(2, 2, figsize=(10, 8), sharex=True)

        # Plot 1: Magnitude vs Frequency
        s1.semilogx(frequency_e, magnitude_e, 'b', label='Original Data', color='#f0a963ff')
        s1.semilogx(frequency_e, magnitude, 'b', label="PyZero Data")
        s1.set_ylabel('Magnitude(dB)')
        s1.set_title('Magnitude vs Frequency')
        s1.set_yticks([-40, -20, 0])
        s1.grid()
        s1.grid(which='minor', ls='--', alpha=0.5)
        s1.legend()

        # Plot 2: Phase vs Frequency
        s2.semilogx(frequency_e, phase_e, 'b', label='Original Data', color='#f0a963ff')
        s2.semilogx(frequency_e, phase, 'b', label="PyZero Data")
        s2.set_xlabel('Frequency (Hz)')
        s2.set_ylabel('Phase (degrees)')
        s2.grid()
        s2.grid(which='minor', ls='--', alpha=0.5)
        s2.set_title('Phase vs Frequency')
        s2.set_yticks([-45, 0, 45, 90])
        s2.legend()

        # Plot 3: Magnitude Residuals
        r1.semilogx(frequency_e, np.array(magnitude_e) - magnitude, '#f0a963ff')
        r1.set_ylabel('Magnitude(dB)')
        r1.set_title('Magnitude Residuals')

        # Plot 4: Phase Residuals
        r2.semilogx(frequency_e, np.array(phase_e) - phase, '#f0a963ff')
        r2.set_xlabel('Frequency (Hz)')
        r2.set_ylabel('Phase(degrees)')
        r2.set_title('Phase Residuals')

        # Adjust layout and show plot
        plt.tight_layout()

        return plt
