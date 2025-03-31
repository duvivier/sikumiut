import numpy as np

def saturation_specific_humidity(T,Ps):

    """
    Calculates saturation specific humidity using parameter values of the Clausius-Clapeyron relation given in O'Gorman and Schneider, (2008).
    
    Input:
    
    T  [ temperature --- °C ]
    Ps [ Surface pressure --- Pa ]
    
    Output: 
    
    qs [ saturation specific humidity --- kg/kg ]
    
    """

    es0 = 610.78     # Saturation vapor pressure at T0
    T0  = 273.16     # Reference temperature
    Rv  = 461.5      # Gas constant of water vapor
    Lv  = 2.5e6      # Latent heat of vaporization
    ep  = 0.622      # Ratio of gas constants of dry air and water vapor
    T   = T + 273.15 # Convert temperature to Kelvin
    
    # Calculate saturation vapor pressure
    es  = es0 * np.exp(-(Lv/Rv) * ((1/T)-(1/T0)))
    
    # Calculate saturation specific humidity 
    qs  = ep * es / Ps
    
    return qs


def model(grid, T, F = 0, sea_ice_albedo = 'on', sea_ice_thermodynamics = 'on'):
    """
    ...
    
    Input:
    
    Output:
    
    """

    # --- parameters ---
    
    # physical parameters
    mld   = 60                     # depth of mixed layer [ m]
    cday  = 86400.0                # seconds in day [ s ]
    cyear = cday*365.25            # sec in calendar year [ s]
    cpsw  = 3.996e3                # specific heat of sea water [ J/kg/K ]
    rhosw = 1.026e3                # density of sea water [ kg/m^3 ]
    cw    = cpsw*rhosw*mld / cyear # heat capacity of mixed layer [ W yr m^-2 K^-1 ]

    D = 0.3                        # diffusivity for heat transport [ W m^-2 K^-1 ]

    A = 196                        # outgoing longwwave radiation when T = 0  [ W m^-2 ]
    B = 1.8                        # outgoing longwave radiation temperature dependence [ W m^-2 K^-1 ]
    
    S1 = 338                       # insolation seasonal dependence [ W m^-2 ]
    S0 = 420                       # insolation at equator [ W m^-2 ]
    S2 = 240                       # insolation spatial dependence [ W m^-2 ]
    a0 = 0.7                       # ice-free co-albedo at equator
    a2 = 0.1                       # ice-free co-albedo spatial dependence
    ai = 0.4                       # co-albedo where there is sea ice
    Fb = 0                         # heat flux from ocean below [ W m^-2 ]
    k = 2                          # sea ice thermal conductivity [ W m^-1 K^-1 ]
    Lf = 9.5                       # sea ice latent heat of fusion [ W yr m^-3 ]
    cg = 0.098                     # ghost layer heat capacity [ W yr m^-2 K^-1 ]
    tau = 1e-5                     # ghost layer coupling timescale [ yr ]
    Lv = 2.5e6                     # latent heat of vaporization [ J kg^-1 ]
    cp = 1004.6                    # heat capacity of air at constant pressure [ J kg^-1 K^-1 ]
    RH = 0.8                       # relative humidity
    Ps = 1e5                       # surface pressure [ Pa ]

    # grid and time-stepping parameters
    n   = grid['n']
    dx  = grid['dx']
    x   = grid['x']
    xb  = grid['xb']
    nt  = grid['nt']
    dur = grid['dur']
    dt  = grid['dt']

    print(f'Running SCM-MEBM for {dur} years...')
    
    # --- model ---

    # diffusion Operator (Wagner and Eisenman, (2015), Appendix A) 
    lam    = D/dx**2*(1-xb**2)
    L1     = np.append(0, -lam) 
    L2     = np.append(-lam, 0) 
    L3     = -L1-L2
    diffop = - np.diag(L3) - np.diag(L2[:n-1],1) - np.diag(L1[1:n],-1)

    # definitions for implicit scheme on Tg
    cg_tau = cg/tau
    dt_tau = dt/tau
    dc     = dt_tau*cg_tau
    kappa  = (1+dt_tau)*np.identity(n)-dt*diffop/cg

    ty     = np.arange(dt/2,1+dt/2,dt)
    S      = (np.tile(S0-S2*x**2,[nt,1])-np.tile(S1*np.cos(2*np.pi*ty),[n,1]).T*np.tile(x,[nt,1]))

    # zero out negative insolation
    S = np.where(S<0,0,S)

    # some more definitions
    M   = B+cg_tau
    aw  = a0-a2*x**2                 # open water albedo
    kLf = k*Lf

    # create output arrays
    Es_output = np.zeros((n,nt)) 
    Ts_output = np.zeros((n,nt))
    ASR_output = np.zeros((n,nt))
    time = np.linspace(0,1,nt)

    # initial conditions
    Tg = T                           # ghost layer temperature
    E = cw*T                         # enthalpy

    # start numerical integration by looping over Years 
    for years in range(dur):
        
        # Loop within One Year
        for i in range(nt):

            # Sea ice albedo
            if sea_ice_albedo == 'on':
                alpha = aw*(E>0) + ai*(E<0)
            else:
                alpha = aw

            C = alpha*S[i,:] + cg_tau*Tg - A + F

            # Solve for surface temperature with sea ice thermodynamics
            if sea_ice_thermodynamics == 'on':
                T0 = C/(M-kLf/E)
            else:
                T0 = E/cw

            # save final year
            if years == (dur-1): 
                Es_output[:,i] = E
                Ts_output[:,i] = T
                ASR_output[:,i] = alpha*S[i,:]

            T = E/cw*(E>=0)+T0*(E<0)*(T0<0)
            
            # Forward Euler on E
            E = E+dt*(C-M*T+Fb)

            # Implicit Euler on Tg

            # Forward Euler on diffusion of latent heat
            q = RH * saturation_specific_humidity(Tg,Ps)
            rhs1 = np.matmul(dt*diffop/cg, Lv*q/cp)

            if sea_ice_thermodynamics == 'on':
                Tg = np.linalg.solve(kappa-np.diag(dc/(M-kLf/E)*(T0<0)*(E<0)),
                               Tg + rhs1 + (dt_tau*(E/cw*(E>=0)+(ai*S[i,:]-A+F)/(M-kLf/E)*(T0<0)*(E<0))))
            else:
                Tg = np.linalg.solve(kappa,
                               Tg + rhs1 + dt_tau*(E/cw) )
                
    Hi_output = -Es_output/Lf*(Es_output<0)


    print(f'Global-mean surface temperature = {np.round(np.mean(Ts_output, axis=(0,1)),1)} °C')
    print(f'Equator-to-pole surface temperature difference = {np.round(np.ptp(np.mean(Ts_output, axis=1)),1)} °C')
    print(f'Global-mean top-of-atmosphere energy imbalance = {np.round(np.mean(ASR_output, axis=(0,1)) - A - B*np.mean(Ts_output, axis=(0,1)),1)} W m^{-2}')

    return time, Es_output, Ts_output, Hi_output, ASR_output