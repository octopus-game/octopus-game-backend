#!/usr/bin/env python3
from rich import print
import os
import httpx
from datetime import datetime, timezone, timedelta

def date_to_index(iso_date):
  date = datetime.fromisoformat(iso_date)
  midnight = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
  from_midnight = date - midnight
  if from_midnight.days < 0:
    return None
  return int(from_midnight.seconds / 60 / 30)


def get_tariff_data():
    api_key = os.environ['OCTOPUS_API_KEY']
    auth = httpx.BasicAuth(username=api_key, password="")
    client = httpx.Client()
    midnight = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start =  midnight + timedelta(days=1)
    tomorrow_end = tomorrow_start + timedelta(hours=3)
    tariff_url = f"https://api.octopus.energy/v1/products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-C/standard-unit-rates/"
    response = client.get(tariff_url, auth=auth)
    # Type of Contract :  Cap stays at £1 per unit but new formula only deducts 17.9p from higher unit prices, https://energy-stats.uk/octopus-agile-east-midlands/
    # Tariff code is of the format T"E-1R-$PRODUCT_CODE-C" where PRODUCT_CODE here is AGILE-FLEX-22-11-25 and C is region
    # To change region, please use https://en.m.wikipedia.org/wiki/Meter_Point_Administration_Number

    print(response)
    data = response.json()
    results = data.get('results')
    by_half_hour = [None] * 48

    for block in results:
        index = date_to_index(block['valid_from'])
        if index is not None:
            by_half_hour[index] = block['value_inc_vat']
    return by_half_hour

print(get_tariff_data())