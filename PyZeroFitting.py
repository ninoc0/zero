import argparse
import os
import numpy as np
from zero import Circuit
from zero.analysis import AcSignalAnalysis
from zero.data import Series, Response
import pandas as pd
import matplotlib.pyplot as plt

# Reads and processes input files
def main():
    parser = argparse.ArgumentParser(description='Process node and data file.')
    
    # Add arguments for input_file and data_file
    parser.add_argument('input_file', type=argparse.FileType('r'), help='The node text file')
    parser.add_argument('data_file', type=argparse.FileType('r'), nargs='?', default=None, help='The data text file (optional)')
    parser.add_argument('--plot_pyzero', action='store_true', help='Plot PyZero responses')

    args = parser.parse_args()
    
    # Read the contents of the text files
    with args.input_file as infile:
        input_file_content = infile.read()

    data_file_content = None
    if args.data_file:
        with args.data_file as datafile:
            data_file_content = datafile.read()
    
    process_files(input_file_content, data_file_content, args.plot_pyzero)

def process_files(input_file_content, data_file_content, plot_pyzero):
    # Converting your node txt to PyZero format
    def convert_text_to_circuit(file_content):
        formatted_circuit_lines = []
        
        for line in file_content.splitlines():
            line = line.strip()
            if line.startswith('op'):
                parts = line.split()
                if len(parts) >= 6:
                    _, op_name, op_model, n1, n2, n3 = parts
                    formatted_circuit_lines.append(f'circuit.add_library_opamp(name="{op_name}", model="{op_model}", node1="{n1}", node2="{n2}", node3="{n3}")')
                else:
                    formatted_circuit_lines.append(f"Ignoring line: {line} (Invalid format for op-amp)")
            elif line.startswith(('r', 'c', 'l')):
                parts = line.split()
                if len(parts) >= 5:
                    elem_type, elem_name, elem_value, n1, n2 = parts
                    if elem_type == 'r':
                        formatted_circuit_lines.append(f'circuit.add_resistor(name="{elem_name}", value="{elem_value}", node1="{n1}", node2="{n2}")')
                    elif elem_type == 'c':
                        formatted_circuit_lines.append(f'circuit.add_capacitor(name="{elem_name}", value="{elem_value}", node1="{n1}", node2="{n2}")')
                    elif elem_type == 'l':
                        formatted_circuit_lines.append(f'circuit.add_inductor(name="{elem_name}", value="{elem_value}", node1="{n1}", node2="{n2}")')
                else:
                    formatted_circuit_lines.append(f"Ignoring line: {line} (Invalid format for resistor/capacitor/inductor)")

        formatted_circuit = '\n'.join(formatted_circuit_lines)
        return formatted_circuit

    def convert_text_to_freq(file_content):
        for line in file_content.splitlines():
            line = line.strip()
            if line.startswith('freq'):
                parts = line.split()
                if len(parts) == 4 and parts[0] == 'freq':
                    start_val = int(parts[1])
                    stop_val = int(parts[2])
                    interval = int(parts[3])
                    return start_val, stop_val, interval
        return None, None, None

    def convert_text_to_test(file_content):
        for line in file_content.splitlines():
            line = line.strip()
            if line.startswith('test'):
                parts = line.split()
                if len(parts) == 3 and parts[0] == 'test':
                    nin = (parts[1])
                    nout = (parts[2])
                    return nin, nout
        return None, None

    formatted_circuit = convert_text_to_circuit(input_file_content)
    start_val, stop_val, interval = convert_text_to_freq(input_file_content)
    nin, nout = convert_text_to_test(input_file_content)

    # PyZero Code
    circuit = Circuit()
    frequencies = np.logspace(start_val, stop_val, interval)

    exec(formatted_circuit)

    ## Analysis
    analysis = AcSignalAnalysis(circuit=circuit)
    solution = analysis.calculate(frequencies=frequencies, input_type="voltage", node=nin)

    res = solution.get_response(nin, nout)
    magres = res.db_magnitude
    phares = res.phase

    magnitude_z = np.array(magres)
    phase_z = np.array(phares)

    if plot_pyzero:
        plot = solution.plot_responses(sink=nout)
        plot.show()

    ## Experimental Code
    # Open and read the data file content
    if data_file_content:
        lines = data_file_content.splitlines()

        # Initialize empty lists for frequency, magnitude, and phase
        frequency_e = []
        magnitude_e = []
        phase_e = []

        start_parsing = True
        for line in lines:
            if start_parsing:
                # Skip comment lines
                if line.startswith('#') or not line.strip():
                    continue

                # Parse the data
                parts = line.split()
                if len(parts) == 3:
                    freq = float(parts[0])
                    mag = float(parts[1])
                    phs = float(parts[2])

                    frequency_e.append(freq)
                    magnitude_e.append(mag)
                    phase_e.append(phs)

        # Plots
        fig, ((s1, s2), (r1, r2)) = plt.subplots(2, 2, figsize=(10, 8), sharex=True)

        # Plot 1: Magnitude vs Frequency
        s1.semilogx(frequency_e, magnitude_e, 'b', label='Original Data', color='#f0a963ff')
        s1.semilogx(frequency_e, magnitude_z, 'b', label="PyZero Data")
        s1.set_ylabel('Magnitude(dB)')
        s1.set_title('Magnitude vs Frequency')
        s1.set_yticks([-40, -20, 0])
        s1.grid()
        s1.grid(which='minor', ls='--', alpha=0.5)
        s1.legend()

        # Plot 2: Phase vs Frequency
        s2.semilogx(frequency_e, phase_e, 'b', label='Original Data', color='#f0a963ff')
        s2.semilogx(frequency_e, phase_z, 'b', label="PyZero Data")
        s2.set_xlabel('Frequency (Hz)')
        s2.set_ylabel('Phase (degrees)')
        s2.grid()
        s2.grid(which='minor', ls='--', alpha=0.5)
        s2.set_title('Phase vs Frequency')
        s2.set_yticks([-45, 0, 45, 90])
        s2.legend()

        # Plot 3: Magnitude Residuals
        r1.semilogx(frequency_e, np.array(magnitude_e) - magnitude_z, '#f0a963ff')
        r1.set_ylabel('Magnitude(dB)')
        r1.set_title('Magnitude Residuals')

        # Plot 4: Phase Residuals
        r2.semilogx(frequency_e, np.array(phase_e) - phase_z, '#f0a963ff')
        r2.set_xlabel('Frequency (Hz)')
        r2.set_ylabel('Phase(degrees)')
        r2.set_title('Phase Residuals')

        # Adjust layout and show plot
        plt.tight_layout()

        plt.show()

if __name__ == '__main__':
    main()