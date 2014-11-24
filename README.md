HouseholdSurvey2014
===================

These scripts import PSRC's 2014 household survey from spreadsheets to Python Pandas dataframes.

Spreadsheet data should be saved in the same directory as the scripts. 

"HHSurveyToPandas.py" is the primary script that loads data into memory. It compiles the following data.


Variables:

Household:		 Household file (DataFrame)
Vehicle:		 Vehicle file (DataFrame)
Person:			 Person file (DataFrame)
Trip:			 Trip file (DataFrame)

HHPer:			 Merge of household and person files (DataFrame)
HHPerTrip:		 Merge of household, person, and trip files (DataFrame)
num_households: 	 Number of Households (float)
num_people: 		 Number of People (float)
num_trips:		 Number of Trips (float)
trip_ok:		 Subset of HHPerTrip where the trip length is between 0 and 200 miles (DataFrame)
average_trip_length:	 Average trip length of trips in trip_ok (float)

mode_share:		 Mode share for all trips (Series)
mode_share_df:		 Data frame with weighted and unweighted mode share (DataFrame)
purpose_share:		 Purpose share for all trips (Series)
purpose_share_df:	 Data frame with weighted and unweighted purpose share (DataFrame)
non_home_trips:		 Subset of HHPerTrip where the destination purpose is not going home (DataFrame)
num_non_home_trips:	 The number of non-home trips (float)

trips_to_work:		 Subset of HHPerTrip where the destination purpose is to go to work (DataFrame)
num_work_trips:		 Number of work trips (float)
work_trip_mode_share:	 Mode share for trips to work (Series)
work_trip_mode_share_df: Data frame with weighted and unweighted work trip mode share (DataFrame)

For all float and series variables, the associated unweighted variable can be called by adding "_unweighted" to the variable name


Functions:

round_add_percent (float)
Rounds a floating point number to the nearest hundredth and adds a percent sign, returning a string
Example: round_add_percent(1.23) = '1.23%'

remove_percent(string)
Removes a percent sign from a string and returns a floating point number
Example: remove_percent('4.5%') = 4.5

get_mode_share(DataFrame, grouper = string, weighted = Boolean: True)
Obtains the weighted or unweighted mode share grouped by a variable

get_mode_share_06(DataFrame, grouper = string, weighted = Boolean: True)
Like get_mode_share, but for the 2006 survey data in h5 format

weighted_average(DataFrame, column = string, weights = string, grouper = string)*
Returns the weighted average of the specified column of a data frame. Grouping by another variable is optional
(Set grouper = None (default) if no grouping is to be done)
Returns a series if grouping is done and a floating point number if not

weighted_variance(DataFrame, column = string, weights = string)*
Returns the weighted variance of the specified column of a data frame.

weighted_skew(DataFrame, column = string, weights = string)*
Returns the weighted skewness of the specified column of a data frame.

weighted_kurtosis(DataFrame, column = string, weights = string, excess = Boolean: True)*
Returns the weighted kurtosis of the specified column of a data frame. If excess is set to true then the excess kurtosis will be computed.

*weighted moment functions based on the formulas found at http://www.nematrian.com/R.aspx?p=WeightedMomentsAndCumulants

recode_index(DataFrame, old_name = string, new_name = string)
Recodes the name of the index

min_to_hour(input, base):
Converts minutes since base hour to hour of day
Examples: min_to_hour(0, 3) = '03-04'; min_to_hour(390, 3) = '09-10'; min_to_hour(390, 0) = '06-07'; min_to_hour(720, 3) = '15-16'

all_same(items)
Checks if all of the items in a list or series are the same
Examples: all_same([1, 1, 1]) = True; all_same([1, 2, 3]) = False


File-creating functions:

school_issue(Trip_File, Person_File)
Checks among the data which records have the issue of kids driving to school. Creates an Excel file

timeshareplot()
Creates a time share histogram. Matplotlib is required

get_outliers(dist, time, speed)
Creates an Excel file with travel distances, times, and speeds greater than the specified criteria

Movers(HHPer, HHPerTrip):
Creates an Excel file with people who started and ended their day in different locations


