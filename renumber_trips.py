﻿import pandas as pd
import numpy as np
import config
import process_survey as ps


# We will still need to reset to trip ids on the trip file by concatenating the fields
# new_trip_num and personID

# Load the survey data per process_survey.py
trip = ps.load_data(config.trip_file)
person = ps.load_data(config.person_file)
household = ps.load_data(config.household_file)



trip.sort(['personID', 'tripID'], inplace=True)

# Group the particular list of trips beloning to a person
persons_trips = trip.groupby('personID')

# Reset the trip numbers of the people
trip['new_trip_num'] = persons_trips.cumcount()+1

#Now get the new total number of trips for this person
trip_newindex = trip.set_index('personID', drop=False)
trip_newindex['new_total_trip'] = persons_trips.size()

trip_newindex.to_csv(base_path + "\\new_trip_out.csv")


persons_tottrips = pd.DataFrame()
persons_tottrips['personID']= persons_trips.count().index
persons_tottripsnewix = persons_tottrips.set_index('personID', drop=False)
persons_tottripsnewix ['numtrips']= persons_trips.size()


# Update the persons table with the new number of trips
person_newnumtrips = pd.merge(person, persons_tottripsnewix, left_on = 'personid', right_on = 'personID', how = 'left')

person_newnumtrips.to_csv(base_path + '\\new_persons_out.csv', encoding = 'utf-8')

#update the households table with the sum of the person trips in the
#household

hh_tripnewix = trip_newindex.set_index('hhid', drop=False)
hh_trips_grouped = hh_tripnewix.groupby('hhid')

persons_tottrips = pd.DataFrame()
persons_tottrips['personID']= persons_trips.count().index
persons_tottripsnewix = persons_tottrips.set_index('personID', drop=False)
persons_tottripsnewix ['numtrips']= persons_trips.size()

hh_newtrips = pd.DataFrame()
hh_newtrips['hhid'] = hh_trips_grouped.count().index
hh_newtrips.set_index('hhid', drop=False, inplace=True)
hh_newtrips['new_hh_trip']=hh_trips_grouped.size()

hh_newnumtrips = pd.merge(hh_newtrips, household, left_on = 'hhid', right_on = 'hhid', how = 'right')

hh_newnumtrips.to_csv(base_path + '\\new_households_out.csv', encoding = 'utf-8')


 