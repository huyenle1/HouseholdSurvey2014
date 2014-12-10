# Queries for factors influencing walking, bike, and transit use
# Segmented by regional center, major center, and non-center

import pandas as pd
import numpy as np
import HHSurveyToPandas as survey_df    # Load survey data

# Load the survey data per HHSurveyToPandas.py
household = survey_df.load_survey_sheet(survey_df.household_file, survey_df.household_sheetname)
vehicle = survey_df.load_survey_sheet(survey_df.vehicle_file, survey_df.vehicle_sheetname)
person = survey_df.load_survey_sheet(survey_df.person_file, survey_df.person_sheetname)
trip = survey_df.load_survey_sheet(survey_df.trip_file, survey_df.trip_sheetname)

# Merge household records to person file
person_hh = pd.merge(person, household, left_on=['hhid'], right_on=['hhid'], suffixes=('_per', '_hh'))

# Merge person-household records to trip file
trip_person_hh = pd.merge(trip, person_hh, left_on=['personID'], 
                          right_on=['personid'], suffixes=('_trip', '_person_hh'))

# Send to clipboard for pasting into Excel
def outclip(file):
    file.to_clipboard()

# Factors influencing mode choice

# wbt_transitsafety
# Walk, bike or ride transit more if: Safer ways to get to transit stops (e.g. more sidewalks, lighting, etc.)

# By regional growth centers
wbt_transitsafety_rgc = pd.pivot_table(person_hh, values='expwt_final_per', rows='h_rgc_name', 
                                    columns='wbt_transitsafety', aggfunc=np.sum)

# wbt_transitfreq
# Walk, bike or ride transit more if: Increased frequency of transit (e.g. how often the bus arrives)
wbt_transitfreq_rgc = pd.pivot_table(person_hh, values='expwt_final_per', rows='h_rgc_name', 
                                    columns='wbt_transitfreq', aggfunc=np.sum)

# wbt_reliability
# Walk, bike or ride transit more if: Increased reliability of transit (e.g. the bus always arrives at exactly the scheduled time)
wbt_reliability_rgc = pd.pivot_table(person_hh, values='expwt_final_per', rows='h_rgc_name', 
                                    columns='wbt_reliability', aggfunc=np.sum)

# wbt_bikesafety
# Walk, bike or ride transit more if: Safer bicycle routes (e.g. protected bike lanes)
wbt_bikesafety_rgc = pd.pivot_table(person_hh, values='expwt_final_per', rows='h_rgc_name', 
                                    columns='wbt_bikesafety', aggfunc=np.sum)

# wbt_walksafety
# Walk, bike or ride transit more if: Safer walking routes (e.g. more sidewalks, protected crossings, etc.)
wbt_walksafety_rgc = pd.pivot_table(person_hh, values='expwt_final_per', rows='h_rgc_name', 
                                    columns='wbt_walksafety', aggfunc=np.sum)

# wbt_other
# Walk, bike or ride transit more if: Other
wbt_other_rgc = pd.pivot_table(person_hh, values='expwt_final_per', rows='h_rgc_name', 
                                    columns='wbt_other', aggfunc=np.sum)

# wbt_none
# Walk, bike or ride transit more if: None of these would get me to walk, bike, and/or take transit more
wbt_none_rgc = pd.pivot_table(person_hh, values='expwt_final_per', rows='h_rgc_name', 
                                    columns='wbt_none', aggfunc=np.sum)

# wbt_na
# Walk, bike or ride transit more if: Not applicable  I already regularly walk, bike, and/or take transit
wbt_na_rgc = pd.pivot_table(person_hh, values='expwt_final_per', rows='h_rgc_name', 
                                    columns='wbt_na', aggfunc=np.sum)