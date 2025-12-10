import pandas as pd
import requests
import os 


def fetching_data(url):

    # response to the api request
    response = requests.get(url)
    # a status code of 200 means sucesfull 
    if response.status_code == 200:
        print ("data fetch succesful")
    else: 
        print(f"fetch was unsucesful: {response.status_code}")
    # coverting the data into JSON a format which can be understood 
    data = response.json()
    # the actual data we need is in the 'value' key
    actual_data = data['value']
    # converts the data into dataframe, a data structure within python with rows and columns
    df = pd.DataFrame(actual_data)
    
    return df


# need to fetch the country code data 

def country_code(country_url):   

    country_response = requests.get(country_url)

    if country_response.status_code == 200:
        print("country code data fetch good")

    else:
        print(f"country code data fetch was not good: {country_response.status_code}")

    data = country_response.json()

    actual_data = data['value']

    country_data = pd.DataFrame(actual_data)

    columns_to_keep = [
        'Code',
        'Title'
    ]
    clean_country_data = country_data[columns_to_keep]
    return clean_country_data
# CLEANING THE DATA 


def merge_country(df, clean_country_data):

    merged_df = df.merge(clean_country_data, left_on = 'SpatialDim', right_on = 'Code', how = 'left')
    return merged_df     

def cleaning_data(merged_df):

    # first keeing only the columns that we dont need
    columns_to_keep = [
        'ParentLocation', # Continent
        'SpatialDim', # country codes
        'TimeDimensionValue', # Year
        'NumericValue', # tb incidence
        'Title' # country full names
    ]

    df_clean = merged_df[columns_to_keep]

    # renaming the columns 

    df_clean = df_clean.rename(columns={
        'SpatialDim': 'country_code',
        'ParentLocation': 'continent',
        'TimeDimensionValue': 'year',
        'NumericValue': 'tb_incidence',
        'Title': 'Country'
    })

    # removing rows where continets are missing 
    df_clean = df_clean.dropna(subset=['continent'])
        
    return df_clean
       

def save_data(df_clean, save_filepath):

    df_clean.to_csv(save_filepath, index=False)
    print(f"cleaned data saved to {save_filepath}")


save_filepath = os.path.join(os.path.dirname(__file__), '..', 'data', 'tb_data_clean_updated.csv')
country_url = "https://ghoapi.azureedge.net/api/DIMENSION/COUNTRY/DimensionValues"
url = "https://ghoapi.azureedge.net/api/MDG_0000000020" 
df = fetching_data(url)
country = country_code(country_url)
merged_data = merge_country(df, country )
clean_data = cleaning_data(merged_data)
save = save_data(clean_data, save_filepath)


print(clean_data.head())
