import numpy as np
import os
import zero
import pandas as pd

import zero.fitting
from zero import Circuit
from zero.analysis import AcSignalAnalysis
from zero.data import Series, Response
from zero.fitting import *

# 1000 frequencies between 10 mHz to 100 kHz.
frequencies = np.logspace(-2, 5, 100)

# Create circuit object.
circuit = Circuit()

# Add components.
circuit.add_library_opamp(model="AD829", node1="n4", node2="n2", node3="n5")
circuit.add_resistor(value="1k", node1="n1", node2="n2")
circuit.add_resistor(value="1k", node1="n3", node2="n4")
circuit.add_resistor(value="1k", node1="n4", node2="gnd")
circuit.add_resistor(value="1k", node1="n2", node2="n5")
circuit.add_capacitor(value="5p", node1="n2", node2="n5")
circuit.add_capacitor(value="5p", node1="gnd", node2="n4")
circuit.add_library_opamp(model="AD829", node1="gnd", node2="n7", node3="n8")
circuit.add_resistor(value="1k", node1="n5", node2="n6")
circuit.add_resistor(value="100k", node1="n5", node2="n7")
circuit.add_resistor(value="1k", node1="n7", node2="n8")
circuit.add_capacitor(value="2.2n", node1="n6", node2="n7")
circuit.add_capacitor(value="5p", node1="n7", node2="n8")

nin = 'n1'
nout = 'n8'

analysis = AcSignalAnalysis(circuit=circuit)
solution = analysis.calculate(frequencies=frequencies, input_type="voltage", node=nin)
fitting = Fitting()

res = solution.get_response(nin, nout)
magres = res.db_magnitude
phares = res.phase

magnitude_z = np.array(magres)
phase_z = np.array(phares)

# Data File
script_path = os.path.dirname( os.path.abspath(__file__) )
data_file_path = os.path.join(script_path, 'data.txt')

if os.path.exists(data_file_path):
    print("Data file found.")
else:
    print("Data file not found.")

plot = fitting.plot_responses(data_file_path, magnitude_z, phase_z)

if plot:
   plot.savefig('fig1.png')
   print("Plot saved!")
else:
    print("Plot not generated.")
plt.show()
