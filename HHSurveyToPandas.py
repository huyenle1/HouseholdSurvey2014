import pandas as pd
import numpy as np
import time
import h5toDF
import imp
import scipy.stats as stats
import math

location = '[INSERT FILE LOCATION HERE]'
household_file = '[INSERT HOUSEHOLD FILEPATH HERE]'
vehicle_file = '[INSERT VEHICLE FILEPATH HERE]'
person_file = '[INSERT PERSON FILEPATH HERE]'
trip_file = '[INSERT TRIP FILEPATH HERE]'
work_distance_file = '[INSERT WORK DISTANCE FILEPATH HERE]'
school_distance_file = '[INSERT SCHOOL DISTANCE FILEPATH HERE]'
guide_file = '[INSERT GUIDE FILEPATH HERE]'

#Checks if matplotlib is installed
try:
    imp.find_module('matplotlib')
    found = True
except ImportError:
    found = False
if found:
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    import matplotlib

def round_add_percent(number): #Rounds a floating point number and adds a percent sign
    if type(number) == str or type(number) == None:
        raise ValueError("Hey! That's not a number!")
    outnumber = str(round(number, 2)) + '%'
    return outnumber

def remove_percent(input = str): #Removes a percent sign at the end of a string to get a number
    if input[len(input) - 1] != '%':
        raise TypeError("The function is called 'remove_percent.' I recommend that you give me something that ends with a percent sign. It just might work a little better.")
    try:
        output = float(input[:len(input) - 1])
        return output
    except ValueError:
        raise TypeError("Woah, " + input + "'s not going to work. I need a string where everything other than the last character could be a floating point number.")

#This function gets the mode share grouped by a specified variable. Can be weighted or unweighted
def get_mode_share(df, grouper = None, weighted = True):
    if not isinstance(df, pd.DataFrame):
        raise TypeError("The first argument isn't a data frame. I refuse to work!")
    modes = df['mode'].value_counts().index.tolist() #List of different modes in set
    if grouper == None:
        if weighted:
            mode_trips = df[['mode', 'expwt_final']].groupby('mode').sum()['expwt_final'] #Add up expansion weights by mode
            total_trips = df['expwt_final'].sum()
        else:
            mode_trips = df[['mode', 'expwt_final']].groupby('mode').count()['expwt_final'] #Count number of entries by mode
            total_trips = df['expwt_final'].count()
        mode_share = mode_trips / total_trips * 100
        mode_share = mode_share.fillna(0)
        mode_share = mode_share.apply(round_add_percent)
        return mode_share
    else:
        #Get total number of trips by category
        if weighted:
            mode_trips_by_grouper = df[[grouper, 'mode', 'expwt_final']].groupby(['mode', grouper]).sum()[['expwt_final']]
        else:
            mode_trips_by_grouper = df[[grouper, 'mode', 'expwt_final']].groupby(['mode', grouper]).count()[['expwt_final']]
        mode_trips_by_grouper = mode_trips_by_grouper.reset_index()
        mode_trips_by_grouper = mode_trips_by_grouper.pivot(index = 'mode', columns = grouper, values = 'expwt_final') #Creates a pivot table
        #Get total trips
        if weighted:
            total_trips_by_grouper = df[[grouper, 'expwt_final']].groupby(grouper).sum()['expwt_final']
        else:
            total_trips_by_grouper = df[[grouper, 'expwt_final']].groupby(grouper).count()['expwt_final']
        mode_share_by_grouper = pd.DataFrame(index = modes, columns = mode_trips_by_grouper.columns)
        #Divide trips by category by total number of trips to get share
        for group in mode_share_by_grouper.columns:
            for mode in modes:
                try:
                    mode_share_by_grouper.loc[mode, group] = mode_trips_by_grouper.loc[mode, group] / total_trips_by_grouper[group] * 100
                except LookupError:
                    continue
            mode_share_by_grouper[group] = mode_share_by_grouper[group].fillna(0)
            mode_share_by_grouper[group] = mode_share_by_grouper[group].apply(round_add_percent)
        return mode_share_by_grouper

def get_mode_share_06(df, grouper = None, weighted = True): #Function that gets the mode share from the 2006 data in h5 format
    if not isinstance(df, pd.DataFrame):
        raise TypeError("The first argument isn't a data frame. I refuse to work!")
    modes = df['mode'].value_counts().index.tolist() #List of different modes in set
    if grouper == None:
        if weighted:
            mode_trips = df[['mode', 'trexpfac']].groupby('mode').sum()['trexpfac']
            total_trips = df['trexpfac'].sum()
        else:
            mode_trips = df[['mode', 'trexpfac']].groupby('mode').count()['trexpfac']
            total_trips = df['trexpfac'].count()
        mode_share = mode_trips / total_trips * 100
        mode_share = mode_share.fillna(0)
        mode_share = mode_share.apply(round_add_percent)
        return mode_share
    else:
        #Get total number of trips by category
        if weighted:
            mode_trips_by_grouper = df[[grouper, 'mode', 'trexpfac']].groupby(['mode', grouper]).sum()[['trexpfac']]
        else:
            mode_trips_by_grouper = df[[grouper, 'mode', 'trexpfac']].groupby(['mode', grouper]).count()[['trexpfac']]
        mode_trips_by_grouper = mode_trips_by_grouper.reset_index()
        mode_trips_by_grouper = mode_trips_by_grouper.pivot(index = 'mode', columns = grouper, values = 'trexpfac') #Creates a pivot table
        #Get total trips
        if weighted:
            total_trips_by_grouper = df[[grouper, 'trexpfac']].groupby(grouper).sum()['trexpfac']
        else:
            total_trips_by_grouper = df[[grouper, 'trexpfac']].groupby(grouper).count()['trexpfac']
        mode_share_by_grouper = pd.DataFrame(index = modes, columns = mode_trips_by_grouper.columns)
        #Divide trips by category by total number of trips to get share
        for group in mode_share_by_grouper.columns:
            for mode in modes:
                try:
                    mode_share_by_grouper.loc[mode, group] = mode_trips_by_grouper.loc[mode, group] / total_trips_by_grouper[group] * 100
                except LookupError:
                    continue
            mode_share_by_grouper[group] = mode_share_by_grouper[group].fillna(0)
            mode_share_by_grouper[group] = mode_share_by_grouper[group].apply(round_add_percent)
        return mode_share_by_grouper

def weighted_average(df_in,col,weights,grouper = None): #Computes a weighted average, which can be grouped by a variable
    if grouper==None:
        df_in[col+'_sp']=df_in[col].multiply(df_in[weights]) #Multiply each value by associated weight
        n_out=pd.Series.sum(df_in[col+'_sp'])/pd.Series.sum(df_in[weights]) #Divide by sum of weights
        return(n_out)
    else:
        df_in[col+'_sp']=df_in[col].multiply(df_in[weights]) #Multiply each value by associated weight
        df_out=df_in.groupby(grouper).sum() #Group by grouper
        df_out[col+'_wa']=df_out[col+'_sp'].divide(df_out[weights]) #Divide grouped sum-product by grouped sum of weights
        return(df_out[col+'_wa'])

#Functions based on formulas at http://www.nematrian.com/R.aspx?p=WeightedMomentsAndCumulants
def weighted_variance(df_in, col, weights):
    wa = weighted_average(df_in, col, weights)
    df_in['sp'] = df_in[weights] * (df_in[col] - wa) ** 2
    n_out = df_in['sp'].sum() / df_in[weights].sum()
    return n_out

def weighted_skew(df_in, col, weights):
    wa = weighted_average(df_in, col, weights)
    wv = weighted_variance(df_in, col, weights)
    df_in['sp'] = df_in[weights] * ((df_in[col] - wa) / (math.sqrt(wv))) ** 3
    n_out = df_in['sp'].sum() / df_in[weights].sum()
    return n_out

def weighted_kurtosis(df_in, col, weights, excess = True): #Gives the excess kurtosis
    wa = weighted_average(df_in, col, weights)
    wv = weighted_variance(df_in, col, weights)
    df_in['sp'] = df_in[weights] * ((df_in[col] - wa) / (math.sqrt(wv))) ** 4
    if excess:
        n_out = df_in['sp'].sum() / df_in[weights].sum() - 3
    else:
        n_out = df_in['sp'].sum() / df_in[weights].sum()
    return n_out

def recode_index(df,old_name,new_name): #Recodes index
   df[new_name]=df.index
   df=df.reset_index()
   del df[old_name]
   df=df.set_index(new_name)
   return df

def min_to_hour(input, base): #Converts minutes since a certain time of the day to hour of the day
    timemap = {}
    for i in range(0, 24):
        if i + base < 24:
            for j in range(0, 60):
                if i + base < 9:
                    timemap.update({i * 60 + j: '0' + str(i + base) + ' - 0' + str(i + base + 1)})
                elif i + base == 9:
                    timemap.update({i * 60 + j: '0' + str(i + base) + ' - ' + str(i + base + 1)})
                else:
                    timemap.update({i * 60 + j: str(i + base) + ' - ' + str(i + base + 1)})
        else:
            for j in range(0, 60):
                if i + base - 24 < 9:
                    timemap.update({i * 60 + j: '0' + str(i + base - 24) + ' - 0' + str(i + base - 23)})
                elif i + base - 24 == 9:
                    timemap.update({i * 60 + j: '0' + str(i + base - 24) + ' - ' + str(i + base - 23)})
                else:
                    timemap.update({i * 60 + j:str(i + base - 24) + ' - ' + str(i + base - 23)})
    output = input.map(timemap)
    return output

def all_same(items): #Checks if all of the items in a list or list-like object are the same
    return all(x == items[0] for x in items)

def to_percent(y, position): #Converts a number to a percent
    global found
    if found:
        # Ignore the passed in position. This has the effect of scaling the default
        # tick locations.
        s = str(100 * y)

        # The percent symbol needs escaping in latex
        if matplotlib.rcParams['text.usetex'] == True:
            return s + r'$\%$'
        else:
            return s + '%'
    else:
        print('No matplotlib')
        return 100 * y

                
#Start Importing
timerstart = time.time()

#Import categorical variable recoding map
mapimportstart = time.time()
guide = h5toDF.get_guide(guide_file)
cat_var_dict = h5toDF.guide_to_dict(guide)
print('Categorical variable recoding map successfully imported in '+str(round(time.time()-mapimportstart,1))+u' seconds \u270d')

#Import Household File
filetimerstart = time.time()
Household = pd.io.excel.read_excel(household_file)
for column in Household.columns:
    if column in cat_var_dict:
        Household[column] = Household[column].map(cat_var_dict[column])
print('House File successfully imported and recoded in '+str(round(time.time()-filetimerstart,1))+u' seconds \u2302')

#Import Vehicle File
filetimerstart = time.time()
Vehicle = pd.io.excel.read_excel(vehicle_file)
for column in Vehicle.columns:
    if column in cat_var_dict:
        Vehicle[column] = Vehicle[column].map(cat_var_dict[column])
print('Vehicle File successfully imported and recoded in '+str(round(time.time()-filetimerstart,1))+u' seconds \u2708')

#Import Person File
filetimerstart = time.time()
Person = pd.io.excel.read_excel(person_file)
for column in Person.columns:
    if column in cat_var_dict:
        Person[column] = Person[column].map(cat_var_dict[column])
print('Person File successfully imported and recoded in '+str(round(time.time()-filetimerstart,1))+u' seconds \u2603')

#Import Trip File (Main Sheet)
filetimerstart = time.time()
Trip = pd.io.excel.read_excel(trip_file, sheetname = 'Data')
for column in Trip.columns:
    if column in cat_var_dict:
        pass
        Trip[column] = Trip[column].map(cat_var_dict[column])
print('Trip File successfully imported and recoded in '+str(round(time.time()-filetimerstart,1))+u' seconds \u2638')

#Done Importing
print('2014 Household Travel Survey Import Successful in ' + str(round(time.time() - timerstart, 1)) + u' seconds \u263a')

#Some basic summaries
num_households = Household['expwt_final'].sum()
num_households_unweighted = Household['hhid'].count()

HHPer = pd.merge(Household, Person, on = 'hhid')
num_people = HHPer['expwt_final'].sum()
num_people_unweighted = Person['personid'].count()

HHPerTrip = pd.merge(HHPer, Trip, left_on = ['hhid', 'personid'], right_on = ['hhid', 'personID'])
num_trips = HHPerTrip['expwt_final'].sum()
num_trips_unweighted = HHPerTrip['expwt_final'].count()

#####################BEGIN FILTER##################################################################

filter_start = time.time()
print('Begin data processing')

#Create blank columns to indicate if a trip is implied to be walking to or from transit
HHPerTrip['walk_to_transit'] = np.nan
HHPerTrip['walk_from_transit'] = np.nan

HHPerTrip = HHPerTrip.set_index('tripID')

transit_modes = ['Bus (public transit)',
                 'Train (rail and monorail)',
                 'Ferry or water taxi',
                 'Streetcar',
                 'Paratransit',
                 'Private bus or shuttle']

implied_transfer_time = 20 #Set number of minutes to assume person waiting for transfer

print ('Begin identification of access, egress, and transfer walk trips')
for trip in HHPerTrip.index.tolist():  
    if HHPerTrip.loc[trip, 'mode'] == 'Walk, jog, or wheelchair': #Check if walk trip
        if trip + 1 in HHPerTrip.index.tolist(): #Check if next trip exists
            if HHPerTrip.loc[trip + 1, 'mode'] in transit_modes: #Check if next trip is transit
                if HHPerTrip.loc[trip + 1, 'time_start_mam'] - HHPerTrip.loc[trip, 'time_end_mam'] < implied_transfer_time: #Check if next trip began within implied transfer time
                    HHPerTrip.loc[trip, 'walk_to_transit'] = 1
                    HHPerTrip.loc[trip + 1, 'walk_to_transit'] = 0
                else:
                    HHPerTrip.loc[trip, 'walk_to_transit'] = 0
            else:
                HHPerTrip.loc[trip, 'walk_to_transit'] = 0
        else:
            HHPerTrip.loc[trip, 'walk_to_transit'] = 0
        if trip - 1 in HHPerTrip.index.tolist(): #Check if previous trip exists
            if HHPerTrip.loc[trip - 1, 'mode'] in transit_modes: #Check if previous trip was transit
                if HHPerTrip.loc[trip, 'time_start_mam'] == HHPerTrip.loc[trip - 1, 'time_end_mam']: #Check if current trip began at the same time that the previous trip ended
                    HHPerTrip.loc[trip, 'walk_from_transit'] = 1 
                    HHPerTrip.loc[trip - 1, 'walk_from_transit'] = 0
                else:
                    HHPerTrip.loc[trip, 'walk_from_transit'] = 0
            else:
                HHPerTrip.loc[trip, 'walk_from_transit'] = 0
        else:
            HHPerTrip.loc[trip, 'walk_from_transit'] = 0

print('Access, egress, and transfer walk trips identified')


#Loop to identify if multi-route transit trips should be same trip
HHPerTrip['Transfered'] = np.nan
HHPerTrip['Transfered'] = HHPerTrip['Transfered'].fillna(0) #Creates column of zeros

print('Begin identification of unlinked transit trips')
tripids = HHPerTrip.query('mode in @transit_modes').index.tolist()
tripids.reverse()
for trip in tripids: #Loops over all transit trips
    if trip + 1 in tripids: #Checks if next trip is transit
        if HHPerTrip.loc[trip + 1, 'time_start_mam'] - HHPerTrip.loc[trip, 'time_end_mam'] <= implied_transfer_time: #Checks if next trip began within the implied transfer time
            HHPerTrip.loc[trip + 1, 'Transfered'] = 1
            HHPerTrip.loc[trip, 'gdist'] = HHPerTrip.loc[trip, 'gdist'] + HHPerTrip.loc[trip + 1, 'gdist'] #Add distances together
            HHPerTrip.loc[trip, 'trip_dur_reported'] = HHPerTrip.loc[trip, 'trip_dur_reported'] + HHPerTrip.loc[trip + 1, 'trip_dur_reported'] #Add times together
print('Unlinked transit trips identified')

HHPerTrip = HHPerTrip.query('Transfered != 1 and walk_to_transit != 1 and walk_from_transit != 1')
print('Access, egress, and transfer walk trips and unlinked transit trips removed')

print('Data processed in ' + str(round(time.time() - filter_start, 1)) + ' seconds')

#########################END FILTER##########################################################

#Various basic data
trip_ok = HHPerTrip.query('gdist > 0 and gdist < 200')
average_trip_length = weighted_average(trip_ok, 'gdist', 'expwt_final', None)
average_trip_length_unweighted = trip_ok['gdist'].mean()

mode_share = HHPerTrip.groupby('mode').sum()['expwt_final']/num_trips*100
mode_share_unweighted = HHPerTrip.groupby('mode').count()['expwt_final']/num_trips_unweighted*100
mode_share_df = pd.DataFrame.from_items([('Weighted', mode_share.round(2)), ('Unweighted', mode_share_unweighted.round(2))])

purpose_share = HHPerTrip.groupby('d_purpose').sum()['expwt_final']/num_trips*100
purpose_share_unweighted = HHPerTrip.groupby('d_purpose').count()['expwt_final']/num_trips_unweighted*100
purpose_share_df = pd.DataFrame.from_items([('Weighted', purpose_share.round(2)), ('Unweighted', purpose_share_unweighted.round(2))])
purpose_share_df = recode_index(purpose_share_df, 'd_purpose', 'Destination Purpose')

non_home_trips = HHPerTrip.query('d_purpose != "Go home"')
num_non_home_trips = non_home_trips['expwt_final'].sum()
num_non_home_trips_unweighted = non_home_trips['expwt_final'].count()

trips_to_work = HHPerTrip.query('d_purpose == "Go to workplace" or d_purpose == "Go to other work-related place"')
num_work_trips = trips_to_work['expwt_final'].sum()
num_work_trips_unweighted = trips_to_work['expwt_final'].count()
work_trip_mode_share = trips_to_work.groupby('mode').sum()['expwt_final']/num_work_trips*100
work_trip_mode_share_unweighted = trips_to_work.groupby('mode').count()['expwt_final']/num_work_trips_unweighted*100
work_trip_mode_share_df = pd.DataFrame.from_items([('Weighted', work_trip_mode_share.round(2)), ('Unweighted', work_trip_mode_share_unweighted.round(2))])

trips_to_work = HHPerTrip.query('d_purpose == "Go to workplace" or d_purpose == "Go to other work-related place"')
num_work_trips = trips_to_work['expwt_final'].sum()
num_work_trips_unweighted = trips_to_work['expwt_final'].count()
work_trip_mode_share = trips_to_work.groupby('mode').sum()['expwt_final']/num_work_trips*100
work_trip_mode_share_unweighted = trips_to_work.groupby('mode').count()['expwt_final']/num_work_trips_unweighted*100
work_trip_mode_share_df = pd.DataFrame.from_items([('Weighted', work_trip_mode_share.round(2)), ('Unweighted', work_trip_mode_share_unweighted.round(2))])

def school_issue(Trip, Person):
    #Checking for school issue
    Trip['travelers_next'] = np.nan
    Trip['time_at_dest'] = np.nan
    Trip = Trip.set_index('tripID')
    Trip = Trip.sort_index()
    for trip in Trip.index:
        if trip + 1 in Trip.index:
            Trip['travelers_next'][trip] = Trip['travelers_total'][trip + 1]
            Trip['time_at_dest'][trip] = Trip['time_start_mam'][trip + 1] - Trip['time_end_mam'][trip]
    Trip = Trip.reset_index()
    Trip['personid'] = Trip['personID'] #Recode column name to make consistent
    shared_trips = pd.merge(Trip, Person, on =['hhid', 'personid']).query('mode == "Drove/rode ONLY with other household members" or mode == "Drove/rode with people not in household (may also include household members)"')
    households = shared_trips['hhid'].value_counts().index
    stwsi = [] #List to keep track of the shared trips with the issue
    uee = 0 #This is for entries with unicode encoding errors, as they can be manually looked at
    for household in households: #Loop over the households
        hh_shared_trip = shared_trips.query('hhid == @household')
        destinations = hh_shared_trip['place_end'].value_counts().index
        for destination in destinations: #Loop over the destinations
            try:
                hh_destination = hh_shared_trip.query('place_end == "' + str(destination) + '"')
            except UnicodeEncodeError:
                uee = uee + 1
                print('Unicode encode error for Household Number ' + str(household))
                continue
            trips = hh_destination['time_end_mam'].value_counts().index   
            for trip in trips:
                specific_shared_trip = hh_destination.query('time_end_mam == @trip') #If people went to the same destination at the same time, that was assumed to be a specific trip
                school_issue = all(purpose == 'Go to school/daycare (e.g. daycare, K-12, college)' for purpose in specific_shared_trip['d_purpose']) #Check if everybody's purpose was to go to school or daycare
                if school_issue:
                    stwsi.append((household, destination, trip)) #Add any trip that has the issue

    if uee == 1:
        print('There was 1 Unicode Encode Error')
    else:
        print('There were ' + uee + ' Unicode Encode Errors')

    si = pd.Series(index = shared_trips.index) #Create a blank series that's 0 if there's no issue, and 1 if there is
    si = si.fillna(0)
    shared_trips = shared_trips.reset_index()
    for i in range(len(shared_trips['hhid'])):
        if (shared_trips['hhid'][i], shared_trips['place_end'][i], shared_trips['time_end_mam'][i]) in stwsi:
            si[i] = 1
    shared_trips['school_issue'] = si
    hh_with_school_issue = shared_trips.query('school_issue == 1 and mode != "School bus" and student == "No, not a student"')
    dropoff_or_pickup = hh_with_school_issue.query('travelers_total > travelers_next and time_at_dest < 10 or travelers_total < travelers_next and time_at_dest < 10')

    #Write the file
    writer = pd.ExcelWriter(location + '/SchoolIssue.xlsx', engine = 'xlsxwriter')
    hh_with_school_issue.to_excel(excel_writer = writer, sheet_name = 'Non-Students going to school', na_rep = 'NA')
    dropoff_or_pickup.to_excel(excel_writer = writer, sheet_name = 'Pickup and Dropoff', na_rep = 'NA')
    workbook = writer.book
    sheet = 'Non-Students going to school'
    worksheet = writer.sheets[sheet]
    worksheet.autofilter(0, 1, worksheet.dim_rowmax, worksheet.dim_colmax)
    sheet = 'Pickup and Dropoff'
    worksheet = writer.sheets[sheet]
    worksheet.autofilter(0, 1, worksheet.dim_rowmax, worksheet.dim_colmax)
    writer.save()

def timeshareplot():
    global found
    if found:
        HHPerTrip['time_start_ma3'] = HHPerTrip['time_start_mam'] - 180
        HHPerTrip['dep_hr'] = min_to_hour(HHPerTrip['time_start_ma3'], 3)
        trip_time_dep = HHPerTrip[['dep_hr', 'expwt_final']].groupby('dep_hr').sum()['expwt_final']
        trip_time_dep_share = 100 * trip_time_dep / trip_time_dep.sum()

        HHPerTrip['time_end_ma3'] = HHPerTrip['time_end_mam'] - 180
        HHPerTrip['arr_hr'] = min_to_hour(HHPerTrip['time_end_ma3'], 3)
        trip_time_arr = HHPerTrip[['arr_hr', 'expwt_final']].groupby('arr_hr').sum()['expwt_final']
        trip_time_arr_share = 100 * trip_time_arr / trip_time_arr.sum()

        trip_time = pd.DataFrame()
        trip_time['Departure Time'] = trip_time_dep_share
        trip_time['Arrival Time'] = trip_time_arr_share

        trip_time_hist = trip_time.plot(legend = True, grid = True, kind = 'bar', color = ['#004040', '#00c0c0'], sharex = True, rot = 60, figsize = (15, 10))
        matplotlib.pyplot.title('2014 Household Travel Survey Time Share', size = 48, family = 'Times New Roman')
        matplotlib.pyplot.xlabel('Hour of Day', size = 18, family = 'Times New Roman')
        matplotlib.pyplot.ylabel('% of Trips', size = 18, family = 'Times New Roman')
        matplotlib.pyplot.show()
        trip_time_fig = trip_time_hist.get_figure()
        trip_time_fig.savefig(location + '/Time_Share.png')
    else:
        raise ImportError("So matplotlib isn't really installed on your computer. Unless you have the library fairy's phone number, you should just go ahead and install it before trying to run this function.")

def get_outliers(dist, time, speed):
    High_Dist = Trip.query('gdist > @Dist')
    Long_Time = Trip.query('trip_dur_reported > @Time')
    High_Speed = HHPerTrip.query('implied_speed_mph > @Speed')
    writer = pd.ExcelWriter(location + '/Outliers.xlsx', engine = 'xlsxwriter')
    High_Dist.to_excel(excel_writer = writer, sheet_name = 'Travel Distance', na_rep = 'NA')
    Long_Time.to_excel(excel_writer = writer, sheet_name = 'Travel Time', na_rep = 'NA')
    High_Speed.to_excel(excel_writer = writer, sheet_name = 'Speed', na_rep = 'NA')
    for sheet in writer.sheets:
        worksheet = writer.sheets[sheet]
        worksheet.autofilter(0, 1, worksheet.dim_rowmax, worksheet.dim_colmax)
        worksheet.freeze_panes(1, 0)
    writer.save()
    print('Outliers Ready')

def Movers(HHPer, HHPerTrip):
    HHPer['loc_change'] = np.nan
    HHPer = HHPer.set_index('personid')
    for person in HHPerTrip['personid'].value_counts().index:
        persontrips = HHPerTrip[['personid', 'tripID', 'olat', 'dlat', 'olng', 'dlng']].query('personid == @person')
        persontrips = persontrips.reset_index()
        ntrips = persontrips['tripID'].count()
        if abs(persontrips['olat'][0] - persontrips['dlat'][ntrips - 1] < 0.0009) and (persontrips['olng'][0] - persontrips['dlng'][ntrips - 1] < 0.0006): #About a 50 meter radius
            HHPer['loc_change'][person] = 0
        else:
            HHPer['loc_change'][person] = 1
    loc_change_percentage = str(round((HHPer['loc_change'].fillna(0).multiply(HHPer['expwt_final']).sum() / HHPer['expwt_final'].sum()) * 100, 2)) + '%'
    print(loc_change_percentage)

work_distances = pd.DataFrame.from_csv(work_distance_file)
work_distances_in_50 = work_distances.query('miles < 50')

school_distances = pd.DataFrame.from_csv(school_distance_file)
school_distances_in_50 = work_distances.query('miles < 50')

print('Data imported and ready to analyze!')