#!/usr/bin/env python3

import httpx
from datetime import datetime, timezone, timedelta
import numpy as np
from tariffs import date_to_index
from collections import Counter

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


def get_carbon_intensity_data(regionid=13):
    headers = {'Accept': 'application/json'}
    client = httpx.Client()
    midnight = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    # 12 AM TO 12 AM  
    request = client.get(f"https://api.carbonintensity.org.uk/regional/intensity/{midnight.isoformat()}/fw24h/regionid/{regionid}", params={}, headers = headers)
    intensity_data_today = request.json().get('data').get('data') # its of the format data "{metadata, data :{}}"

    # Tomorrow 12 AM to 3AM 
    tomorrow_start =  midnight + timedelta(days=1)
    tomorrow_end = tomorrow_start + timedelta(hours=3)
    request = client.get(f"https://api.carbonintensity.org.uk/regional/intensity/{tomorrow_start.isoformat()}/{tomorrow_end.isoformat()}/regionid/{regionid}", params={}, headers = headers)
    intensity_data_tomorrow = request.json().get('data').get('data')


    by_half_hour = [None] * 54
    for day in [(0,intensity_data_today), (48,intensity_data_tomorrow)]:
        buffer = day[0]
        for block in day[1]:
            index = date_to_index(block['from'])
            intensity_value = max(block['intensity'].get('forecast',0), block['intensity'].get('actual',0))
            intensity_index = block['intensity'].get('index',None)
            top_3_generation_mix = parse_generationmix(block['generationmix'])
            if index is not None:
                if buffer > 0 and index < 47:
                    index += buffer # Early hours of tomorrow 
                by_half_hour[index] = {'intensity_value':intensity_value,'intensity_index':intensity_index,'top_3_generation_mix': top_3_generation_mix}
    return by_half_hour

def get_aggregate_carbon_intensity_tariff_data(regionid=13):
    aggregate_carbon_intensity_tariff_data = {}
    carbonintensity = get_carbon_intensity_data(regionid=regionid)
    morning, afternoon, evening, night = [],[],[],[]
    time_of_day_indexes = {'morning' : (14,24), 'afternoon': (24,34) , 'evening': (34,44) , 'night': (44,54)}
    for time_of_day, indexes in time_of_day_indexes.items():
        count = 0
        intensity_sum = 0
        intensity_index_list = []
        energy_source_list = []
        energy_contribution_sum = 0

        for i in range(indexes[0],indexes[1]):
            intensity_sum += carbonintensity[i]['intensity_value']
            intensity_index_list.append(carbonintensity[i]['intensity_index'])
            if carbonintensity[i]['top_3_generation_mix'][0]['fuel'] != 'imports': # Interest in generated power rather than importsS
                energy_source_list.append(carbonintensity[i]['top_3_generation_mix'][0]['fuel'])
                energy_contribution_sum += carbonintensity[i]['top_3_generation_mix'][0]['perc']
            else:
                energy_source_list.append(carbonintensity[i]['top_3_generation_mix'][1]['fuel'])
                energy_contribution_sum += carbonintensity[i]['top_3_generation_mix'][1]['perc']
            count +=1

        average_intensity_value = intensity_sum / count 
        common_intensity_index = Counter(intensity_index_list).most_common(1)[0][0]
        common_energy_source = Counter(energy_source_list).most_common(1)[0][0]
        common_energy_source_contribution = int(energy_contribution_sum / count)
        aggregate_carbon_intensity_tariff_data[time_of_day] = {'average_carbon_intensity_value(gCO2/kWh)':average_intensity_value, 'common_intensity_index':common_intensity_index,
                                                                 'common_energy_source':common_energy_source, 'common_energy_source_contribution(%)': common_energy_source_contribution }
    return aggregate_carbon_intensity_tariff_data




    