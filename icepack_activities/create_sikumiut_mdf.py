"""
Code 'recipe' for generating the atmospheric forcing for Sikumiut Icepack 
activities.

It should not be necessary for participants to run this script, but it is
included here for completeness in case someone wants to regenerate the forcing
data
"""

import os
import xarray as xr
import pandas as pd
import numpy as np

# Load mdf_toolkit
# if this is first time running, go to the root of the mdf-toolkit directory
# in this same conda environment
# and run ```pip install -e .``` first
from mdftoolkit.MDF_toolkit import MDF_toolkit as MDF

## Load preprocessed NSA QCRAD data
data_in_path = os.path.join('~', 'data', 'sikumiut')
filename = 'nsaqcrad1longC1.cl.subset.20241001_20250405.nc'
ds_in = xr.open_dataset(os.path.join(data_in_path, filename))

# Data Citation:
cite = '''Zhang, D. Data Quality Assessment for ARM Radiation Data (QCRAD1LONG),
2024-10-01 to 2025-03-25, North Slope Alaska (NSA), Central Facility, Barrow AK
(C1). Atmospheric Radiation Measurement (ARM) User Facility.
https://doi.org/10.5439/1027372
'''

# Convert to pandas dataframe
df_out = ds_in.to_dataframe()

# Assume all precipitation is snowfall
df_out['snowfall_rate'] = df_out['precip_rate']
# Clip negative shortwave values
df_out['BestEstimate_down_short_hemisp'][
    df_out.BestEstimate_down_short_hemisp < 0] = 0.0
# Convert temperature to Kelvin
df_out['Temp_Air'] += 273.15
# Convert pressure from kPa to hPa
df_out['press'] *= 10.0

def calc_mix_ratio(temp, RHw, press):
    """
    Function for calculating mixing ratio from C. Cox

    !!! Temperature must be in Kelvin !!!


    Calculations based on Appendix B of the PTU/HMT manual to be mathematically consistent with the
    derivations in the on onboard electronics. Checked against Ola's code and found acceptable
    agreement (<0.1% in MR). RHi calculation is then made following Hyland & Wexler (1983), which
    yields slightly higher (<1%) compared a different method of Ola's
    """
    
    # calculate saturation vapor pressure (Pws) using two equations sets, Wexler (1976) eq 5 & coefficients
    c0    = 0.4931358
    c1    = -0.46094296*1e-2
    c2    = 0.13746454*1e-4
    c3    = -0.12743214*1e-7
    omega = temp - ( c0*temp**0 + c1*temp**1 + c2*temp**2 + c3*temp**3 )

    # eq 6 & coefficients
    bm1 = -0.58002206*1e4
    b0  = 0.13914993*1e1
    b1  = -0.48640239*1e-1
    b2  = 0.41764768*1e-4
    b3  = -0.14452093*1e-7
    b4  = 6.5459673
    Pws = np.exp( ( bm1*omega**-1 + b0*omega**0 + b1*omega**1 + b2*omega**2 + 
                   b3*omega**3 ) + b4*np.log(omega) ) # [Pa]

    Pw = RHw*Pws/100 # # actual vapor pressure (Pw), eq. 7, [Pa]

    x = 1000*0.622*Pw/((press*100)-Pw) # mixing ratio by weight (eq 2), [g/kg]

    return x

# Create mixing ratio and specific humidity columns
df_out['mixing_ratio'] = calc_mix_ratio(df_out.Temp_Air, df_out.rh,
                                           df_out.press)
df_out['specific_humidity'] = (df_out.mixing_ratio/1000)/(
    1 + df_out.mixing_ratio/1000)


# Specify which variables correspond to MDF var names
var_map_dict = {'lat'   : 'lat',
                'lon'   : 'lon',
                'uas'   : 'wind_u',
                'vas'   : 'wind_v',
                'tas'   : 'Temp_Air',
                'hus'   : 'specific_humidity',
                'rlds'  : 'down_long_hemisp',
                'rsds'  : 'BestEstimate_down_short_hemisp',
                'pr'    : 'precip_rate',
                'prsn'  : 'snowfall_rate',
                }

## Convert into MDF
MDF_out = MDF(supersite_name='sikumiut', verbose=True)
global_atts = {
    "title"                    : "Sikumiut Icepack atmospheric forcing",
    "Conventions"              : "MDF, CF (where possible)",
    "creator_name"             : "David Clemens-Sewall",
    "creator_email"            : "davidclemenssewall@gmail.com",
    "project"                  : "Sikumiut sea ice field school",
    "summary"                  : "Hourly atmospheric forcing for Icepack from ARM measurements",
    "id"                       : "TBD",
    "license"                  : "CC-0", 
    "metadata_link"            : "TBD",
    "references"               : cite,
    "time_coverage_start"      : "{}".format(df_out.index[0]),
    "time_coverage_end"        : "{}".format(df_out.index[-1]),
    "naming_authority"         : "___", 
    "standard_name_vocabulary" : "___", 
    "keywords"                 : "surface energy budget, arctic, polar",
    "calendar"                 : "standard",
}
MDF_out.update_global_atts(global_atts)  

modf_df = MDF.map_vars_to_mdf(df_out, var_map_dict, drop=True)
MDF_out.add_data_timeseries(modf_df, cadence="time60")
MDF_out.write_files(output_dir=os.path.join(os.getcwd(), 'data/'),
                    fname_only_underscores=True)

### Below here is for creating the pseudo-precipitation forcing to best match
# the observed 5 (ish) cm snow depth on the ice
# As a simple way of doing this, let's zero out all precip
# before Nov. 22 and after Dec. 22
df_out_ns = df_out.copy(deep=True)
pr_start = "2024-11-22"
pr_end = "2024-12-22"
df_out_ns['precip_rate'].loc[:pr_start] = 0.0
df_out_ns['precip_rate'].loc[pr_end:] = 0.0
df_out_ns['snowfall_rate'].loc[:pr_start] = 0.0
df_out_ns['snowfall_rate'].loc[pr_end:] = 0.0

## Convert into MDF
MDF_out = MDF(supersite_name='sikumiut_nearshore', verbose=True)
global_atts = {
    "title"                    : "Sikumiut Icepack atmospheric forcing",
    "Conventions"              : "MDF, CF (where possible)",
    "creator_name"             : "David Clemens-Sewall",
    "creator_email"            : "davidclemenssewall@gmail.com",
    "project"                  : "Sikumiut sea ice field school",
    "summary"                  : "Hourly atmospheric forcing for Icepack from"+
                                 " ARM measurements. Precipitation is only " +
                                 "from Nov. 22 to Dec. 22 to approximate " +
                                 "effects of wind-drive snow redistribution.",
    "id"                       : "TBD",
    "license"                  : "CC-0", 
    "metadata_link"            : "TBD",
    "references"               : cite,
    "time_coverage_start"      : "{}".format(df_out_ns.index[0]),
    "time_coverage_end"        : "{}".format(df_out_ns.index[-1]),
    "naming_authority"         : "___", 
    "standard_name_vocabulary" : "___", 
    "keywords"                 : "surface energy budget, arctic, polar",
    "calendar"                 : "standard",
}
MDF_out.update_global_atts(global_atts)  

modf_df = MDF.map_vars_to_mdf(df_out_ns, var_map_dict, drop=True)
MDF_out.add_data_timeseries(modf_df, cadence="time60")
MDF_out.write_files(output_dir=os.path.join(os.getcwd(), 'data/'),
                    fname_only_underscores=True)
