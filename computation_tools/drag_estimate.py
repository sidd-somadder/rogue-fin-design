import numpy as np

# Primarily using John Anderson's Fundamentals of Aerodynamics, 7th Edition (2024) for reference

def wing_FF_incompressible(tc):
    # Raymer form factor
    return 1+(2*tc) + 100*(tc**4)

def get_friction_coeff(L, V, nu=1.57e-4,):
    Re_L = (V*L) / (nu)

    # Von Karman + Blasius
    return 0.074/(Re_L**(0.2))

def estimate_skin_friction_drag(root, tip, height, V, t, steps=100, rho=0.002377):

    # discretize planform into strips/sections
    y = np.linspace(0,height,steps+1)
    midpt = (y[1:] + y[:-1])/2
    dy = height/steps

    # chord as a function of the position along fin span
    c_y = ((tip-root)/height) * midpt + root 

    # get thickness to chord along span
    tc = t/(c_y)

    # dynamic presssure
    q = 0.5 * rho * (Vmax**2)

    Cf = get_friction_coeff(L=c_y,V=V)
    formfac = wing_FF_incompressible(tc)

    # get drag contribution for each strip/section
    C_Df = (Cf)*(formfac)*(2*c_y*dy) 

    # Return as a drag force (lbs)
    return np.sum(C_Df) * q

# CHANGE THESE INPUTS
root = 5.5
tip = 3
height = 4.25
Vmax = 308

# Previous year fin planform dimensions
root_OLD = 9.0
tip_OLD = 3.0
height_OLD = 4.0
thickness = 0.25

# convert units in inches to feet
thickness = thickness/12
root = root/12
tip = tip/12
height = height/12
root_OLD = root_OLD/12
tip_OLD = tip_OLD/12
height_OLD = height_OLD/12

drag = estimate_skin_friction_drag(root,tip,height,Vmax,thickness)
drag_prev = estimate_skin_friction_drag(root_OLD,tip_OLD,height_OLD,Vmax,thickness)

percent_change = 100 * ((drag-drag_prev)/drag_prev)

print(f"Estimated new skin friction : {drag:.3g} lbf")
print(f"Estimated previous skin friction : {drag_prev:.3g} lbf")
print(f"Estimated % change : {percent_change:.3g}")
#print(2* get_friction_coeff(4/12, 309))

