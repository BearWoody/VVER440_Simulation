# VVER440 Simulation
A real-time, interactive, physics-based simulator of a Pressurized Water Reactor (PWR), heavily inspired by the VVER-440 (V-213) units used at the Dukovany Nuclear Power Station. Built entirely in Python using tkinter.
This project is not just a UI mockup—it features a custom thermodynamic and point-kinetics engine that simulates the delicate balance between reactor power, steam pressure, turbine RPM, and a live national electrical grid.

Realistic Reactor Physics: Features point kinetics, negative temperature coefficient (self-regulating feedback), and control rod group assemblies.
Fuel Burnup Simulation: The reactor's behavior changes depending on the fuel campaign state (100% fresh fuel requires rods at ~11%, while 10% depleted fuel requires rods at ~89% to maintain nominal power).

Full Plant Thermodynamics:
  Primary Loop: Pressurizer (heaters/sprays), Main Circulation Pumps, and cavitation limits (boiling point dynamically calculated based on pressure).
  Secondary Loop: Steam Generator thermodynamics, feedwater pumps, and BRU-A atmospheric steam dumps.
  Tertiary Loop: Condenser vacuum physics and cooling tower pumps.
Grid Synchronization & AGC:

A fully functional synchroscope for connecting turbines to the national grid.

Floating grid frequency (nominal 50.000 Hz) affected by national demand and the plant's output.

Simulated Primary Control (Droop) and Secondary Control (AGC / Virtual dispatchers).

Station Blackout (SBO) & Emergencies: Experience a total grid collapse. Maintain island mode, or rely on Emergency Diesel Generators (EDGs) to keep the primary pumps running and prevent a meltdown.

SCRAM (AZ): Emergency reactor shutdown with residual heat simulation.

This project is for educational and entertainment purposes. It is a simplified model and not intended for real-world nuclear engineering or training.
