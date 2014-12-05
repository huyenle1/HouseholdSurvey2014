# Queries realted to telecommuting
# Segmented by county, age, and income

import pandas as pd
import numpy as np
import HHSurveyToPandas as survey_df    # Load survey data
from survey_queries import outclip

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

# --- Pivot Table Queries ---
# 
# Aggregating on expwt sums to represent total households, not just survey results


# --- Telecommute ---
# On travel date: Worked from home or telecommuted for any part of the day
telecommute_by_county = pd.pivot_table(person_hh, values='expwt_final_per', index='telecommute', 
                                    columns='h_county_name', aggfunc=np.sum)
telecommute_by_age = pd.pivot_table(person_hh, values='expwt_final_per', index='telecommute', 
                                    columns='age', aggfunc=np.sum)
telecommute_by_inc = pd.pivot_table(person_hh, values='expwt_final_per', index='telecommute', 
                                    columns='hh_income_detailed', aggfunc=np.sum)

# How often telecommute
telecommute_freq_by_county = pd.pivot_table(person_hh, values='expwt_final_per', index='telecommute_freq', 
                                    columns='h_county_name', aggfunc=np.sum)
telecommute_freq_by_age = pd.pivot_table(person_hh, values='expwt_final_per', index='telecommute_freq', 
                                    columns='age', aggfunc=np.sum)
telecommute_freq_by_inc = pd.pivot_table(person_hh, values='expwt_final_per', index='telecommute_freq', 
                                    columns='hh_income_detailed', aggfunc=np.sum)