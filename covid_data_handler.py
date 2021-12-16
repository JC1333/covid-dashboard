"""This modules main purpose is to get up-to-date covid data for the national and local area
specifically data related recent cases,cumulative deaths and hospital admissions"""
import sched
import time
import json
from uk_covid19 import Cov19API
from functionallity import get_config_data

s = sched.scheduler(time.time,time.sleep)


def parse_csv_data(csv_filename):
    """parses a csv file into a list"""
    with (open(csv_filename,'r',)).read() as file:
        prev_index = -1
        next_index = 0
        row_count = 0
        rows = []
        while next_index>=0:
            next_index = file.find('\n',prev_index+1)
            rows.append(file[prev_index+1:next_index])
            prev_index = next_index
            row_count = row_count + 1
        if rows[-1]=='' :
            rows.pop()
        return rows



def process_covid_csv_data(covid_csv_data):
    """takes a pre made list and calculates value from it"""
    #data seperated by commas
    last7days_cases = 0
    current_hospital_cases = 0
    total_deaths = 0
    row_count = 3 #at three as current day is not filled and yesterday is not complete
    while row_count!=10 : #last7days_cases loop
        current_row = covid_csv_data[row_count]
        last_comma = current_row.rfind(',')
        row_cases = current_row[last_comma+1:len(current_row)]
        last7days_cases = last7days_cases + int(row_cases)
        row_count = row_count + 1


    current_row = covid_csv_data[1] #current_hospital_cases
    last_comma = current_row.rfind(',')
    fifth_comma = current_row.rfind(',',0,last_comma-1)
    current_hospital_cases = int(current_row[fifth_comma+1:last_comma])


    current_row = covid_csv_data[14] #total_deaths
    last_comma = current_row.rfind(',')
    fifth_comma = current_row.rfind(',',0,last_comma-1)
    fourth_comma = current_row.rfind(',',0,fifth_comma-1)
    total_deaths = int(current_row[fourth_comma+1:fifth_comma])


    return last7days_cases , current_hospital_cases , total_deaths

def covid_API_request(location='exeter',location_type='ltla'):
    """collects covid data from an api before processing and storing the data
       json file"""
    user_set = get_config_data()
    location = user_set['local_area']
    location_type = user_set['local_type']
    nation=user_set['nation']

    national = [
    'areaType=nation',
    'areaName='+nation,
    ]

    national_structure = {
    "newCasesBySpecimenDate": "newCasesBySpecimenDate",
    "cumDailyNsoDeathsByDeathDate":"cumDailyNsoDeathsByDeathDate",
    "hospitalCases":"hospitalCases",
    }

    local = [
    'areaType='+location_type,
    'areaName='+location,
    ]

    local_structure = {
    "newCasesBySpecimenDate": "newCasesBySpecimenDate"
    }

    #getting and filtering data from API
    natapi = Cov19API(filters=national, structure=national_structure)
    locapi = Cov19API(filters=local, structure=local_structure)

    natData = natapi.get_json()['data']
    locData = locapi.get_json()['data']

    national_infection_sum=0
    local_infection_sum=0
    count=1

    while count!=7:
        singleDayNat = natData[count]
        singleDayLoc = locData[count]
        national_infection_sum = national_infection_sum + singleDayNat.get('newCasesBySpecimenDate')
        local_infection_sum = local_infection_sum + singleDayLoc.get('newCasesBySpecimenDate')
        count=count+1

    national_hosptital_cases = natData[0].get('hospitalCases')
    national_cumumlative_deaths = natData[0].get('cumDailyNsoDeathsByDeathDate')

    count = 0
    while type(national_cumumlative_deaths)!=int:
        national_cumumlative_deaths = natData[count].get('cumDailyNsoDeathsByDeathDate')
        count=count+1

    data = {
            'local_infection_sum':local_infection_sum,
            'location':location,
            'nation':nation,
            'national_infection_sum':national_infection_sum,
            'national_hosptital_cases':national_hosptital_cases,
            'national_cumumlative_deaths':national_cumumlative_deaths
        }

    data_file = open('covid_data.json', 'w')
    json.dump(data,data_file)
    data_file.close()


def schedule_covid_updates(update_interval,update_name):
    """schedules for the covid data to be updated using the sched module"""
    sched_name = s.enterabs(update_interval, 1, covid_API_request,())
    return sched_name
