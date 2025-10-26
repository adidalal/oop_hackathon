import os
import requests
import json

stedi_api_key = os.environ.get("STEDI_API_KEY")


def check_eligibility():
    url = "https://healthcare.us.stedi.com/2024-04-01/change/medicalnetwork/eligibility/v3"
    body = {
        "tradingPartnerServiceId": "60054",
        "provider": {"organizationName": "Provider Name", "npi": "1999999984"},
        "subscriber": {
            "firstName": "Jane",
            "lastName": "Doe",
            "dateOfBirth": "20040404",
            "memberId": "AETNA12345",
        },
        "encounter": {"serviceTypeCodes": ["30"]},
    }

    response = requests.request(
        "POST",
        url,
        json=body,
        headers={
            "Authorization": f"Key {stedi_api_key}",
            "Content-Type": "application/json",
        },
    )

    return response.text


result = check_eligibility()
print(result)
