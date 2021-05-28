import pandas as pd
import requests, json 

states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
result_frame = []
for state in states:
    # pull full json blob for state
    response = requests.get("https://apps.npr.org/elections20-interactive/data/counties/{}-0.json".format(state))
    # iterate through county results
    for county in response.json()['results']:
        # turn candidate vote info into a dataframe
        temp_df = pd.DataFrame(county['candidates'])
        # add in geography info
        temp_df['state'] = state
        temp_df['fips'] = county['fips']
        temp_df['rating'] = county['rating']
        result_frame.append(temp_df)
state_county_results = pd.concat(result_frame).reset_index(drop=True)
state_county_results.to_csv('pres_county_2020.csv', index=False)
