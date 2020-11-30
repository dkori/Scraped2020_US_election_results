# import required packages
from bs4 import BeautifulSoup
import requests
import pandas as pd
import regex as re

# assign url for politico house election summary page
url = "https://www.politico.com/2020-election/results/house/"
# retrieve main politico house election summary page
req = requests.get(url)
soup = BeautifulSoup(req.content, 'html.parser')

# retrieve all state links in a list
state_links = soup.find('ul','jsx-3088201999 state-link-list').find_all("p")
# drop the first element since that's "all states"
state_links = state_links[1:len(state_links)]

# extract the urls from state_links
state_urls = [x.find("a").get('href') for x in state_links]
# add in "politico.com" to each url
state_urls = ["http://politico.com"+x+'house' for x in state_urls]

# define a function to parse rows of each race's table
def parse_row(row,state,district):
    # first td contains candidate name and party, so extract that
    name_party = row.find_all('td')[0].find_all('div')
    name = name_party[0].get_text()
    party = name_party[1].get_text()
    # text of second td contains votes
    votes = row.find('div','candidate-votes-next-to-percent').get_text()
    return([state,district,name,party,votes])

# define a function that takes a state_url as an argument, and returns a dataframe of all election results for that state
def get_state_results(state_url):
    # store name of state
    state = re.sub('/house','',re.sub('.*results/','',state_url))
    # retrieve state
    req = requests.get(state_url)
    if req.status_code!=404:
        soup = BeautifulSoup(req.content, 'html.parser')
        # create a list of all result blocks
        result_blocks = soup.find_all('div','smaller-leaderboard-container')
        # create a blank list to store results for each district in the state
        all_districts = []
        for result_block in result_blocks:
            # store the name of district
            district = result_block.find('div').get('id')
            # isolate table body, parse to list of rows
            result_table = result_block.find('div','results-table').find('table').find('tbody').find_all('tr')
            # iterate through rows of result_table, use parse_row to extract info
            table_row_list = [parse_row(row,state,district=district) for row in result_table]
            # convert table_row_list to pandas
            temp_df = pd.DataFrame(table_row_list,columns = column_names)
            # add pandas frame to all_districts
            all_districts.append(temp_df)
    return(pd.concat(all_districts))

# run function over all state_urls
all_state_results = [get_state_results(state_url) for state_url in state_urls]

# concat in pandas
all_cd_results = pd.concat(all_state_results).reset_index()
# export to csv
all_cd_results[['state','district','candidate','party','votes']].to_csv('results by cd 2020.csv',
                                                                       index=False)
