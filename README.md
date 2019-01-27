# procyclingstats.com-webscraper

This repository contains datasets scraped from the procycling stats.com website, as well as the python code used to retrieve them. The data contains base informations about riders and urls used to retrieve those informations. 
 
## Examples of the data you can find
 
##Rider data

| ID | Fullname | Teamname | Birthdate | Country | Height | Weight | pcs_url |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | Adam Yates | Mitchelton-Scott | 19920807 | Great Britain | 1.73 | 58.0 | https://www.procyclingstats.com/rider/adam-yates |
| 6 | Adrián González | Burgos-BH | 19920913 | Spain | 1.71 | 63.0 | https://www.procyclingstats.com/rider/adrian-gonzalez |

##Stage data

| ID | Stage_Name | Date | Stage_Type | Start | Finish | Race_ID | Stage# | url | Length | 
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 94 | Tour de France 2015  Stage 9 (TTT) | 2015-07-12 | TTT | Vannes | Plumelec | 17 | 9 | race/tour-de-france/2015/stage-9 | 28.0
| 130 | Vuelta a España 2015  Stage 9 | 2015-08-30 | RR | Torrevieja | Cumbre del Sol. Benitachell | 21 | 9 | race/vuelta-a-espana/2015/stage-9 | 168.3
  
Feel free to download the data and use it as you see fit. This repository is  as a demo project. If you want up to date data, you'll have to run the code yourself and probably tinker with the code, as the procyclingstats url structures tend to change quite a bit with time.

## todo-list
- [x] Repair stage data

- [x] Add race/stage data generating code

- [ ] Fetch result data
