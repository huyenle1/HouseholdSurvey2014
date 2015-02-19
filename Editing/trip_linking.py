import pandas as pd
import numpy as np
import HHSurveyToPandas as survey_df    # Load survey data
import process_survey as ps

# Load the survey data per HHSurveyToPandas.py
trip = survey_df.load_survey_sheet(survey_df.trip_file, survey_df.trip_sheetname)

# List of unique personIDs
uniquePersonIDs = trip.groupby('personID').count().index

# First find the people whose mode changes at all between trips
# Loop through each person in the survey

# Ignore trips that are drop-off/pick-up. These might indicate a mode change (SOV to HOV 2 or 3+) but we
# don't want them to be linked. 

# Max size of trip sets
trip_set_max = 4

# Make sure the trip file is sorted by Trip ID first!
trip.sort('tripID', inplace=True)

problem_trips = []
person_counter = 0
for person in uniquePersonIDs:
    flag = 1
    #print person_counter
    trip_subsample = trip.query("personID == " + str(person))
    #trip_subsample = trip.query("personID == 1410000801")
    # If there are no mode changes for all trips, ignore this person's trips
    if len(set(trip_subsample['mode'])) > 1:
        # Loop through each person's trips
        for row in xrange(0, len(trip_subsample)-1):
            person_trip = trip_subsample.iloc[row]
            next_pers_trip = trip_subsample.iloc[row+1]

            # Are these 2 trips unlinked?
            # Ignore drop-off/pick-up. These might indicate a mode change (SOV to HOV 2 or 3+) but we don't want them to be linked. 
            # Also ignore purpose of mode transfer.
            # Also ignore bus-bus trips
            if (    (person_trip['mode'] <> next_pers_trip['mode']          # Include mode changes
                or  (person_trip['mode'] == next_pers_trip['mode'] == 8))   # Include bus-to-bus transfer
                and person_trip['a_dur'] <= 15                                             
                and (   person_trip['d_purpose'] == next_pers_trip['d_purpose']     # Trip purp must be the same
                     or person_trip['d_purpose'] == 15)                     # or purp listed as "mode change"
                and person_trip['d_purpose'] <> 9                           # Exclude drop-off/pick-up trips
                or person_trip['d_purpose'] == 15 and next_pers_trip['mode'] <> 16  # Include all mode changes except planes
                ):
                # If this looks unlinked, flag it
                problem_trips.append(["%05d" % (person_counter,) + "%02d" % (flag,), person_trip['tripID']])
                problem_trips.append(["%05d" % (person_counter,) + "%02d" % (flag,), next_pers_trip['tripID']])

                # Is this trip part of an existing linked trip pair or a new trip pair?
                # Is the activity duration longer 30 minutes? Then it's probably a separate commute trip
                if next_pers_trip['a_dur'] > 30:
                    flag += 1

    person_counter += 1

# In the returned array, the first column is a concatentation of person ID in the first 5 columns and the last 2 columns contain the index of the linked trip for each person
   
print len(problem_trips)

# Join the problem_trips flags to the regular trip file
problem_trips_df = pd.DataFrame(problem_trips,columns=['linked_flag', 'tripID'])
merged_trips = pd.merge(left=trip,right=problem_trips_df,on='tripID',left_index=True,how='outer')
merged_trips.drop_duplicates(inplace=True) # Remove duplicates
merged_trips.fillna(0, inplace=True)

# Isolate unlinked trips
unlinked_trips = merged_trips.query("linked_flag <> 0")

# List of all linked trip sets and the number of records in each
unlinked_sets = unlinked_trips.groupby('linked_flag').count()['recordID']

# Summary statistics on linked trip sets - gives us an idea of how well we identified linked trips
setsize = {}
for idx in list(unlinked_sets.index):
     # Examine each set of linked trips
     trip_set = unlinked_trips[unlinked_trips['linked_flag'] == idx]
     setsize[idx] = len(trip_set)

# Find distribution of set sizes
df_setsize = pd.DataFrame([setsize.keys(), setsize.values()]).T
setsize_dist = df_setsize.groupby(1).count()   # Distribution of set size

# Distribution shows that most (90%) of sets are 2 or 3 trips only. Let's automatically join these only and do the others manually. 
# Discard sets with more than 3 trips because these are too unusual
#linked_list = linked_list[linked_list <= 3]

unlinked_trips_df = pd.DataFrame(unlinked_trips)
unlinked_trips_df.index = unlinked_trips.linked_flag    # Change index to work with the flag

# Get mode combination for each set
unlinked_trips_df['mode'] = unlinked_trips_df['mode'].astype("int64")   # Convert from float to int first
unlinked_trips_df['mode'] = pd.DataFrame(unlinked_trips_df['mode'].astype("str"))     # Convert to string
# Create new column with concatentation of modes
unlinked_trips_df['combined_modes'] = unlinked_trips_df.groupby('linked_flag').apply(lambda x: '-'.join(x['mode']))

# Filter out sets with more than 4 unlinked trip and flag them for manual inspection
# The name "..._max4" is poorly titled. The max set size is now flexible so that greater or fewer 
unlinked_trips_max4 = unlinked_trips_df[unlinked_trips_df['combined_modes'].str.count('-') < trip_set_max]

sum_fields = ['gdist', 'gtime', 'trip_dur_reported']

# Convert to consistent type - float 64
for field in sum_fields:
    unlinked_trips_max4[field] = unlinked_trips_max4[field].astype("float64")

# Convert transitline data into integer
for field in ['transitline' + str(x) for x in xrange(1,5)]:
    unlinked_trips_max4[field] = unlinked_trips_max4[field].astype("int")

# Get the sums of trips grouped by each person's set
sums = unlinked_trips_max4.groupby('linked_flag').sum()

# Now we want to squish those unlinked trips together!
# The "primary trip" will inherit characeristics of associated trips
# Return list of primary trips and max distance for each set
#primary_trips = linked_trips_df.groupby('linked_flag').max()[['tripID','gdist']]

# change index to be trip ID because this is the number we ultimately want
df = pd.DataFrame(unlinked_trips_max4)
df.index = unlinked_trips_max4['tripID']
# Find the trip ID of the longest trip in each set
primary_trips = pd.DataFrame(df.groupby('linked_flag')['gdist'].agg(lambda x: x.idxmax()))
#unlinked_trips_max4.groupby('linked_flag')

# Select only the primary trip from each set
primary_trips_df = unlinked_trips_max4[df['tripID'].isin(primary_trips['gdist'])]
primary_trips_df.index = primary_trips_df.linked_flag   # Reset index to trip set ID

# Change primary trip start time to time of first in linked trip set
for field in ['time_start_mam', 'time_start_hhmm', 'o_purpose', 'place_start', 'ocity', 'ocnty', 'ozip', 'address_start', 'olat', 'olng']:
    # Save the original data in a new column
    primary_trips_df.loc[:,field + '_original'] = primary_trips_df[field]
    primary_trips_df.loc[:,field] = df.groupby('linked_flag').apply(lambda x: x[field].iloc[0])

# Change primary trip start time to time of last in linked trip set
# Change primary purpose and activity duration to that of the last trip in the set
for field in ['time_end_hhmm', 'time_end_hhmm', 'a_dur', 'd_purpose', 'place_end', 'dcity', 'dcnty', 'dzip', 'address_end', 'dlat', 'dlng']:
    # Save the original data in a new column
    primary_trips_df.loc[:,field + '_original'] = primary_trips_df[field]
    primary_trips_df.loc[:,field] = df.groupby('linked_flag').apply(lambda x: x[field].iloc[-1])
    
for field in sum_fields:
    # Save original primary trip info in a new column appened with "_original"
    primary_trips_df.loc[:,field + '_original'] = primary_trips_df[field]
    # Replace the primary trip fields with summed data
    primary_trips_df.loc[:,field] = sums[field]


## Save transitline data into primary trip record
#tr1 = pd.DataFrame(df.groupby('linked_flag')[['transitline1']].agg(lambda x: x.tolist()))
## Create new column to store unique transitline trips
#for each in ['transitline' + str(x) for x in xrange(1,5)]:
#    primary_trips_df[each + '_list'] = ""
#tr2 = pd.DataFrame(df.groupby('linked_flag')['transitline2'].agg(lambda x: x.tolist()))

# this returns greater than zero values for a single row - a single list of a list

# Collect all transitline1 values for a set in a single array
tr1 = pd.DataFrame(df.groupby('linked_flag')[['transitline1']].agg(lambda x: x.tolist()))
tr2 = pd.DataFrame(df.groupby('linked_flag')[['transitline2']].agg(lambda x: x.tolist()))
tr3 = pd.DataFrame(df.groupby('linked_flag')[['transitline3']].agg(lambda x: x.tolist()))
tr4 = pd.DataFrame(df.groupby('linked_flag')[['transitline4']].agg(lambda x: x.tolist()))
ts1 = pd.DataFrame(df.groupby('linked_flag')[['transitsystem1']].agg(lambda x: x.tolist()))
ts2 = pd.DataFrame(df.groupby('linked_flag')[['transitsystem2']].agg(lambda x: x.tolist()))
ts3 = pd.DataFrame(df.groupby('linked_flag')[['transitsystem3']].agg(lambda x: x.tolist()))
ts4 = pd.DataFrame(df.groupby('linked_flag')[['transitsystem4']].agg(lambda x: x.tolist()))

# Add together all the transitline values (1 through 4)
combined_transitlines = pd.DataFrame(tr1['transitline1'] + tr2['transitline2'] + tr3['transitline3'] + tr4['transitline4'])
combined_transitsys = pd.DataFrame(ts1['transitsystem1'] + ts2['transitsystem2'] + ts3['transitsystem3'] + ts4['transitsystem4'])
#combined_transitlines[0].iloc[0]

combined_transitlines["tr1"] = ""
combined_transitlines["tr2"] = ""
combined_transitlines["tr3"] = ""
combined_transitlines["tr4"] = ""
combined_transitsys["ts1"] = ""
combined_transitsys["ts2"] = ""
combined_transitsys["ts3"] = ""
combined_transitsys["ts4"] = ""

# Number of columns for transit lines or transit systems (4 in 2014 survey design)
num_transitlines = 4
num_transys = 4

for row in xrange(0, len(combined_transitlines)):
    # Add all unlinked trips' transitline data into a list
    combined_transitlines[0].iloc[row] = list(set(combined_transitlines[0].iloc[row]))  #[0] selects df column
    combined_transitsys[0].iloc[row] = list(set(combined_transitsys[0].iloc[row]))  #[0] selects df column
    # Remove zeros that might be at beginning of the list
    combined_transitlines[0].iloc[row] = [x for x in combined_transitlines[0].iloc[row] if x != 0]
    combined_transitsys[0].iloc[row] = [x for x in combined_transitsys[0].iloc[row] if x != 0]
    # But we want to pad the rest with zeros for consistent array shape
    combined_transitlines[0].iloc[row] = np.pad(combined_transitlines[0].iloc[row],
                                                (0,num_transitlines-len(combined_transitlines[0].iloc[row])),
                                                mode='constant')
    combined_transitsys[0].iloc[row] = np.pad(combined_transitsys[0].iloc[row],
                                                (0,num_transitlines-len(combined_transitsys[0].iloc[row])),
                                                mode='constant')

    for i in xrange(4):
        combined_transitlines["tr" + str(i + 1)].iloc[row] = combined_transitlines[0].iloc[row][i]
        combined_transitsys["ts" + str(i + 1)].iloc[row] = combined_transitsys[0].iloc[row][i]

# Add the transitline values to the primary trip record
for i in xrange(1,5):
    primary_trips_df['transitline' + str(i)] = combined_transitlines['tr' + str(i)]
    primary_trips_df['transitsystem' + str(i)] = combined_transitsys['ts' + str(i)]

# Do the same for transitsystem

#a = nonzero(tr1.loc['1054601'][0] + tr2.loc['1054601'][0] + tr3.loc['1054601'][0] + tr4.loc['1054601'][0]))

#for row in xrange(len(tr1)):
#    a = tr1.iloc[row][0]
#    b = tr2.iloc[row][0]
#    c = tr3.iloc[row][0]
#    d = tr4.iloc[row][0]
#    print a
#    # add in the newlist to a column for each linked trip
#    newlist = []
#    for each in [a, b, c, d]:
#        for col in each:
#            if col > 0:
#                newlist.append(col)
#    primary_trips_df['transitline1' + '_list'].iloc[row] = newlist

# Add trips from transit

# Trips with all unlinked trips removed
# note the "-trip" call to grab inverse of selection, so we're getting all survey trips NOT in unlinked_trips_df
trip_unlinked_removed_all = trip[-trip['tripID'].isin(unlinked_trips_df.tripID)]   # ALL unlinked trips removed

# Trips with all linked trips added (and unlinked trips removed)
trip_with_linked = pd.concat([trip_unlinked_removed_all,primary_trips_df])

# List of still unlinked trips - these still need to be addressed
unprocessed_unlinked_trips = unlinked_trips_df[unlinked_trips_df['combined_modes'].str.count('-') >= trip_set_max]

# Distribution of combined trip modes
a = primary_trips_df.groupby('combined_modes').count()['recordID']

# Send to excel
writer = pd.ExcelWriter('trip_linking.xlsx')

# Trip file with ALL unlinked files removed and new linked trips added
trip_with_linked.to_excel(writer, "Linked Trips Combined")

# Trips with ALL unlinked trips removed
trip_unlinked_removed_all.to_excel(writer, 'All Unlinked Trips Removed')

# Linked Trips only
# Join with regular trip file data
primary_trips_df.to_excel(writer, 'Linked Trips Only')

# Unlinked Trips only
unlinked_trips_df.to_excel(writer, 'Unlinked Trips Only')

# List of unprocessed unlinked trips
unprocessed_unlinked_trips.to_excel(writer, "Unprocessed Unlinked Trips")

# Unlinked trips that need to be edited by hand
writer.close()