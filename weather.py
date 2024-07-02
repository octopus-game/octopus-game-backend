#!/usr/bin/env python3

import os
import json
import httpx

api_key = os.environ['DATAPOINT_API_KEY']

headers = {'Accept': 'application/json'}
client = httpx.Client()
request = client.get(f"http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/3840?res=3hourly&key={api_key}", params={}, headers = headers)
data = request.json()


def summary(three_hours):
  # https://www.metoffice.gov.uk/services/data/datapoint/code-definitions
  weather_type = three_hours['W']
  if weather_type == '1':    # Sunny Day
    sun = 2
  elif weather_type == '3':  #  Partly cloudy
    sun = 1
  else:
    sun = 0

  wind = int(three_hours['S'])
  temp = int(three_hours['T'])
  return { "sun": sun, "wind": wind, "temp": temp }

weather = []
# next 24 hours
forecast = data['SiteRep']['DV']['Location']['Period'][0]['Rep']
for three_hours in forecast:
  weather.append(summary(three_hours))
# add til next day 3am...
til3 = data['SiteRep']['DV']['Location']['Period'][1]['Rep'][0]
weather.append(summary(til3))

print(weather)
