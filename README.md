OMNIMAC Simulator (Developed by Hussam Abdellatif)
=================

Welcome to the official simulator for:

"OMNIMAC: Enabling Virtual Omni-Directional Connectivity in Narrow-Beam THz Systems with Reflecting Surfaces"

This project provides a lightweight Python-based simulator developed to evaluate MAC protocols in highly directional THz systems. The simulator supports both analytical and simulation-based evaluations and was used in our published work to benchmark OMNIMAC against existing protocols like ADAPT.

Main Publication:
-----------------
OMNIMAC: Enabling Virtual Omni-Directional Connectivity in Narrow-Beam THz Systems with Reflecting Surfaces  
Authors: Hussam Abdellatif, Albert Diez-Comas, Arjun Singh, Josep M. Jornet

Getting Started
---------------
Main Simulation Entry:
    python main_OMNIMAC.py

Graphical Interface for Packet Tracing and Visualization:
    python UNLAB_shark.py

Virtual Environment:
- The required Python environment is captured in the 'venvsim' folder.
- To create or activate the environment:

    python3 -m venv venvsim
    source venvsim/bin/activate
    pip install -r requirements.txt

If no requirements.txt is included, you can generate one using:
    pip freeze > requirements.txt

Project Structure
-----------------
main_OMNIMAC.py     --> Main simulation + analytical model  
UNLAB_shark.py      --> GUI for packet trace visualization  
parameters.py       --> Simulation constants and configuration  
phy.py              --> PHY-layer functions (SNR, BER, modulation)  
results.py          --> Logging and results storage  
plotter.py          --> Visualization tools  
math_toolkit.py     --> Math helpers  
utilities.py        --> Utility functions  
room2.py            --> Room modeling  
satellite_FOV.py    --> Satellite field-of-view modeling  
main_ADAPT2.py      --> Baseline ADAPT protocol (v2)  
main_ADAPTSIM.py    --> Baseline ADAPT protocol (simulation mode)  
trigTest.py         --> Experimental code  
untitled.m          --> MATLAB utility

Key Features
------------
- OMNIMAC protocol with reflective-surface-based NLoS support
- GUI visualization of packet events and network layout
- Sectorized beam steering model with configurable transition latency
- Analytical and simulation-based throughput comparison
- Control and data plane separation (RTS/CTS logic)
- Performance benchmarking against ADAPT-3

License and Citation
--------------------
This simulator is released for academic and research use.
If you use this code in your work, please cite the original OMNIMAC paper.

Acknowledgments
---------------
Developed at Northeastern University as part of THz MAC research.
Supported by UNLAB and collaborators at University at Buffalo.
