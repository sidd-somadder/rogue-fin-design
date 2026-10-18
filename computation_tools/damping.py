import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

# Primarily using Mandell's Topics in Advanced Model Rocketry (1973) for reference

def getDampingRatio(Ccm, Cdm, I_long):
    return Cdm / (2*np.sqrt(Ccm*I_long));

def getJetDampingMCoef(mflow, exit_X, CG):
    return mflow*(exit_X - CG)**2

def getAeroDampingMCoef(Aref, V, CP, CG, C_Nalph_F, C_Nalph_NC=2.0, rho=0.002377):
    fin_term = C_Nalph_F*(CP[0]-CG)**2
    nc_term = C_Nalph_NC*(CP[1]-CG)**2 
    sum = fin_term + nc_term
    return 0.5 * rho * V * Aref * sum

def getCorrectiveMCoeff(Aref, V, CP, CG, C_Nalph_F, C_Nalph_NC=2.0, rho=0.002377):
    fin_term = C_Nalph_F*(CP[0]-CG)
    nc_term = C_Nalph_NC*(CP[1]-CG) 
    sum = fin_term + nc_term
    return 0.5 * rho * (V**2) * Aref * sum

def getNormalFCoeff(Cr, Ct, S, rt, N=4, beta = 1): # Assume cropped delta
    # Fin Aspect Ratio
    AR = (4*S)/(Cr+Ct)

    gamma = np.arctan((0.5*Cr - 0.5*Ct)/S)
    # print(f"GAMMA = {gamma}")
    num = N*AR*((Cr+Ct)/(2*rt))*(S/rt)
    den = 2 + np.sqrt(4+ (((AR*beta)/(np.cos(gamma)))**2))

    C_N_alpha_F = num/den

    # Correction factor due to body tube interference
    K = 1 +  rt/(S + rt)

    C_N_alpha_F =  K * C_N_alpha_F

    # Sharp nose cone assumption
    C_N_alpha_NC = 2

    return C_N_alpha_F, C_N_alpha_NC

def getCenterPressure(NC_len, RK_len, root, tip):
    # Assume Tangent Ogive nosecone
    Z_NC = 0.466*NC_len

    # Use nomenclature from Mandell; Assume root TE flush with end of rocket; assume clipped delta
    Z_T = RK_len - root
    Xt = root - tip
    Z_F2 = (Xt/3) * ((root+2*tip)/(root+tip))
    Z_F3 = (1/6)*((root + tip) - (root*tip)/(root + tip))

    Z_F = Z_T + Z_F2 + Z_F3
    return [Z_F, Z_NC]

# CHANGE THESE VALUES: (inches)
root = 5.5
tip = 3
height = 4.25
body_diam = 5.15
rocket_len = 112
nc_len = 25.6

# CHANGE THIS .CSV FILE NAME
file = 'iteration2_subscale_30mph.csv'

# Extract .csv data from specified file in flight_data/ folder
script_dir = Path(__file__).resolve().parent
csv_path = script_dir.parent / 'flight_data' / file
data = np.loadtxt(csv_path, delimiter=',', skiprows=1)

# Gravitational acceleration factor
G_C = 32.174

# Import time (s), velocity (ft/s), mass (oz), longitudinal inertia (lbft^2), center of gravity (ft), density (lb/ft^3), mach number
time = data[:,0]
velocity = data[:,1]
mass = data[:,2] / 16 / G_C
I_long = data[:,3] / G_C
CG = data[:,4] / 12
rho = data[:,5] / G_C
M = data[:,6]

# Compressibility Correction (Prandtl-Glauert); works for subsonic compressible flow
beta = np.sqrt(1-M**2)

# Rocket dimensions converted to to ft
root = root / 12
tip = tip / 12
height = height / 12
body_diam = body_diam / 12
rocket_len = rocket_len / 12
nc_len = nc_len / 12
Aref = (np.pi * (body_diam**2)/4)

# Estimate mass flow using gradient
m_flow = - np.gradient(mass, time)

CP = getCenterPressure(nc_len, rocket_len, root, tip)
C_Nalph_F, C_Nalph_NC = getNormalFCoeff(root, tip, height, (body_diam/2), N=4, beta=beta)
Cdm_aero = getAeroDampingMCoef(Aref, velocity, CP, CG, C_Nalph_F, C_Nalph_NC=C_Nalph_NC, rho=rho)
Cdm_jet = getJetDampingMCoef(m_flow, rocket_len, CG)
Cdm = (Cdm_aero + Cdm_jet)
Ccm = getCorrectiveMCoeff(Aref, velocity, CP, CG, C_Nalph_F, C_Nalph_NC=C_Nalph_NC, rho=rho)
zeta = getDampingRatio(Ccm, Cdm, I_long=I_long)

# Since we're interested in damping starting from launch rod exit (~0.73s), mask zeta from about the 70th index and on
zeta = zeta[70:]
print(f"Max. Damping Ratio: {np.max(zeta)}")
print(f"Min. Damping Ratio: {np.min(zeta)}")

# Plot damping ratio as a function of time using OpenRocket data
zeta_nan = np.empty(70)
zeta_nan.fill(np.nan)
zeta_plot = np.concatenate((zeta_nan,zeta))
plt.plot(time,zeta_plot)
plt.xlabel("Time (s)")
plt.ylabel(r"Damping Ratio ($\zeta$)")
plt.grid(True,alpha=0.2)
plt.title("Damping Coefficient vs. Time")
plt.show()


