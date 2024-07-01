#!/usr/bin/env python3

import httpx
from datetime import datetime, timezone
import numpy as np

def date_to_index(iso_date):
  date = datetime.fromisoformat(iso_date)
  midnight = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
  from_midnight = date - midnight
  if from_midnight.days != 0:
    return None
  return int(from_midnight.seconds / 60 / 30)

def parse_generationmix(generationmix):
    fuel_list = []
    perc_list = []
    top_3_generation_mix = []
    for fuel_dict in generationmix:
        fuel_list.append(fuel_dict['fuel'])
        perc_list.append(fuel_dict['perc'])
    sorted_perc_list = np.argsort(perc_list)[::-1]
    for index in sorted_perc_list[:3]:
        top_3_generation_mix.append({'fuel':fuel_list[index],'perc':perc_list[index]})
    return top_3_generation_mix
    
def get_carbon_intensity_data(postcode=None, region_id=13):
    # If no postcode is passed, data for London regions is returned.
    headers = {'Accept': 'application/json'}
    client = httpx.Client()
    midnight = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    if postcode is None:
        request = client.get(f"https://api.carbonintensity.org.uk/regional/intensity/{midnight.isoformat()}/fw24h/regionid/{region_id}", params={}, headers = headers)
    else:
        request = client.get(f"https://api.carbonintensity.org.uk/regional/intensity/{midnight.isoformat()}/fw24h/regionid/{region_id}", params={}, headers = headers)
    
    request_data = request.json().get('data')
    intensity_data = request_data.get('data')
    by_half_hour = [None] * 48
    for block in intensity_data:
        index = date_to_index(block['from'])
        intensity_value = max(block['intensity'].get('forecast',0), block['intensity'].get('actual',0))
        intensity_index = block['intensity'].get('index',None)
        top_3_generation_mix = parse_generationmix(block['generationmix'])
        if index:
            by_half_hour[index] = {'intensity_value':intensity_value,'intensity_index':intensity_index,'top_3_generation_mix': top_3_generation_mix}

    return by_half_hour

print(get_carbon_intensity_data())