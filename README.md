# Rogue Fin Design (2026–27)

Fin redesign for NYU Rogue Aerospace's 2026–27 FAR-OUT competition rocket. The goal is to reduce fin planform area, and with it fin drag, while keeping the competition's stability and damping requirements and the team's flutter margin. This repository holds the Python analysis tools, the OpenRocket flight data they run on, the fin cross-section coordinates used in XFOIL, and the design documentation.

**Status:** Iteration 3 closed. The selected fin flies on the November 8, 2026 sub-scale launch; Iteration 4 will revisit the cross-section.

## Current design

| | Previous full-scale fins | Selected (Iteration 3) | Requirement |
|---|---|---|---|
| Planform, root × tip × height (in) | 10 × 2 × 5 | **7.5 × 2.5 × 5** | — |
| Area per fin | 30.0 in² | 25.0 in² (−16.7%) | — |
| Rail-exit stability, worst of 30 runs at 20 mph | 1.61 cal | 1.66 cal | ≥ 1.5 cal |
| Damping ratio ζ at 30 mph | 0.07–0.12 | 0.06–0.10 | 0.03–0.5 |
| Flutter margin, V<sub>f</sub> / V<sub>max</sub> | 3.1 | 3.5 | ≥ 2 |
| Estimated fin skin-friction drag | — | −11.8% | — |

Both fins are cropped deltas. The sub-scale flight keeps the team's 45° chamfered edges.

## Documentation

| Document | Contents |
|---|---|
| [Fin Design Summary Report](docs/Fin_Design_Summary_Report.pdf) | **Start here.** Requirements, design approach, iteration history, key findings, next steps. |
| [Rocket Damping](docs/Rocket_Damping.pdf) | The damping-ratio method behind `damping.py`. |
| [Preliminary Planform Drag](docs/Preliminary_Planform_Drag.pdf) | The skin-friction drag estimate behind `drag_estimate.py`. |

## Repository layout

```
rogue-fin-design/
├── computation_tools/      Python analysis scripts
├── flight_data/            OpenRocket simulation exports (CSV)
├── saved_profile_coords/   Fin cross-section coordinates for XFOIL (Selig .dat)
├── docs/                   Summary report and method write-ups (PDF)
├── requirements.txt
└── LICENSE
```

## Tools

| Script | What it does | Method |
|---|---|---|
| `damping.py` | Damping ratio ζ over a simulated flight, including aerodynamic and jet damping. Prints the maximum and minimum after rail exit and plots ζ against time. | Mandell (1973), Prandtl–Glauert correction on the fins |
| `drag_estimate.py` | Skin-friction drag of a candidate fin against the previous fins, both at a common reference velocity. | Turbulent flat plate (one-seventh power law), Raymer form factor, summed over spanwise strips |
| `flutter.py` | Flutter speed, its ratio to the rocket's maximum velocity, and the relative change between two planforms. | NACA TN 4197 |
| `profile_gen.py` | Cross-section coordinates in Selig format: 45° chamfer / double wedge, blunt wedge, elliptical leading edge. | — |
| `xfoil_wrapper.py` | Runs XFOIL viscous and inviscid analyses on saved sections and sweeps section drag against chord. | XFOIL |

The scripts have no command-line arguments. Each has an inputs block near the bottom, marked `# CHANGE THESE ...`. Edit it and run the file. Geometry is entered in inches and velocity in ft/s; the scripts convert to ft–slug–s internally.

## Getting started

Requires Python 3 with NumPy and Matplotlib.

```bash
git clone https://github.com/sidd-somadder/rogue-fin-design.git
cd rogue-fin-design
pip install -r requirements.txt
python computation_tools/damping.py
```

Run `profile_gen.py` from the repository root, since it saves to `saved_profile_coords/` relative to the working directory.

`xfoil_wrapper.py` also needs [XFOIL](https://web.mit.edu/drela/Public/web/xfoil/). It looks for the executable in this order: the `XFOIL_PATH` environment variable, your `PATH`, then `~\XFOIL6.99\xfoil.exe`.

```bash
export XFOIL_PATH=/path/to/xfoil          # macOS / Linux
setx XFOIL_PATH "C:\path\to\xfoil.exe"    # Windows
```

## Using your own OpenRocket data with `damping.py`

`damping.py` reads columns **by position** and converts units itself. A different column order or unit gives wrong results without an error, so export from OpenRocket with exactly these columns, in this order:

| # | Column | Units |
|---|---|---|
| 1 | Time | s |
| 2 | Total velocity | ft/s |
| 3 | Mass | oz |
| 4 | Longitudinal moment of inertia | lb·ft² |
| 5 | CG location | in |
| 6 | Air density | lb/ft³ |
| 7 | Mach number | — |

Include the field descriptions and flight events as comments, with `#` as the comment character. The script finds rail exit from the `# Event LAUNCHROD occurred` line. Save the file to `flight_data/`, then set `file` and the rocket geometry (`root`, `tip`, `height`, `body_diam`, `rocket_len`, `nc_len`) in the inputs block.

Main assumptions in the model:

- Only the nose cone and fins produce normal force. Body lift is neglected, and the airframe has no transitions.
- The nose cone has C<sub>Nα</sub> = 2 and its center of pressure at L<sub>N</sub>/3.
- The fins are a cropped delta whose trailing edge is flush with the aft end, and the nozzle exit is at the aft end.
- The method is linear in angle of attack, so the rail-exit value in a strong crosswind is an estimate.

## Flight data

| File | Rocket and fins | Wind |
|---|---|---|
| `perseverence2026_nowind.csv` | Full scale, previous fins (10 × 2 × 5) | None |
| `perseverence2026_30mph.csv` | Full scale, previous fins (10 × 2 × 5) | 30 mph |
| `candidateG_fullscale_30mph.csv` | Full scale, selected fins (7.5 × 2.5 × 5) | 30 mph |
| `iteration2_subscale_nowind.csv` | Sub-scale, Iteration 2 | None |
| `iteration2_subscale_30mph.csv` | Sub-scale, Iteration 2 | 30 mph |

## References

- G. K. Mandell, G. J. Caporaso, and W. P. Bengen, *Topics in Advanced Model Rocketry*. MIT Press, 1973.
- S. Niskanen, *OpenRocket Technical Documentation*, version 13.05, 2013.
- D. J. Martin, "Summary of Flutter Experiences as a Guide to the Preliminary Design of Lifting Surfaces on Missiles," NACA TN 4197, 1958.
- J. D. Anderson, Jr. and C. P. Cadou, *Fundamentals of Aerodynamics*, 7th ed. McGraw-Hill, 2024.
- D. P. Raymer, *Aircraft Design: A Conceptual Approach*, 6th ed. AIAA, 2018.
- M. Drela, "XFOIL: An Analysis and Design System for Low Reynolds Number Airfoils," in *Low Reynolds Number Aerodynamics*, Springer, 1989.
- Friends of Amateur Rocketry, *FAR-OUT 2026–27 Official Competition Rules and Requirements*, Rev. 2026-08-31.

## Author and license

Siddhartha Somadder, Flight Dynamics, NYU Rogue Aerospace. Released under the [MIT License](LICENSE).
