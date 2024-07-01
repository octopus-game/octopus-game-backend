#!/usr/bin/env python3

import os
import httpx

api_key = os.environ['OCTOPUS_API_KEY']

auth = httpx.BasicAuth(username=api_key, password="")
client = httpx.Client()
response = client.get('https://api.octopus.energy/v1/products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-L/standard-unit-rates/', auth=auth)

print(response.json())
