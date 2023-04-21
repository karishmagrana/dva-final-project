# %%
from pynytimes import NYTAPI
from datetime import datetime
from gspread_pandas import Spread, conf
import os
import pandas as pd
import geocoder

# %%
def init():
     return conf.get_config(conf_dir= os.getcwd(), file_name=r'C:\Users\cyoha\Downloads\nyt\secrets.json') 
def updateSheet(spreadsheet, name, data):
    
    spread = Spread(spreadsheet, config=init())
    
    found = False
    for worksheet in spread.sheets:
        if(name in worksheet.title):
            found = True
            
            
    if not found:
        print("adding {}".format(name))
        spread.create_sheet(name)
    else:
        print("clear")
        spread.clear_sheet(sheet = name)
    
    spread.df_to_sheet(data, index=False, headers=True, start=(1, 1), replace=False, sheet=name, raw_columns=None, freeze_index=False, freeze_headers=True, fill_value='', add_filter=True, merge_headers=False, flatten_headers_sep=None)
    print("finished update {} succesfully".format(name))

# %%
nyt = NYTAPI("Bhsi0IoDjMDMTHSqOOWbdpRaIiw8Tg5a", parse_dates=True)

# %%
#per https://pynytimes.michadenheijer.com/popular/top-stories sections are as below
sections = "arts, automobiles, books, business, fashion, food, health, home, insider, magazine, movies, national, nyregion, obituaries, opinion, politics, realestate, science, sports, sundayreview, technology, theater, tmagazine, travel, upshot, world"
sections = sections.split(", ")
story = []
for section in sections:
    top_stories = nyt.top_stories(section)
    story.extend(top_stories)

# %%
most_viewed = nyt.most_viewed(days = 30)


# %%
most_shared_email = nyt.most_shared(
    days = 30,
    method = "email"
)

# %%
most_shared_facebook = nyt.most_shared(
    days = 30,
    method = "facebook"
)


# %%
latest = nyt.latest_articles(
)

# %%
dataframes = [pd.DataFrame(latest), pd.DataFrame(most_shared_email), pd.DataFrame(most_viewed), pd.DataFrame(story), pd.DataFrame(most_shared_facebook)] 
combined_df = pd.concat(dataframes, axis=0, ignore_index=True, sort=False)

# %%
combined_df.columns

# %%
updateSheet("NYTAPI output", "output", combined_df)

# %%
def extract_city(facet):
    if '(' in facet and ')' in facet:
        return facet.split('(')[0].strip()
    else:
        return facet

# %%

#start clean
# Create a new DataFrame to store the duplicated rows
new_df = pd.DataFrame()
# Iterate over each row in the original DataFrame
for idx, row in combined_df.iterrows():
    # Get the list of geo facets for the current row
    geo_facets = row['geo_facet']
    # If there are multiple geo facets, duplicate the row for each one
    if isinstance(geo_facets, list):
        for facet in geo_facets:
            # Create a new row with the current geo facet
            print(facet)
            new_row = row.copy()
            new_row['geo_facet'] = facet
            
            # Add the new row to the new DataFrame
            new_df = pd.concat([new_df, pd.DataFrame(new_row).T], axis=0)
    # If there is only one geo facet, simply add the original row to the new DataFrame
    else:
        new_df = pd.concat([new_df, pd.DataFrame(row).T], axis=0)

# Reset the index of the new DataFrame
new_df.reset_index(inplace=True, drop=True)



# %%
# define a function to get the city, country, and state information
def get_location_info(location):
    if location is not None:
        location = extract_city(location)
        g = geocoder.osm(location, language='en')
        city = g.city
        country = g.country
        state = g.state
        print(pd.Series([city, country, state]))
        return pd.Series([city, country, state])
    else: 
        return pd.Series([None, None, None])
df = new_df
# apply the function to the geo_facet column and add the resulting columns to the dataframe
df[['city', 'country', 'state']] = df['geo_facet'].apply(get_location_info)

# %%
updateSheet("NYTAPI output", "clean", df)


