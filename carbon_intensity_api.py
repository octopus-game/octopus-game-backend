#!/usr/bin/env python3

import httpx
from datetime import datetime, timezone

def get_carbon_intensity_data(postcode=None, region_id=13):
    # If no postcode is passed, data for London regions is returned.
    headers = {'Accept': 'application/json'}
    client = httpx.Client()
    midnight = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    if postcode is None:
        request = client.get(f"https://api.carbonintensity.org.uk/regional/intensity/{midnight.isoformat()}/fw24h/regionid/{region_id}", params={}, headers = headers)
        
    
    print(request.json())

get_carbon_intensity_data()