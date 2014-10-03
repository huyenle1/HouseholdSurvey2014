import pandas as pd
import numpy as np
import time
import h5toDF
import imp
import scipy.stats as stats

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
        raise ValueError("The function is called 'remove_percent.' I recommend that you give me something that ends with a percent sign. It just might work a little better.")
    try:
        output = float(input[:len(input) - 1])
        return output
    except ValueError:
        raise ValueError("Woah, " + input + "'s not going to work. I need a string where everything other than the last character could be a floating point number.")

#This function gets the mode share grouped by a specified variable. Can be weighted or unweighted
def get_mode_share(df, grouper, weighted = True):
    modes = df['mode'].value_counts().index.tolist() #List of different modes in set
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

def weighted_average(df_in,col,weights,grouper): #Computes a weighted average, which can be grouped by a variable
    if grouper==None:
        df_in[col+'_sp']=df_in[col].multiply(df_in[weights])
        n_out=pd.Series.sum(df_in[col+'_sp'])/pd.Series.sum(df_in[weights])
        return(n_out)
    else:
        df_in[col+'_sp']=df_in[col].multiply(df_in[weights])
        df_out=df_in.groupby(grouper).sum()
        df_out[col+'_wa']=df_out[col+'_sp'].divide(df_out[weights])
        return(df_out[col + 'wa'])

def recode_index(df,old_name,new_name): #Recodes index
   df[new_name]=df.index
   df=df.reset_index()
   del df[old_name]
   df=df.set_index(new_name)
   return df

def all_same(items): #Checks if all of the items in a list are the same
    return all(x == items[0] for x in items)

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

location = 'J:/Projects/Surveys/HHTravel/Survey2014/Data/Review'

#Start Importing
timerstart = time.time()

#Import categorical variable recoding map
mapimportstart = time.time()
guidefile = location + '/Pandas/HHS2014CatVarDict.xlsx'
guide = h5toDF.get_guide(guidefile)
cat_var_dict = h5toDF.guide_to_dict(guide)
print('Categorical variable recoding map successfully imported in '+str(round(time.time()-mapimportstart,1))+u' seconds \u270d')

#Import Household File
filetimerstart = time.time()
Household = pd.io.excel.read_excel(location + '/1_PSRC2014_HH_2014-08-07_v2.xlsx')
for column in Household.columns:
    if column in cat_var_dict:
        Household[column] = Household[column].map(cat_var_dict[column])
print('House File successfully imported and recoded in '+str(round(time.time()-filetimerstart,1))+u' seconds \u2302')

#Import Vehicle File
filetimerstart = time.time()
Vehicle = pd.io.excel.read_excel(location + '/2_PSRC2014_Vehicle_2014-08-07.xlsx')
for column in Vehicle.columns:
    if column in cat_var_dict:
        Vehicle[column] = Vehicle[column].map(cat_var_dict[column])
print('Vehicle File successfully imported and recoded in '+str(round(time.time()-filetimerstart,1))+u' seconds \u2708')

#Import Person File
filetimerstart = time.time()
Person = pd.io.excel.read_excel(location + '/3_PSRC2014_Person_2014-08-07_v2.xlsx')
for column in Person.columns:
    if column in cat_var_dict:
        Person[column] = Person[column].map(cat_var_dict[column])
print('Person File successfully imported and recoded in '+str(round(time.time()-filetimerstart,1))+u' seconds \u2603')

#Import Trip File (Main Sheet)
filetimerstart = time.time()
Trip = pd.io.excel.read_excel(location + '/4_PSRC2014_Trip_2014-08-07_v2x.xlsx')
for column in Trip.columns:
    if column in cat_var_dict:
        pass
        Trip[column] = Trip[column].map(cat_var_dict[column])
print('Trip File successfully imported and recoded in '+str(round(time.time()-filetimerstart,1))+u' seconds \u2638')

#Import Trip Time Check Sheet
time_check = False
if time_check:
    filetimerstart = time.time()
    Trip_timecheck = pd.io.excel.read_excel(location + '/4_PSRC2014_Trip_2014-08-07_v2.xlsx', sheetname = 1)
    for column in Trip_timecheck.columns:
        if column in cat_var_dict:
            pass
            Trip_timecheck[column] = Trip_timecheck[column].map(cat_var_dict[column])
    print('Trip File (Timecheck sheet) successfully imported and recoded in '+str(round(time.time()-filetimerstart,1))+u' seconds \u231a')

#Done Importing
print('2014 Household Travel Survey Import Successful in ' + str(round(time.time() - timerstart, 1)) + u'seconds \u263a')

#Some basic summaries
num_households = Household['expwt_final'].sum()
num_households_unweighted = Household['hhid'].count()

HHPer = pd.merge(Household, Person, on = 'hhid')
num_people = HHPer['expwt_final'].sum()
num_people_unweighted = Person['personid'].count()

HHPerTrip = pd.merge(HHPer, Trip, left_on = ['hhid', 'personid'], right_on = ['hhid', 'personID'])
num_trips = HHPerTrip['expwt_final'].sum()
num_trips_unweighted = HHPerTrip['expwt_final'].count()

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
    writer = pd.ExcelWriter(location + '/pandas/SchoolIssue.xlsx', engine = 'xlsxwriter')
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
        trip_time_fig.savefig(location + '/Pandas/Time_Share.png')
    else:
        raise ImportError("So matplotlib isn't really installed on your computer. Unless you have the library fairy's phone number, you should just go ahead and install it before trying to run this function.")

def get_outliers(dist, time, speed):
    High_Dist = Trip.query('gdist > @Dist')
    Long_Time = Trip.query('trip_dur_reported > @Time')
    High_Speed = HHPerTrip.query('implied_speed_mph > @Speed')
    writer = pd.ExcelWriter(location + '/pandas/Outliers.xlsx', engine = 'xlsxwriter')
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