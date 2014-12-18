import pandas as pd
import numpy as np
import config

#household = process_survey.load_data(household_file)
def load_data(file):
    return pd.io.excel.read_excel(io=file[0], sheetname=file[1])

def join_hh2per(person_df, household_df):
    ''' Join household fields to each person record. Input is pandas dataframe '''
    return pd.merge(person_df, household_df, 
                    left_on=config.p_hhid, right_on=config.h_hhid, 
                    suffixes=('_per', '_hh'))

def join_hhper2trip(trip_df, hh_per_df):
    ''' Join person and household fields to trip records '''
    return pd.merge(trip_df, hh_per_df, 
                    left_on=config.t_personid, right_on=config.p_personid, 
                    suffixes=('_trip', '_p_hh'))

class Person:
    def __init__(self, df):
        self.age = df[config.p_age].mean()
        self.gender = df[config.p_gender].mean()
        self.employment = df[config.p_employment].mean()
        self.numjobs = df[config.p_jobs_count].mean()
        self.worker = df[config.p_worker].mean()
        self.num_trips = df[config.p_numtrips].mean()                # Number of trips made on travel day (derived)
        self.hours_work = df[config.p_hours_work].mean()             # Work: Hours per week
   

class Household:
    def __init__(self, df):
        self.hhsize = df[config.h_hhsize].mean()                     # Household size
        self.numadults = df[config.h_numadults].mean()               # Number of adults
        self.numchildren = df[config.h_numchildren].mean()           # Number of children
        self.numworkers = df[config.h_numworkers].mean()             # Number of workers
        self.hhnumtrips = df[config.h_numtrips].mean()               # Household number of trips on travel day (derived)
        self.vehicle_count = df[config.h_veh_count].mean()                  # Number of vehicles
        self.income = df.groupby(config.h_income_det_imp)[h_exp_wt].count() # Income classes

class Trip:
    def __init__(self, df):
        self.tripdur = df['trip_dur_reported']


def clip(file):
    ''' Send to clipboard for pasting into Excel '''
    file.to_clipboard()

def main():
    pass

if __name__ == '__main__':
    main()