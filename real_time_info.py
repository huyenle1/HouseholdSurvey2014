# Queries for real-time information and smartphone usage

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

# Get metadata - number of samples per regional center
#metadata = 

# Replace NaN for regional centers to count number of responses not in centers
person_hh = person_hh.fillna(-1)

# Impact of real-time information
# By regional growth centers

# Travel info impact on travel plans: I make the same trip I was planning, but it is less stressful
# impact_sametrip
impact_sametrip_rgc = pd.pivot_table(person_hh, values='expwt_final_per', rows='h_rgc_name', 
                                    columns='impact_sametrip', aggfunc=np.sum)

# Travel info impact on travel plans: I start my trip earlier
# impact_earlier
impact_earlier_rgc = pd.pivot_table(person_hh, values='expwt_final_per', rows='h_rgc_name', 
                                    columns='impact_earlier', aggfunc=np.sum)


# Travel info impact on travel plans: I start my trip later
# impact_later
impact_later_rgc = pd.pivot_table(person_hh, values='expwt_final_per', rows='h_rgc_name', 
                                    columns='impact_later', aggfunc=np.sum)

# Travel info impact on travel plans: I choose a completely different route than originally planned
# impact_diffroute
impact_diffroute_rgc = pd.pivot_table(person_hh, values='expwt_final_per', rows='h_rgc_name', 
                                    columns='impact_diffroute', aggfunc=np.sum)

# Travel info impact on travel plans: I take my planned route, but with small changes to avoid congestion
# impact_smallchange
impact_smallchange_rgc = pd.pivot_table(person_hh, values='expwt_final_per', rows='h_rgc_name', 
                                    columns='impact_smallchange', aggfunc=np.sum)

# Travel info impact on travel plans: I choose a different travel mode (e.g. I take the bus instead of driving)
# impact_diffmode
impact_diffmode_rgc = pd.pivot_table(person_hh, values='expwt_final_per', rows='h_rgc_name', 
                                    columns='impact_diffmode', aggfunc=np.sum)

# Travel info impact on travel plans: I postpone or cancel my trip
# impact_postpone
impact_postpone_rgc = pd.pivot_table(person_hh, values='expwt_final_per', rows='h_rgc_name', 
                                    columns='impact_postpone', aggfunc=np.sum)

# Travel info impact on travel plans: I change the number or order of the stops I plan to make on my trip
# impact_order
impact_order_rgc = pd.pivot_table(person_hh, values='expwt_final_per', rows='h_rgc_name', 
                                    columns='impact_order', aggfunc=np.sum)