import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# For now, assume symmetric airfoil
# Use NACA 4 digit formalas & convention

# Fin dimensions in inches
thickness = 0.25
root = 7.5
tip = 2.5

# thickness in percent chord
t_root = float(thickness/root)
t_tip = float(thickness/tip)

# Define x-axis per unit chord, for root, and for tip 
x = np.linspace(0,1, num=201, endpoint=True)
x_root = x * root
x_tip = x * tip

# Define thickness distribution using NACA formula for root and tip separately
yt_root = 5*t_root*(0.2969 * np.sqrt(x) - 0.1260*x - 0.3516*(x**2) + 0.2843*(x**3) - 0.1015*(x**4))
yt_tip =  5*t_tip*(0.2969 * np.sqrt(x) - 0.1260*x - 0.3516*(x**2) + 0.2843*(x**3) - 0.1015*(x**4))

# For symmetric airfoil, thickness is a purely vertical translation from the x-axis
yr_upper = root * yt_root 
yr_lower = root* -yt_root
ytip_upper = tip* yt_tip
ytip_lower = tip* -yt_tip

# For Selig format, concatenate respective X axes from TE to LE back to TE
Xr = np.concatenate([np.flip(x_root[1:]), x_root])
Xt = np.concatenate([np.flip(x_tip[1:]), x_tip])

# Concatenate respective root & tip upper and lower surfaces
Yr = np.concatenate([np.flip(yr_upper[1:]), yr_lower])
Yt = np.concatenate([np.flip(ytip_upper[1:]), ytip_lower])

# Define coordinates by combining X & Y arrays
root_coord = np.column_stack((Xr, Yr))
tip_coord = np.column_stack((Xt, Yt))

# Simple plotter method
def plotCoords(X,Y,title=""):   
    plt.plot(X,Y,'b-',lw=1.5)
    plt.axis('equal') 
    plt.title(title)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Exports coordinates to saved_profile_coords folder
def exportCoords(coords,name="NACA"):
    Path("saved_profile_coords").mkdir(exist_ok=True)
    filename = f"{name}.dat"
    filepath = Path("saved_profile_coords") / filename

    with open(filepath, 'w') as f:
        for row in coords:
            f.write(f"  {row[0]:.6e}  {row[1]:.6e}\n")
    
    print(f"Profile coordinates saved to {filepath}.")

# Plot for visual verification
plotCoords(Xr,Yr, title=f"Fin Root Airfoil, Max thickness = {thickness} in., Root = {root} in.")
plotCoords(Xt,Yt, title=f"Fin Tip Airfoil, Max thickness = {thickness} in., Tip = {tip} in.")

# Export to folder
exportCoords(root_coord, name=f"NACA_root_{root}inch")
exportCoords(root_coord, name=f"NACA_tip_{tip}inch")

