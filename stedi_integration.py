import os
import requests
import json
from pprint import pprint

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

    response_data = response.json()
    return response_data


def analyze_deductible_info(response_data):
    benefits = response_data.get("benefitsInformation", [])

    contract_deductible = None
    remaining_deductible = None

    # Find deductible information
    for benefit in benefits:
        if benefit.get("code") == "C" and benefit.get("name") == "Deductible":
            time_qualifier = benefit.get("timeQualifier")
            benefit_amount = benefit.get("benefitAmount")

            if time_qualifier == "Contract" and benefit_amount:
                contract_deductible = float(benefit_amount)
            elif time_qualifier == "Remaining" and benefit_amount:
                remaining_deductible = float(benefit_amount)

    # Calculate HDHP status: contract deductible >= 1500
    is_hdhp = 1 if contract_deductible and contract_deductible >= 1500 else 0

    # Check if deductible is met: remaining amount = 0
    deductible_met = 1 if remaining_deductible == 0 else 0

    return {"remaining_deductible": remaining_deductible, "is_hdhp": is_hdhp}


def insurance_response_message(deductible_analysis):
    if (
        deductible_analysis["is_hdhp"]
        and deductible_analysis["remaining_deductible"] >= 1000
    ):
        message = "You are enrolled in a High Deductible Health Plan (HDHP). Even though you haven't met your deductible, your insurance covers the annual visit for no aditional payment. For follow-up imaging, we are pleased to offer you a 50% cash pay discount."
    elif deductible_analysis["remaining_deductible"] == 0:
        message = "You have met your deductible for this year. Your insurance will cover the annual visit and any follow-up imaging at no additional cost to you."
    else:
        message = "We couldn't figure it out. The demo gods are not on our side."
    return message
