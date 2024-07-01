#!/usr/bin/env python3

import os
import httpx
from datetime import datetime, timezone

def date_to_index(iso_date):
  date = datetime.fromisoformat(iso_date)
  midnight = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
  from_midnight = date - midnight
  if from_midnight.days != 0:
    return None
  return int(from_midnight.seconds / 60 / 30)

api_key = os.environ['OCTOPUS_API_KEY']

auth = httpx.BasicAuth(username=api_key, password="")
client = httpx.Client()
response = client.get('https://api.octopus.energy/v1/products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-L/standard-unit-rates/', auth=auth)

data = response.json()
results = data.get('results')
by_half_hour = [None] * 48

for block in results:
  index = date_to_index(block['valid_from'])
  if index is not None:
    by_half_hour[index] = block['value_inc_vat']

print(by_half_hour)
