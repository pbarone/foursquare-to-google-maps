import requests
import json
from colorama import Fore
import csv

from dotenv import load_dotenv
import os
load_dotenv()

# Retrieve teh Fourquare access token in the .env file. To get access to the access token visit https://studio.foursquare.com/map/tokens.html 
FSQACCESS_TOKEN = os.getenv('FSQACCESS_TOKEN')


APIVERSION = "20241120"



def export_to_csv(obj, filename):
    """
    Exports a list of dictionaries (or a single dictionary) to a CSV file.
    
    Args:
        obj (list[dict] | dict): The object(s) to export. Can be a list of dictionaries or a single dictionary.
        filename (str): The name of the CSV file to create.
    """
    # Ensure obj is a list of dictionaries
    if isinstance(obj, dict):
        obj = [obj]

    # Validate input
    if not all(isinstance(item, dict) for item in obj):
        raise ValueError("Input must be a dictionary or a list of dictionaries.")

    # Generate headers dynamically from keys of the first object
    headers = obj[0].keys() if obj else []

    # Write to CSV
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(obj)

url = f"https://api.foursquare.com/v2/users/self/lists?limit=200"

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {FSQACCESS_TOKEN}",
    }

params = {
        "v": APIVERSION  # API version (YYYYMMDD format)
    }

response = requests.get(url, headers=headers, params=params)

if response.status_code != 200:
    print(Fore.RED + "Error: " + response.text)
    print(Fore.WHITE)
    exit()

# convert response to json object
responseObj = json.loads(response.text)

listGroups = responseObj['response']['lists']['groups'][1]['items']

AllPlaces = []

for listGroup in listGroups:
    print(Fore.RED + listGroup['id'] + " - " + listGroup['name'])
    print(Fore.WHITE)

    listGroupID = listGroup['id']


    url = f"https://api.foursquare.com/v2/lists/{listGroupID}"

    listGroupResponse = requests.get(url, headers=headers, params=params)
    listGroupResponseObj = json.loads(listGroupResponse.text)
    
    places = listGroupResponseObj['response']['list']['listItems']['items']

    placeCount = 1
    for place in places:
        try: 
            thisPlace = {
                "index": placeCount,
                "ListName": listGroup['name'], 
                "id": place['venue']['id'],
                "name": place['venue']['name'],
                "address": place['venue']['location']['address'],
                "city": place['venue']['location']['city'],
                "state": place['venue']['location']['state'],
                "country": place['venue']['location']['country'],
                "lat": place['venue']['location']['lat'],
                "lng": place['venue']['location']['lng'],
                #"categories": place['venue']['categories'],
                #"url": place['venue']['url']
            }
            print(Fore.GREEN + f"{placeCount:0>5} - {place['venue']['name']}")
            print(Fore.WHITE)
            AllPlaces.append(thisPlace)

            placeCount += 1

        except Exception as e:
            print("no name")
        
    
export_to_csv(AllPlaces, 'allplaces.csv')

print("done")

# get list items
# listGroupResponseObj = json.loads(ListResponse.text) 
# ListResponseObj['response']['list']['listItems']['items'][0]['venue']