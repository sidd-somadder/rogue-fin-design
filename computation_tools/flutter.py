import numpy as np

# This script automates calculations for worst case fin flutter and compares it to rocket speed.

def relative_flutter(ar_new, ar_old, tc_new, tc_old, taper_new, taper_old):
    '''
    Uses known taper ratio, aspect ratio, and effective thickness to chord ratio for fins to calculate relative flutter speed ratio
    Returns a factor r where Vf_new = r*Vf_old
    '''
    tc_ratio = (tc_new**3) / (tc_old**3)
    tapers_ratio = (taper_old + 1) / (taper_new + 1)
    ar_ratio_cubic = (ar_old**3) / (ar_new**3)
    ar_ratio_lin = (ar_new + 2) / (ar_old + 2)

    return np.sqrt(ar_ratio_cubic * ar_ratio_lin * tapers_ratio * tc_ratio)

def absolute_flutter(tc,G,P,AR,taper,a):
    '''
    Computes absolute flutter speed from NACA TN 4197 equation; estimate number, not precise.

    Inputs: Mach no. and known max rocket velocity (OpenRocket stats), effective thickness (tc)
    material shear modulus (G; ksi), local static pressure (P), fin aspect ratio (AR), tip/root taper ratio.
    '''
    numerator = 2*(G*1000)*(AR+2)*(tc**3)
    denominator = 1.337*(AR**3)*(P)*(taper+1)

    return a * np.sqrt(numerator/denominator)
    

def flutter_rocketspeed_ratio(Vflutter, Vmax_rocket):
    '''
    Simple method, uses worst-case scenario flutter and the max velocity of rocket to give safety factor
    Current design aims for V_f >= 2*Vmax_rocket 
    '''
    return Vflutter / Vmax_rocket

# CHANGE THESE DIMENSIONS; lengths in inches, vmax in ft/s
thickness = 0.25
h = 5
root = 10
tip = 2
vmax = 496

# from previous subscale
ar_old = 25/30
tc_old = 0.25/10
taper_old = 2/10
vmax_old = 496

# Working numbers, change as redesigns come
area = h*(root + tip)/2
ar_new = (h**2)/area
tc_new = thickness/root
taper_new = tip/root 

# Structural assumption: assume wood core only
birch_shear_mod = 90 #ksi
effective_shear_mod = 725 #ksi

# Static Pressure (psi); worst case using ground level static pressure
P = 14.7

# speed of sound calculation
temp = 32 # F, cold day
gamma = 1.4 # specific heat ratio of air
temp_rankine = 460+temp
R = 1716 # ft*lbf/slugR
a = np.sqrt(gamma*R*temp_rankine)

rel_fl = relative_flutter(ar_new=ar_new, ar_old=ar_old, tc_new=tc_new, tc_old=tc_old, taper_new=taper_new, taper_old=taper_old)
abs_fl_new = absolute_flutter(tc=tc_new, G=effective_shear_mod, P=P, AR=ar_new, taper=taper_new,a=a)
abs_fl_prev = absolute_flutter(tc=tc_old, G=effective_shear_mod, P=P, AR=ar_old, taper=taper_old,a=a)
flutter_factor = flutter_rocketspeed_ratio(Vflutter=abs_fl_new, Vmax_rocket=vmax)
flutter_factor_old = flutter_rocketspeed_ratio(Vflutter=abs_fl_prev, Vmax_rocket=vmax_old)

print(f"Relative flutter change factor : {rel_fl:.3f}")
print(f"New Absolute flutter estimate : {abs_fl_new:.3f} ft/s")
print(f"Flutter-to-Rocket Speed (FRS) factor: {flutter_factor:.3f}")
print(f"OLD FRS factor: {flutter_factor_old:.3f}")