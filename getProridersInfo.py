# coding: utf8

import requests
from bs4 import BeautifulSoup
import json
import time
import random
import os
import re
import sys

#####
#####
# ### Variables

user_agent = {'User-agent': 'Mozilla/5.0'}

# ### Useful functions

# Base function to return HTML from an URL using BeautifulSoup
def download_soup(url):
    print('Starting request for: ' + url)
    if response.status_code == 200:
        response = requests.get(url, headers=user_agent)
        page = response.text
        soup = BeautifulSoup(page, 'lxml')
        print('Successful request!')
        return soup
    else:
        print('Unsuccessful request, status code: '+ response.status_code)

#####
#####
# ### Get team pages URLs from the pcs team page of 2018
# Goes throught the list of teams and stores the URLs in a json

def get_team_urls():
    print("Starting get_team_urls")
    
    startlist = download_soup('https://www.procyclingstats.com/teams/').find_all('a', href = re.compile('team/'))
    urls = [x['href'] for x in startlist]
    list_team_urls = ['https://www.procyclingstats.com/' + u for u in urls]
    list_team_urls =sorted(list(set(list_team_urls)))
    file = 'proteams2018.json'
    with open(file, 'w') as f:
        json.dump(list_team_urls, f)
        
    print("Finished get_team_urls")



#####
#####
# ### Get riders pages URLs from team pages
# Uses the file created with get_team_urls,
# download each team page and scrape through the page to find riders URLs,
# creates its own file of URLs

def get_riders_urls():
    print("Starting get_riders_urls")
    
    with open('proteams2018.json') as f:
        team_urls = json.load(f)
        list_riders_urls= []

        for url in team_urls:
            riders = download_soup(url).find_all('a', class_ = 'rider')
            urls = [x['href'] for x in riders]
            for u in urls:
                list_riders_urls.append('https://www.procyclingstats.com/' + u)
        list_riders_urls = sorted(list(set(list_riders_urls)))
        file = 'proriders2018.json'
        with open(file, 'w') as fr:
            json.dump(list_riders_urls, fr)
            
    print('Finished get_riders_url')



#####
#####
# ###Get rider info
# Parse throught a rider's html page to get:
# name, team, day of birth, country, height, weight
# and return it as a list

def get_uniquerider_info(rider_url):
    print('Starting get_uniquerider_inf('+rider_url+')')

    rider_soup = download_soup(rider_url)
    
    try:
        fullname = rider_soup.find('title').text.encode('latin-1', 'ignore').decode('utf-8', 'ignore')
    except(UnicodeEncodeError):
        fullname = rider_soup.find('title').text
    try:
        team = rider_soup.find('span', class_='red').text.encode('latin-1', 'ignore').decode('utf-8', 'ignore')
    except(UnicodeEncodeError):
        team = rider_soup.find('span', class_='red').text
    except:
        team = 'noteam'
    inter_soup = rider_soup.find('div', style="width: 230px; float: left; font: 12px/15px tahoma; ")
    list_birthdate = inter_soup.find('span').contents[1:4]
    try:
        birthdate_tmp = dt.datetime.strptime(list_birthdate[0] + list_birthdate[2][:-5], " %d %B %Y").date()
    except:
        birthdate_tmp = dt.datetime.strptime(list_birthdate[0] + list_birthdate[2], " %d %B %Y").date()
    birthdate = int(birthdate_tmp.year*10000 + birthdate_tmp.month*100 + birthdate_tmp.day)
    try:
        country = inter_soup.find('a', class_='black').text.encode('latin-1', 'ignore').decode('utf-8', 'ignore')
    except(UnicodeEncodeError):
        country = inter_soup.find('a', class_='black').text
    try:
        height = float(inter_soup.find(text='Height:').next.split()[0])
    except:
        height = 0
    try:
        weight = float(inter_soup.find(text='Weight:').next.split()[0])
    except:
        weight = 0
    
    rider_info_list = [fullname, team, birthdate, country, height, weight, rider_url]
    #print(rider_info_list)
    
    print('Finished get_uniquerider_inf('+rider_url+')')
    return rider_info_list

#####
#####
# ###Get all riders info
# Execute get_riderinfo on all the urls in the file created by get_rider_urls

def get_allriders_info():
    print('Starting get_allriders_info')
    
    namefile ='ridersinfo2018v2.json'
    with open('proriders2018.json','r') as origin_file, open(namefile,'r+', encoding='utf-8') as goal_file:
        list_riders_urls = json.load(origin_file)
        if(os.stat(namefile).st_size!=0):
            saved_riders_info = json.load(goal_file)
            last_saved_rider = saved_riders_info[-1]
            goal_file.close()
            open(namefile, 'w').close()
            goal_file = open(namefile, 'w', encoding='utf-8')
        else:
            saved_riders_info = []
            last_saved_rider = ['aaa']

        try:
            for rider_url in list_riders_urls:
                print(rider_url + ' compared to ' + last_saved_rider[-1])
                if (rider_url > last_saved_rider[-1]):
                    saved_riders_info.append(get_uniquerider_info(rider_url))
                    timer = 0.5 + 0.5 * random.random()
                    print('Success, sleeping for',round(timer,2),'sec') #Reduce server load to avoid being banned
                    time.sleep(timer)
            json.dump(saved_riders_info, goal_file)
                
        except (KeyboardInterrupt, SystemExit):
            if len(saved_riders_info)!=0:
               json.dump(saved_riders_info, goal_file)
            print('INTERRUPT')

        except:
            if len(saved_riders_info)!=0:
               json.dump(saved_riders_info, goal_file)
            print('BUG : ' + rider_url)
   
    print('Finished get_allriders_info')

    

#####
#####
# ### Main

get_team_urls()
get_riders_urls()
get_allriders_info()

#####
#####
# ### Show riderinfo file
# Used to check the content of the file, because encoding showed inconsistencies

def show_riderinfo():
    namefile = 'ridersinfo2018v2.json'
    with open(namefile,'r') as file:
        list_riders_info = json.load(file, encoding='utf-8')
        for r in list_riders_info:
            print(r[0])

show_riderinfo()