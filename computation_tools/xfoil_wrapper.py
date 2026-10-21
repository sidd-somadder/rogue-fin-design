import os
import shutil
import subprocess
import tempfile
import numpy as np
import matplotlib.pyplot as plt

def find_xfoil():

    # check system environment variable 
    explicit = os.environ.get("XFOIL_PATH")
    if explicit and os.path.isfile(explicit):
        return explicit

    found = shutil.which("xfoil") or shutil.which("xfoil.exe")
    if found:
        return found

    for candidate in [os.path.expanduser(r"~\XFOIL6.99\xfoil.exe"),]:
        if os.path.isfile(candidate):
            return candidate

    raise FileNotFoundError("XFOIL not found")

def run_xfoilv(dat_path, chord_ft, Vmax, alpha=0, xtr=0.01, iters=200):
    xfoil = find_xfoil()
    reynold = round(get_reynold(chord_ft,Vmax))
    dat_path = os.path.abspath(dat_path)
    
    with tempfile.TemporaryDirectory() as workdir:
        local_dat = "profile.dat"
        shutil.copy(dat_path, os.path.join(workdir, local_dat))

        polar_name = "polar.txt"
        polar_file = os.path.join(workdir, polar_name) 

        cmds = []
        # coords are in inches (chord = 5); NORM scales to unit chord so Re,
        # CL/CD and the c/4 moment reference are based on the real chord
        cmds.append("NORM")
        cmds.append(f"LOAD {local_dat}")
        cmds.append("")  # answer "Enter airfoil name" prompt (plain .dat has no name line)
        # no PANE: the spline smooths the sharp bevel corners and the BL solve diverges
        #cmds.append("NACA 0005")
        cmds.append("OPER")
        cmds.append(f"VISC {reynold}")
        cmds.append("MACH 0.28")
        cmds.append(f"ITER {iters}")
        cmds.append("VPAR")
        cmds.append(f"XTR {xtr} {xtr}")
        cmds.append("")
        cmds.append("PACC")
        cmds.append(polar_name)
        cmds.append("")
        cmds.append(f"ALFA {alpha}")
        cmds.append("PACC")
        #cmds.append("")
        #cmds.append("QUIT")

        stdin = "\n".join(cmds) + "\n"
        timeout=60
        try:
            proc = subprocess.run(
                [xfoil], input=stdin, cwd=workdir,
                capture_output=True, text=True, timeout=timeout
                )
        except subprocess.TimeoutExpired:
            raise RuntimeError(
                f"XFOIL timed out after {timeout} s.")

        if not os.path.isfile(polar_file):
            raise RuntimeError("XFOIL produced no polar file")

        #print(proc.stdout[-4000:])

        cl, cd, cdp = read_polar(polar_file, alpha)
        # symmetric section at alpha = 0 should give CL ~ 0; XFOIL can converge
        # to a lopsided separated solution on sharp-cornered plates
        if alpha == 0 and abs(cl) > 0.01:
            print(f"WARNING: CL = {cl} at alpha = 0, solution is asymmetric; treat CD with suspicion")
        return float(cd), float(cd-cdp), float(cdp);

def read_polar(polar_file, alpha):
    data = np.loadtxt(polar_file, skiprows=12, ndmin=2)
    if data.shape[0] == 0:
        raise RuntimeError(f"XFOIL did not converge at alpha = {alpha}")
    cl, cd, cdp = data[0, 1], data[0, 2], data[0, 3]
    return cl, cd, cdp          # friction: cd - cdp

def get_reynold(chord_ft, Vmax, nu=1.57e-4):
    return (chord_ft*Vmax)/nu;

def run_xfoilinv(dat_path, alpha=0):
    xfoil = find_xfoil()
    dat_path = os.path.abspath(dat_path)
        
    with tempfile.TemporaryDirectory() as workdir:
        local_dat = "profile.dat"
        shutil.copy(dat_path, os.path.join(workdir, local_dat))        
        polar_name = "polar.txt"
        polar_file = os.path.join(workdir, polar_name) 
        
        cmds = []
        cmds.append("NORM")
        cmds.append(f"LOAD {local_dat}")
        #cmds.append("NACA 0005")
        cmds.append("")
        cmds.append("OPER")
        cmds.append("PACC")
        cmds.append(polar_name)
        cmds.append("")  # answer polar dump filename prompt
        cmds.append(f"ALFA {alpha}")
        cmds.append("")
        cmds.append("PACC")
        cmds.append("")
        cmds.append("QUIT")

        stdin = "\n".join(cmds) + "\n"
        timeout=60
        try:
            proc = subprocess.run(
                [xfoil], input=stdin, cwd=workdir,
                capture_output=True, text=True, timeout=timeout
                )
        except subprocess.TimeoutExpired:
            raise RuntimeError(
                f"XFOIL timed out after {timeout} s.")

        if not os.path.isfile(polar_file):
            raise RuntimeError("XFOIL produced no polar file")

        #print(proc.stdout[-4000:])

        cl, cd,cdp = read_polar(polar_file, alpha)
        return float(cl), float(cd);


chord = np.linspace(2.5,7.5,num=11,endpoint=True)
chord_ft = chord / 12
Vmax = 500 # ft; from selected iteration 3 planform
coords_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saved_profile_coords")

# blunt LE only converges with transition tripped right after the LE face corners (XTR 0.001) and more iterations;
# the sharp wedge hangs at XTR <= 0.002 but its Cd is insensitive between 0.005 and 0.01, so it keeps 0.01
Cd_sharp = np.full_like(chord, np.nan)
Cd_blunt = np.full_like(chord, np.nan)
for k, i in enumerate(chord):
    sharp_path = os.path.join(coords_dir, f"double_wedge_{i}inchchord.dat")
    blunt_path = os.path.join(coords_dir, f"blunt_wedge_{i}inchchord.dat")
    try:
        Cd_sharp[k] = run_xfoilv(sharp_path, chord_ft[k], Vmax)[0]
    except RuntimeError as e:
        print(f"Sharp wedge, chord = {i} in: {e}")
    try:
        Cd_blunt[k] = run_xfoilv(blunt_path, chord_ft[k], Vmax, xtr=0.001, iters=300)[0]
    except RuntimeError as e:
        print(f"Blunt wedge, chord = {i} in: {e}")
    print(f"Chord = {i} in | Cd (sharp) = {Cd_sharp[k]:.5f} | Cd (blunt) = {Cd_blunt[k]:.5f}")

plt.plot(chord, Cd_sharp, 'o-', label="Sharp double wedge")
plt.plot(chord, Cd_blunt, 's-', label="Blunt double wedge")
plt.xlabel("Chord (in)")
plt.ylabel(r"$C_d$")
plt.grid(True, alpha=0.2)
plt.legend()
plt.title(r"Section $C_d$ vs. Chord ($\alpha$ = 0)")
plt.show()
    