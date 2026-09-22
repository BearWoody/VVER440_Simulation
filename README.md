# VVER440 Simulation
A real-time, interactive, physics-based simulator of a Pressurized Water Reactor (PWR), heavily inspired by the VVER-440 (V-213) units used at the Dukovany Nuclear Power Station. Built entirely in Python using tkinter.
This project is not just a UI mockup—it features a custom thermodynamic and point-kinetics engine that simulates the delicate balance between reactor power, steam pressure, turbine RPM, and a live national electrical grid.

Realistic Reactor Physics: Features point kinetics, negative temperature coefficient (self-regulating feedback), and control rod group assemblies.
Fuel Burnup Simulation: The reactor's behavior changes depending on the fuel campaign state (100% fresh fuel requires rods at ~11%, while 10% depleted fuel requires rods at ~89% to maintain nominal power).

Full Plant Thermodynamics:
  Primary Loop: Pressurizer (heaters/sprays), Main Circulation Pumps, and cavitation limits (boiling point dynamically calculated based on pressure).
  Secondary Loop: Steam Generator thermodynamics, feedwater pumps, and BRU-A atmospheric steam dumps.
  Tertiary Loop: Condenser vacuum physics and cooling tower pumps.
