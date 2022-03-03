from state import get_ori_code, get_cities
from sensitive import get_keys

import requests

def get_crime_data():
    sensitive = get_keys()
    file = open("city_data.csv", "r")
    init = False
    codes = {}
    lines = []
    header = ""
    header_init = False
    for line in file:
        if not init:
            header = line.rstrip()
            init = True
            continue
        attribs = line.split(",")
        state = attribs[0].strip()
        year = attribs[1].strip()
        
        if state not in codes:
            codes[state] = {}
        if year not in codes[state]:
            codes[state][year] = get_ori_code(state, get_cities(int(year), state))
        
        cityName = attribs[2].strip()
        state_codes = codes[state][year][0]
        not_found = codes[state][year][1]
        
        if cityName not in not_found:
            ori = state_codes[cityName]
            print("ORI: ", ori, cityName)
            url = "https://api.usa.gov/crime/fbi/sapi/api/summarized/agencies/{}/offenses/{}/{}?API_KEY={}".format(ori, year, year, sensitive["FBI_API"])
            
            response = requests.get(url.strip())
            data = response.json()
           
            # collect attrib names
            attribs = {}
            try:
                results = data["results"]
                if len(results) == 0: # Sometimes FBI returns empty list as results
                    continue 
                           
                for value in results:
                    attribs[value["offense"]] = value["actual"]
                
                line = line.rstrip() # remove newline
                aLine = ""
                for i, key in enumerate(sorted(attribs)):
                    head = ""
                    if i == 0:
                        aLine += ",{}, ".format(attribs[key])
                        head += ",{}, ".format(key)
                    elif i < (len(attribs) - 1):
                        aLine += "{}, ".format(attribs[key])
                        head += "{}, ".format(key)
                    else:
                        aLine += "{}\n".format(attribs[key])
                        head += "{}\n".format(key)
                        
                    if not header_init:
                        header += head
                        
                header_init = True
                line += aLine
                lines.append(line)
                print(year)
            except: # if FBI has no data for this city, skip
                continue
    file = open("data.csv", "w")
    file.write(header)
    for line in lines:
        file.write(line)