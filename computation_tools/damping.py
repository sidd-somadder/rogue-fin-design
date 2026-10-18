import numpy as np

# Primarily using Mandell's Topics in Advanced Model Rocketry (1973) for reference
# work in progress script: need to address for full-scale simulations 

def getDampingRatio(Ccm, Cdm, I_long):
    return Cdm / (2*np.sqrt(Ccm*I_long));

def getJetDampingMCoef(mflow, exit_X, CG):
    return mflow*(exit_X - CG)**2

def getAeroDampingMCoef(Aref, V, C_Nalp, CP, CG, rho=0.002377):
    # Note that the V term cancels in damping ratio, so any value works 
    fin_term = C_Nalp[0]*(CP[0]-CG)**2
    nc_term = C_Nalp[1]*(CP[1]-CG)**2 
    sum = fin_term + nc_term
    return 0.5 * rho * V * Aref * sum

def getCorrectiveMCoeff(Aref, V, C_Nalp, CP, CG, rho=0.002377):
    fin_term = C_Nalp[0]*(CP[0]-CG)
    nc_term = C_Nalp[1]*(CP[1]-CG) 
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

    return [float(C_N_alpha_F), float(C_N_alpha_NC)]

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

# Import Longitudinal moment of Inertia, mass, velocity, CG, 

# Compressibility Correction (Prandtl-Glauert); works for subsonic compressible flow
M = 0.3
beta = np.sqrt(1-M**2)

# Fin Dimensions
root = 5.5
tip = 3
height = 4.25

# Body Dimensions (Const.)
body_diam = 5.15
rocket_len = 112
nc_len = 25.6

Aref = np.pi * (body_diam**2)/4

CP = getCenterPressure(nc_len, rocket_len, root, tip)
C_Nalph = getNormalFCoeff(root, tip, height, (body_diam/2), N=4, beta=beta)
print(C_Nalph)


