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

# Load mdf_toolkit
# if this is first time running, go to the root of the mdf-toolkit directory
# in this same conda environment
# and run ```pip install -e .``` first
from mdftoolkit.MDF_toolkit import MDF_toolkit as MDF

## Load preprocessed NSA QCRAD data
data_in_path = os.path.join('~', 'data', 'sikumiut')
filename = 'nsaqcrad1longC1.cl.subset.20241001_20250325.nc'
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