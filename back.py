import sys
import datetime # TODO Is this necessary
import postcodes_io_api





print("Backend Server Started")
orders = []


apiFail = False
validPostcode = False
try:
    api = postcodes_io_api.Api()
    validPostcode = api.is_postcode_valid("nn57nw")
except:
    print("There was an error accessing the Postcodes IO API. Unable to verify postcode")
    apiFail = True