import numpy as np;
import matplotlib.pyplot as plt
from pathlib import Path

def generate_prev_profile(chord, thickness=0.25, c_pts=200, chamfer=45, chamf_xdist=None):
    x_axis = np.linspace(0,chord, c_pts+1, endpoint=True);

    y_upper = np.zeros_like(x_axis)
    y_lower = np.zeros_like(x_axis)

    # LE and TE bevels run from the midline to full thickness over chamf_xdist (same units as chord)
    # chamf_xdist given -> used directly and chamfer angle is ignored
    # chamf_xdist None  -> derived from chamfer angle (deg)

    half_t = 0.5*thickness

    if chamf_xdist is None:
        chamf_xdist = half_t/np.tan(np.deg2rad(chamfer))

    if not 0 < chamf_xdist < 0.5*chord:
        raise ValueError(f"chamf_xdist = {chamf_xdist} must be between 0 and half the chord")

    le_max_t_percent = chamf_xdist/chord
    te_max_t_percent = (chord - chamf_xdist)/chord 

    LE_maxpt = round(c_pts*le_max_t_percent)
    TE_maxpt = round(c_pts*te_max_t_percent)

    LE_slope = (0.5*thickness)/(chord*le_max_t_percent)
    TE_slope = half_t / (chord * (1 - te_max_t_percent))

    # clamp to half_t: when chamf_xdist falls between grid points the rounded index overshoots the bevel
    y_upper[0:LE_maxpt+1] = np.minimum(LE_slope * x_axis[0:LE_maxpt+1], half_t)
    y_lower[0:LE_maxpt+1] = -y_upper[0:LE_maxpt+1]  

    y_upper[LE_maxpt+1:TE_maxpt] = half_t
    y_lower[LE_maxpt+1:TE_maxpt] = -half_t

    y_upper[TE_maxpt:-1] = np.minimum(half_t - TE_slope*(x_axis[TE_maxpt:-1] - chord*te_max_t_percent), half_t)
    y_lower[TE_maxpt:-1] = -y_upper[TE_maxpt:-1]

    y_upper[-1] = 0
    y_lower[-1] = 0

    # Selig format
    y_upper = np.flip(y_upper)
    upper = np.column_stack((np.flip(x_axis),y_upper))
    lower = np.column_stack((x_axis[1:], y_lower[1:]))

    coords = np.concatenate((upper,lower), axis=0)
    return(coords);

def generate_ellipse_profile(chord, thickness=0.25, c_pts=240, le_length=1.0, te_length=1.0):
    # elliptical LE (semi-axes le_length x half thickness), flat middle, linear TE chamfer to a point
    # LE and TE lengths are fixed; only the flat middle section changes with chord
    half_t = 0.5*thickness
    mid_length = chord - le_length - te_length

    if mid_length < 0:
        raise ValueError(f"chord = {chord} must be at least le_length + te_length = {le_length + te_length}")

    # points per section proportional to its chordwise length
    n_le = max(1, round(c_pts*le_length/chord))
    n_te = max(1, round(c_pts*te_length/chord))
    n_mid = c_pts - n_le - n_te if mid_length > 0 else 0

    # ellipse centred at (le_length, 0); even spacing in angle clusters points at the nose
    theta = np.linspace(0, 0.5*np.pi, n_le+1)
    x_le = le_length*(1 - np.cos(theta))
    y_le = half_t*np.sin(theta)

    x_mid = np.linspace(le_length, le_length + mid_length, n_mid+1)[1:]
    y_mid = np.full_like(x_mid, half_t)

    x_te = np.linspace(le_length + mid_length, chord, n_te+1)[1:]
    y_te = half_t*(chord - x_te)/te_length

    x_axis = np.concatenate((x_le, x_mid, x_te))
    y_upper = np.concatenate((y_le, y_mid, y_te))
    y_upper[-1] = 0

    # Selig format
    upper = np.column_stack((np.flip(x_axis), np.flip(y_upper)))
    lower = np.column_stack((x_axis[1:], -y_upper[1:]))

    coords = np.concatenate((upper,lower), axis=0)
    return(coords);

def profile_plot(coords):
    x = coords[:,0]
    y = coords[:,1]

    plt.plot(x,y, lw=2)
    plt.ylim(-2,2)
    plt.grid(True)
    plt.title(f"Chord = {coords[0,0]} inches")
    plt.ylabel("y, inch")
    plt.xlabel(f"x, inch")
    plt.show()

def save_profile_coords(coords, title="profile"):
    Path("saved_profile_coords").mkdir(exist_ok=True)

    filename = f"{title}.dat"

    filepath = Path("saved_profile_coords") / filename

    with open(filepath, 'w') as f:
        for row in coords:
            f.write(f"  {row[0]:.6e}  {row[1]:.6e}\n")

    print(f"Profile coordinates saved to {filepath}.")

chamfer_coords = generate_prev_profile(3,c_pts=240,chamf_xdist=1)
teardrop_coords = generate_ellipse_profile(3)
profile_plot(chamfer_coords)
profile_plot(teardrop_coords)
save_profile_coords(coords=chamfer_coords,title="double_wedge_3inchchord")
save_profile_coords(coords=teardrop_coords,title="teardrop_3inchchord")