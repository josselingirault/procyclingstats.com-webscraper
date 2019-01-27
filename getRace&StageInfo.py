
# coding: utf-8

# # This code is used to parse and save info about races from procyclinstats.com

# Gets info from pcs and puts into csv format, by year and category

#####
#####
# ### Imports

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
import random
from dateutil.parser import parse

#####
#####
# ### Variables

user_agent = {'User-agent': 'Mozilla/5.0'}
race_circuits_men = (1, 2, 11, 12, 13, 14, 18) 
circuits_code = {1:"WT", 2:"WC", 11:"Africa Tour", 12:"Asia Tour", 13:"Europe Tour", 14:"Oceania Tour", 18:"America Tour"}

# ### Useful functions

def download_soup(url):
    response = requests.get(url, headers=user_agent)
    page = response.text
    soup = BeautifulSoup(page, 'lxml')
    return soup

def sleep(t):
    #sleep for between t and 2*t
    timer = t + t * random.random()
    print('downloading and parsing done, sleeping for',round(timer,2),'sec')
    time.sleep(timer)

#####
#####
# ### Get race and stage infos from from pcs
# Outputs data in csv files separated by year and category

def create_df_calendar(year_start, year_end, race_circuits):
    #Prepare dataframes and variables
    print("STARTING CALENDAR")
    race_df = pd.DataFrame(columns=["Race_Name","Category","Number_stages"])
    stage_df = pd.DataFrame(columns=["Stage_Name","Date","Stage_Type","Start", "Finish", "Race_ID","Stage#","url","Length"])
    special_races = ('world','nc','championship')

    #main part
    #get data for many yeras
    for year in range(year_start, year_end+1):

        #a year has many race circuits
        #get data for all circuits of a year
        for circuit in race_circuits:
            #Reset dataframes for every circuit
            race_df = pd.DataFrame(columns=["Race_Name","Category","Number_stages"])
            stage_df = pd.DataFrame(columns=["Stage_Name","Date","Stage_Type","Start", "Finish", "Race_ID","Stage#","url","Length"])
   
            circuit_url = "https://www.procyclingstats.com/races.php?year=" + str(year) + "&circuit=" + str(circuit) + "&ApplyFilter=Filter"
            circuit_soup = download_soup(circuit_url)
            inter_soup = circuit_soup.find('div', {'class' : 'content'})
            inter_soup = inter_soup.find('table')

            #Get href for links where no special character such as @
            races_in_circuit = [x['href'] for x in inter_soup.find_all('a', href = re.compile('race/')) if not bool(re.compile(r'[^\w/.:-]').search(x['href']))]
                                                                                                                    
            #a circuit has many races
            #get data about each race
            for race_temp_url in races_in_circuit:
                sleep(1)
                race_url = 'https://www.procyclingstats.com/' + race_temp_url#['href'].encode('latin-1', 'ignore').decode('utf-8', 'ignore')
                if race_url[-8:] == "overview":
                    race_url = race_url[:-8]
                    
                #print race_url 
                print(race_url)
                
                #get source code for that race_url
                race_soup = download_soup(race_url)
                
                #get the race's name. Shouldn't need a try/except, all urls have a title
                race_name = race_soup.find('title').text.encode('latin-1', 'ignore').decode('utf-8', 'ignore').replace('|',' ').replace('  ',' ').replace(' Results','')
                
                #get the race's category. Junior/u23 races often have undefined category.
                try:
                    race_cat = race_soup.find('a', href = re.compile('info.php')).text
                except:
                    race_cat = "-"
                    
                #Set some variables by default
                stages_url = None
                is_prologue = False
                is_stage_race = False

                #If the race's a stage race, get stage urls
                try:
                    #Find soup block where stage urls are
                    inter_soup_2 = race_soup.find('div', {'class' : 'ESNav stages'})
                    
                    #If the race's a special race such as championships, nb_stages = 1
                    if inter_soup_2.find('option', value = re.compile('world')) != None or inter_soup_2.find('option', value = re.compile('nc-')) != None or inter_soup_2.find('option', value = re.compile('championship')) != None:
                        nb_stages = 1
                        print("IS SPECIAL")
                    #Else, store all urls in stages_url and count them
                    else:
                        stages = inter_soup_2.find_all('option', value = re.compile('stage'))
                        stages_url = [x['value'] for x in stages]
                        print(stages_url)
                        nb_stages = len(stages)
                        is_stage_race = True

                    #If the race has a prologue
                    if inter_soup_2.find('option', value = re.compile('prologue')) != None:
                        is_prologue = True
                        nb_stages+=1
                        stages_url.insert(0,  race_url[32:] + "/prologue")

                #If the race's a one day race, only one stage
                except(IndexError, AttributeError) as e:
                    print(e)
                    nb_stages = 1

                #save race in dataframe
                temp_df = pd.DataFrame({"Race_Name" : [race_name], "Category" : [race_cat], "Number_stages" : [int(nb_stages)]})
                race_df = pd.concat([race_df, temp_df], ignore_index=True)
                race_index = race_df.index[race_df['Race_Name'] == race_name].tolist()[0]
                #print(race_index)
                #print(race_df)

                #If stage race, get data for stages
                #"Stage_Name","Date","Stage_Type","Start", "Finish", "Race_ID","Stage#","url","Length
                if is_stage_race:
                    print("IS A STAGE RACE")
                    for i in range(len(stages_url)):
                        sleep(1)
                        
                        #Get this stage's soup
                        stage_url = 'https://www.procyclingstats.com/' + stages_url[i]
                        stage_soup = download_soup(stage_url)
                        print(stage_url)
                        
                        #Get stage name from stage soup
                        stage_name = stage_soup.find('title').text.encode('latin-1', 'ignore').decode('utf-8', 'ignore').replace('|',' ').replace(' Results','').replace('  ',' ').rstrip()
                        
                        #Get stage number from loop rank
                        stage_nb = i+1
                        
                        #Get start location, finish location, and the type of race it is
                        try:
                            temp_startfinish = inter_soup_2.find('option', {'value' : stages_url[i]}).text.encode('latin-1', 'ignore').decode('utf-8', 'ignore').split(" - ")
                            print(temp_startfinish)
                            temp_stage_type_str = temp_startfinish[0]
                            temp_startfinish = temp_startfinish[1].split('  ')
                            start_str, finish_str = temp_startfinish[0], temp_startfinish[1]
                        except:
                            start_str, finish_str = "Start", "Finish"
                        if is_prologue:
                            stage_type = "Prologue"
                            is_prologue = False
                        elif re.search('ITT',temp_stage_type_str) != None or re.search('Individual',temp_stage_type_str) != None:
                            print('ITT')
                            stage_type = "ITT"
                        elif re.search('TTT',temp_stage_type_str) != None or re.search('Team', temp_stage_type_str) != None:
                            print('Team TT') 
                            stage_type = "TTT"
                        else:
                            print('Road Race')
                            stage_type = "RR"
                        
                        #Get this stage's date from the stage soup
                        date_soup = stage_soup.find('div', {'class' : 'res-right'})
                        temp_dt = date_soup.find(text=True, recursive=False)
                        stage_date = parse(temp_dt).date()
                    
                        #Get this stage's length from the stage soup
                        try:
                            stage_length = float(stage_soup.find_all('span', {'class':"red"})[1].text.strip('(').strip(')').strip('k'))
                        except(IndexError):
                            stage_length = 0
                            
                        #save in dataframe
                        #"Stage_Name","Stage_Type","Start", "Finish", "Race_ID","Stage#","url","Length"
                        temp_df = pd.DataFrame({"Stage_Name" : [stage_name], "Date" : [stage_date], "Stage_Type" : [stage_type], "Start" : [start_str], "Finish" : [finish_str], "Race_ID" : [int(race_index)], "Stage#" : [int(stage_nb)], "url" : [stages_url[i]], "Length" : [stage_length]})
                        #print(temp_df)
                        stage_df = pd.concat([stage_df, temp_df], ignore_index=True)

                #if one day race, get data about the course
                else:
                    print("IS A ONE DAY RACE")
                    #If ODR, the stage's name is the same as the race's
                    odr_name = race_name.replace('|',' ').replace(' Results','').replace('  ',' ').rstrip()
                    
                    #Get this ODR's date
                    date_soup = race_soup.find('div', {'class' : 'res-right'})
                    temp_dt = date_soup.find(text=True, recursive=False)
                    odr_date = parse(temp_dt).date()
                    
                    #Get start location, finish location, and the type of ODR it is
                    temp_info = race_soup.find_all('span', {'class':"red"})
                    print(temp_info)
                    try:
                        temp_startfinish = temp_info[0].text.encode('latin-1', 'ignore').decode('utf-8', 'ignore').split('  ')
                        odr_start, odr_finish = temp_startfinish[0].strip(), temp_startfinish[1].strip()
                    except:
                        odr_start, odr_finish = "Start", "Finish"
                    try:
                        odr_length = float(temp_info[1].text.strip('(').strip(')').strip('k'))
                    except(IndexError):
                        try:
                            odr_length = float(temp_info[0].text.strip('(').strip(')').strip('k'))
                        except:
                            odr_length = 0
                    odr_nb = 0
                    
                    #get stage type from race_soup
                    stage_type_str = race_soup.find('span', {'class':"blue"}).text
                    if re.search('ITT', stage_type_str) != None or re.search('Individual', stage_type_str) != None:
                        print('ITT')
                        odr_type = "ITT"
                    elif re.search('TTT', stage_type_str) != None or re.search('Team', stage_type_str) != None:
                        print('Team TT') 
                        odr_type = "TTT"
                    else:
                        print('Road Race')
                        odr_type = "RR"
                    #"Stage_Name","Date","Stage_Type","Start", "Finish", "Race_ID","Stage#","url","Length"
                    temp_df = pd.DataFrame({"Stage_Name" : [odr_name], "Date" : [odr_date], "Stage_Type" : [odr_type], "Start" : [odr_start], "Finish" : [odr_finish], "Race_ID" : [int(race_index)], "Stage#" : [int(odr_nb)], "url" : [race_url[32:]], "Length" : [odr_length]})
                    print(temp_df)
                    stage_df = pd.concat([stage_df, temp_df], ignore_index=True)
                    print(stage_df)
            race_df_str = "RaceInfo" + str(year) + "Cat" + str(circuits_code.get(circuit))
            race_df.to_csv(race_df_str + ".csv")
            stage_df_str = "StageInfo" + str(year) + "Cat" + str(circuits_code.get(circuit))
            stage_df.to_csv(stage_df_str + ".csv")
    return 

#####
#####
# ### Main

create_df_calendar(2008, 2018, race_circuits_men)

#####
#####
# ### Group files by year

for year in range(2008, 2019): #from year x to year x-1
    print("Grouping year : " + str(year))
    race_df = pd.DataFrame(columns=["Race_Name","Category","Number_stages"])
    stage_df = pd.DataFrame(columns=["Stage_Name","Date","Stage_Type","Start", "Finish", "Race_ID","Stage#","url","Length"])

    #a year has many race circuits
    #get data for all circuits of a year
    for circuit in race_circuits_men:
        print(str(circuit) + " : " + str(circuits_code.get(circuit)))
        race_df_str = "RaceInfo" + str(year) + "Cat" + str(circuits_code.get(circuit) + ".csv")
        temp_race_df = pd.read_csv(race_df_str, index_col=0)
        stage_df_str = "StageInfo" + str(year) + "Cat" + str(circuits_code.get(circuit) + ".csv")
        temp_stage_df = pd.read_csv(stage_df_str, index_col=0)
        print(temp_stage_df)
        race_df = pd.concat([race_df, temp_race_df], ignore_index=True)
        stage_df = pd.concat([stage_df, temp_stage_df], ignore_index=True)
    
    race_df.to_csv("RaceInfo" + str(year) + ".csv")
    stage_df.to_csv("StageInfo" + str(year) + ".csv")


