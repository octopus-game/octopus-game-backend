#!/usr/bin/env python3

import os
import logging
from python_graphql_client import GraphqlClient
from datetime import datetime, timezone, timedelta

#logging.basicConfig(level=logging.DEBUG)
                  
client = GraphqlClient(endpoint="https://api.octopus.energy/v1/graphql/")

api_key = os.environ['OCTOPUS_API_KEY']
account_number = os.environ['OCTOPUS_ACCOUNT']
#print(api_key)

auth = """
  mutation obtainKrakenToken($input: ObtainJSONWebTokenInput!) {
    obtainKrakenToken(input: $input) {
      token
      payload
      refreshToken
      refreshExpiresIn
    }
  }
"""
variables = { "input": { "APIKey": api_key } }
data = client.execute(query=auth, variables=variables)
#print(data)
token = data['data']['obtainKrakenToken']['token']
headers = { "Authorization": token }


query = """
  query OctocareUsageInfo($accountNumber: String!) {
    octocareUsageInfo(accountNumber: $accountNumber) {
      meterDeviceId
      propertyAddressLine1
    }
  }
"""
variables = { "accountNumber": account_number }
data = client.execute(query=query, variables=variables, headers=headers)
meter_device_id = data['data']['octocareUsageInfo']['meterDeviceId']
print(meter_device_id)



query = """
  query SmartMeterTelemetry(
    $deviceId: String!,
    $start: DateTime,
    $end: DateTime
  ) {
    smartMeterTelemetry(
      deviceId: $deviceId
      grouping: HALF_HOURLY
    	start: $start
	    end: $end
    ) {
      readAt
      consumptionDelta
      demand
    }
  }
"""
# HALF_HOURLY, FIVE_MINUTES, TEN_SECONDS, ONE_MINUTE
midnight = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

variables = { "deviceId": meter_device_id, "start": (midnight - timedelta(days=1)).isoformat(), "end": midnight.isoformat() }
data = client.execute(query=query, variables=variables, headers=headers)
#print(data)

def date_to_index(iso_date, offset_days=0):
  date = datetime.fromisoformat(iso_date)
  midnight = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=offset_days)
  from_midnight = date - midnight
  if from_midnight.days != 0:
    return None
  return int(from_midnight.seconds / 60 / 30)

by_half_hour = [None] * 48

results = data['data']['smartMeterTelemetry']
for block in results:
  index = date_to_index(block['readAt'], offset_days=-1)
  if index is not None:
    by_half_hour[index] = float(block['consumptionDelta'])

print(by_half_hour)