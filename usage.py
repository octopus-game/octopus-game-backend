#!/usr/bin/env python3

import os
import logging
from python_graphql_client import GraphqlClient

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
  query Devices(
    $accountNumber: String!
  ) {
    devices(
      accountNumber: $accountNumber
    ) {
      id
      name
      deviceType
      provider
      status {
        current
        isSuspended
        currentState
      }
      alerts {
        message
        publishedAt
      }
    }
  }
"""
variables = { "accountNumber": account_number }
data = client.execute(query=query, variables=variables, headers=headers)
print(data)

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


#  $start: DateTime,
#  $end: DateTime

query = """
  query SmartMeterTelemetry(
    $deviceId: String!
  ) {
    smartMeterTelemetry(
      deviceId: $deviceId
      grouping: TEN_SECONDS
    	start: "2024-06-30T00:00Z"
	    end: "2024-06-30T01:00Z"
    ) {
      readAt
      consumption
      demand
    }
  }
"""
# HALF_HOURLY, FIVE_MINUTES, TEN_SECONDS, ONE_MINUTE
variables = { "deviceId": meter_device_id }

data = client.execute(query=query, variables=variables, headers=headers)
print(data)


# query = """
#   query MeterPoints(
#     $mpan: ID,
#     $mprn: ID
#   ) {
#     meterPoints(
#       mpan: $mpan,
#       mprn: $mprn
#     ) {
#       status
#       meters {
#         id
#         serialNumber
#       }
#     }
#   }
# """
# variables = { "mpan": "2200018117686", "mprn": None }
# # consumption

# data = client.execute(query=query, variables=variables, headers=headers)
# print(data)

