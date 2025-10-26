import os
import requests
from time import sleep

whatsapp_token = os.environ.get("WHATSAPP_TOKEN")
whatsapp_phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
vapi_token = os.environ.get("VAPI_TOKEN")
customer_number = os.environ.get("CUSTOMER_NUMBER")
base_url = os.environ.get("BASE_URL")

from stedi_integration import insurance_response_message


def send_start_message_to_number(phone_number):
    """Send the start message directly to a phone number"""
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
        "Content-Type": "application/json",
    }

    url = f"https://graph.facebook.com/v24.0/{whatsapp_phone_number_id}/messages"

    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": get_start_message()},
    }

    response = requests.post(url, json=data, headers=headers)
    print(f"whatsapp start message response: {response.json()}")
    response.raise_for_status()


def send_whatsapp_message(body, message):
    """Send a WhatsApp message back to the user"""
    value = body["entry"][0]["changes"][0]["value"]
    phone_number_id = value["metadata"]["phone_number_id"]
    from_number = value["messages"][0]["from"]

    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
        "Content-Type": "application/json",
    }

    url = f"https://graph.facebook.com/v24.0/{phone_number_id}/messages"

    data = {
        "messaging_product": "whatsapp",
        "to": from_number,
        "type": "text",
        "text": {"body": message},
    }

    response = requests.post(url, json=data, headers=headers)
    print(f"whatsapp message response: {response.json()}")
    response.raise_for_status()


def send_whatsapp_image(body, filename, caption=""):
    """Send a WhatsApp image message to the user"""
    value = body["entry"][0]["changes"][0]["value"]
    phone_number_id = value["metadata"]["phone_number_id"]
    from_number = value["messages"][0]["from"]

    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
        "Content-Type": "application/json",
    }

    url = f"https://graph.facebook.com/v24.0/{phone_number_id}/messages"

    image_url = f"{base_url}/images/{filename}"

    data = {
        "messaging_product": "whatsapp",
        "to": from_number,
        "type": "image",
        "image": {"link": image_url, "caption": caption},
    }

    response = requests.post(url, json=data, headers=headers)
    print(f"whatsapp image response: {response.json()}")
    response.raise_for_status()


def get_start_message():
    """Return the initial START message with options"""
    return """
    Hi there! We've missed seeing you at OOP OB and want to make it easy to get back on track with your care. Could you let us know what's been holding you back? Just reply with the number that fits best:
    1️⃣ I moved to a new address
    2️⃣ My insurance changed
    3️⃣ I had a bad experience
    4️⃣ I feel nervous or anxious about the appointment
    5️⃣ I'm worried about the cost
    6️⃣ I forgot to schedule
    Your response will help us make your next visit smooth and worry-free!"""


def handle_address_change():
    """Handle when user moved to a new address (option 1)"""
    return "Thank you for letting us know you moved! Please provide your new address so we can update our records."


def handle_insurance_change():
    """Handle when user's insurance changed (option 2)"""
    return "Thanks for the update on your insurance! Please share the details of your new insurance provider and policy number."


def handle_bad_experience():
    """Handle when user had a bad experience (option 3)"""
    return "We're sorry to hear about your experience. Please let us know what happened so we can address your concerns and improve our services."


def handle_appointment_anxiety(body):
    """Handle when user feels nervous about appointment (option 4)"""
    response = "We completely understand that visiting the office can feel a bit stressful, especially for OB care. I'd love to give you a quick call to chat about any worries and help make your next visit as comfortable as possible."
    send_whatsapp_message(body, response)
    sleep(5)

    # Initiate VAPI call
    requests.post(
        "https://api.vapi.ai/call",
        headers={
            "Authorization": f"Bearer {vapi_token}",
        },
        json={
            "assistantId": "32a48e34-f3e6-47a0-a0ba-f1d41ba69f1e",
            "customer": {"number": customer_number},
            "phoneNumberId": "7d6fc291-3058-4019-96a8-de81778ed9b5",
        },
    )


def handle_cost_concern():
    """Handle when user is concerned about procedure cost (option 5)"""
    # TODO: stedi integration
    hardcoded_analysis = {"remaining_deductible": 2000, "is_hdhp": 1}
    return insurance_response_message(hardcoded_analysis)


def handle_forgot_to_schedule():
    """Handle when user forgot to schedule (option 6)"""
    return "No worries! Let's get you scheduled. Please provide your preferred dates and times for an appointment."


def handle_whatsapp_message(body):
    """Main function to handle incoming WhatsApp messages"""
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    if message["type"] == "text":
        message_body = message["text"]["body"].upper()
    if not message_body:  # pyright: ignore[reportPossiblyUnboundVariable]
        return

    if message_body == "START":
        response = get_start_message()
    elif message_body == "1":
        response = handle_address_change()
    elif message_body == "2":
        response = handle_insurance_change()
    elif message_body == "3":
        response = handle_bad_experience()
    elif message_body == "4":
        handle_appointment_anxiety(body)
        return
    elif message_body == "5":
        send_whatsapp_message(body, "😂")
        send_whatsapp_image(body, "galaxybrain.jpg", caption="galaxybrain")
        response = handle_cost_concern()
        send_whatsapp_message(body, response)
        return
    elif message_body == "6":
        response = handle_forgot_to_schedule()
    else:
        response = message_body

    send_whatsapp_message(body, response)
