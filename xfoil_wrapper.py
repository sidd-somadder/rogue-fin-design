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

def run_xfoilv(dat_path, chord_ft, Vmax, alpha=0):
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
        cmds.append("ITER 200")
        cmds.append("VPAR")
        cmds.append("XTR 0.01 0.01")
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


chord = 4.0 # in
chord_ft = chord/12.0
Vmax = 309 # ft
fileA = "double_wedge_4inchchord.dat"
fileB = "teardrop_4inchchord.dat"

dat_pathA = os.path.join(os.path.dirname(__file__), "saved_profile_coords", fileA)
dat_pathB = os.path.join(os.path.dirname(__file__), "saved_profile_coords", fileB)
print(dat_pathA)

print(f"Cd (Chamfered) : {run_xfoilv(dat_pathA,chord_ft,Vmax)}")
print(f"Cd (Teardrop) : {run_xfoilv(dat_pathB,chord_ft,Vmax)}")

print(run_xfoilinv(dat_pathA, alpha=2)[0])
print(run_xfoilinv(dat_pathB, alpha=2)[0])
    