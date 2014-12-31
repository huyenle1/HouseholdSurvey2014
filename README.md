HouseholdSurvey2014
===================

These scripts import PSRC's 2014 household survey from spreadsheets to Python Pandas dataframes.

Spreadsheet data should be saved in the same directory as the scripts. 

"HHSurveyToPandas.py" is the primary script that loads data into memory. Its functions are imported by the individual query scripts. These query scripts create pivot table summaries for a specific topic, e.g., residence types by income, age, and education. 

Raw survey data is separated into 4 separate files:

Household
Vehicle
Person
Trip

These files are imported into Python and further merged and joined for more complicated data queries. Two important joined files are the Person-Household and the Person-Household-Trip files. The Person-Household file joins household-level data to each person record, using the person ID as a common parameter. This data allows segmentation across certain variables available in only person- or household-level detail. The Person-Household-Trip file joins the Person-Household data with each trip record, allowing further analysis and segmentation.


