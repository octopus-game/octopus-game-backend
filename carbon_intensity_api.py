import httpx
from datetime import datetime 

def get_carbon_intensity_data(postcode=None, region_id=13):
    # If no postcode is passed, data for London regions is returned.
    headers = {'Accept': 'application/json'}
    client = httpx.Client()
    midnight = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)


    if postcode is None:
        request = client.get('https://api.carbonintensity.org.uk/regional/intensity/{midnight}/fw24h/regional/regionid/{regionid}', params={}, headers = headers)
        
    
    print (request.json())

get_carbon_intensity_data()