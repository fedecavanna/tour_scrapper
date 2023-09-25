# --------------------------------------------------------------------------------
def get_cities(index_url, web_url):
    import requests
    from bs4 import BeautifulSoup
   
    # Get the HTML content
    html_content = requests.get(index_url).content

    # Parse the HTML using BeautifulSoup
    bsoup = BeautifulSoup(html_content, 'html.parser')

    # Find all cities
    cities = bsoup.select('.city_list_row a')

    # Initialize the result variable
    result = []
    if len(cities) > 0:
        for city in cities:
            city_info = city.text
            # If there is no ":", it's not a country from the list but one of the promoted ones
            if ":" in city_info:
                country, city_name = city_info.split(": ")
                city_url = web_url + city['href']
                # Create a dictionary name:url for each item
                city_data = {'country': country, 'city': city_name, 'url': city_url}
                result.append(city_data)
    else:
        raise Exception("Failed to get guides list")

    return result

# --------------------------------------------------------------------------------
def get_tours(country, city, url, web_url):
    import requests
    from bs4 import BeautifulSoup
    
    # Get the HTML content
    html_content = requests.get(url).content

    # Parse the HTML using BeautifulSoup
    bsoup = BeautifulSoup(html_content, 'html.parser')

    # Get all 'Sightseeing Walk' or 'Discovery Walk'
    tour_elements = bsoup.select('h3:-soup-contains("Sightseeing Walk: "), h3:-soup-contains("Discovery Walk: ")')

    # Initialize the result variable
    result = []
    if (len(tour_elements) > 0):
        for element in tour_elements:
            tour_type = element.find('span').text.strip().replace(':','')
            tour_title = element.find('a').text.strip()            
            tour_url = web_url + element.find('a')['href']
            # Create a dictionary with multiple keys for each result item
            tour_info = {'country': country, 'city': city, 'type': tour_type, 'title': tour_title, 'url': tour_url}
            result.append(tour_info)
            
    return result

# --------------------------------------------------------------------------------
def clean_text(text):
    import re    
    text = re.sub(r'\n|\r|\r\n|\\', '', text)
    text = text.strip()                
    return text
    
# --------------------------------------------------------------------------------
def get_sigthseeing_data(bsoup, content_map):
    import pandas as pd
            
    # Iterate through all guides to fill in missing data for each spot on the tour
    spot_data = []
    pin_df = pd.DataFrame(content_map["pins"], columns=["latitude", "longitude", "name", "val1", "val2"])                                       
    for index, row in pin_df.iterrows():
        # Get the guide's div
        spot_name = row['name']
        spot_div = bsoup.find("a", string=spot_name).parent.parent
        # Extract missing data
        spot_desc = clean_text(spot_div.find('div').text)
        spot_img = spot_div.find('a')['href']
        # Add the record to the results
        spot_data.append({"name": row['name'], "latitude": row['latitude'], "longitude": row['longitude'], 
                        "val1": row['val1'], "val2": row['val2'], "img": spot_img, "description": spot_desc})  
    
    return spot_data
    
# --------------------------------------------------------------------------------    
def get_discovery_data(bsoup, content_map):    
    import pandas as pd
        
    # Iterate through all guides, but I don't have data on which places they are
    spot_data = []
    pin_df = pd.DataFrame(content_map["pins"], columns=["latitude", "longitude"])                            
    for index, row in pin_df.iterrows():
        spot_data.append({"latitude": row['latitude'], "longitude": row['longitude']})                
    
    # In Discovery guides, I store images
    images_data = []
    images = bsoup.find_all('img', class_='lazyload')
    for image in images:
        images_data.append({'name': image['alt'], 'img': image['src'] }) 
        
    return images_data, spot_data          
            
# --------------------------------------------------------------------------------
def scrap_tour(tour_country, tour_city, tour_url):
    import re
    import requests
    import pandas as pd
    from werkzeug.utils import secure_filename
    from bs4 import BeautifulSoup
    import json
    import os
    
    def sanitize_string(file_path):
        invalid_chars = r'\/:*?"<>|'
        sanitized_dir_name = re.sub(f'[{re.escape(invalid_chars)}]', ' ', file_path)
        return sanitized_dir_name    
    
    # Get the web page content
    headers = {'User-Agent': 'Mozilla'}
    response = requests.get(tour_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch URL: {tour_url}")
    
    # Parse it using BeautifulSoup
    bsoup = BeautifulSoup(response.text, 'html.parser')

    # Get the following variables:
    # Guide name
    guide_name = bsoup.find('b', string='Guide Name:').next_sibling.strip()
    # Guide description
    guide_description = clean_text(bsoup.find_all(class_='tour_desc tbl')[0].text)
    # Guide duration
    guide_duration = bsoup.find('b', string='Tour Duration:').next_sibling.strip()
    # Guide spots
    script_tag = bsoup.find('script', string=re.compile(r'jarr = '))    
    spots_script = script_tag.string         
        
    # Get the JSON by finding its start and end positions within the text
    start_index = spots_script.find('jarr = {')
    end_index = spots_script.find('};', start_index) + 1    
    spots_json2 = spots_script[start_index+7:end_index]
    
    # Store all data (spots and path) in two dataframes:
    content_map = json.loads(spots_json2)
    
    # Spots (Sightseeing or Discovery):      
    if (len(content_map['pins'][0]) == 5):
        guide_type = 'sightseeing'
        spot_data = get_sigthseeing_data(bsoup, content_map)
    else:
        guide_type = 'discovery' 
        images_data, spot_data = get_discovery_data(bsoup, content_map)    
    
    # Path: Iterate through all points on the tour.
    path_df = pd.DataFrame(content_map["path"], columns=["latitude", "longitude"])         
    path_data = []   
    for index, row in path_df.iterrows():
        path_data.append({"latitude": row['latitude'], "longitude": row['longitude']})               
            
    # Generate general tour information
    guide_info = {"type": guide_type,
                  "title": guide_name, 
                  "description": guide_description,                  
                  "duration": guide_duration}
            
    # Create the result JSON    
    if (guide_type == 'sightseeing'):
        json_data = {"info": guide_info, "path": path_data, "spots": spot_data}
    elif (guide_type == 'discovery'):
        json_data = {"info": guide_info, "path": path_data, "images": images_data, "spots": spot_data}
        
    # Create the directory if it doesn't exist
    dir_path = f"{tour_country}\{sanitize_string(tour_city)}"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)    
    
    # Export the result     
    file_path = f"{dir_path}\{sanitize_string(guide_name)}.json"    
    with open(file_path, "w") as f:
        f.write(json.dumps(json_data))           
        
# --------------------------------------------------------------------------------
def main():
    import os
    import sys
    import time, random

    try:             
        web_url = 'https://www.x.com'
        index_url = 'https://www.x.com'
        
        # Set my working directory
        working_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(path=os.path.join(working_dir, 'downloads'))        
                 
        # Get the list of all cities containing tours
        city_index_list = get_cities(index_url, web_url)
                      
        # For each city, get its list of tours
        i = 0        
        for index in city_index_list:                        
            tours_list = get_tours(index['country'], index['city'], index['url'], web_url)
        
            # Extract the data
            for tour in tours_list:                            
                i += 1
                print(f'{i} - {tour["country"]}, {tour["city"]}: {tour["title"]}.')
                
                scrap_tour(tour['country'], tour['city'], tour['url'])                
                # Wait for a random amount of time to avoid overloading with requests
                time.sleep(random.uniform(0.5, 1.5))
                                
        print('Run OK')
        sys.exit(0)    
    except Exception as e:
        print(e)
        sys.exit(1)    

# --------------------------------------------------------------------------------
if __name__== "__main__":
   main()

