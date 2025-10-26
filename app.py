import os
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="deck", static_url_path="")


whatsapp_token = os.environ.get("WHATSAPP_TOKEN")
verify_token = os.environ.get("VERIFY_TOKEN")
vapi_token = os.environ.get("VAPI_TOKEN")
customer_number = os.environ.get("CUSTOMER_NUMBER")


# handle incoming webhook messages
def handle_message(request):
    # Parse Request body in json format
    body = request.get_json()
    print(f"request body: {body}")

    try:
        if not body.get("object"):
            return jsonify(
                {"status": "error", "message": "Not a WhatsApp API event"}
            ), 404

        # Check for valid WhatsApp message structure
        entry = body.get("entry", [])
        if not entry:
            return jsonify({"status": "ok"}), 200

        changes = entry[0].get("changes", [])
        if not changes:
            return jsonify({"status": "ok"}), 200

        value = changes[0].get("value", {})
        messages = value.get("messages", [])

        if messages:
            handle_whatsapp_message(body)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print(f"unknown error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# https://developers.facebook.com/docs/graph-api/webhooks/getting-started#verification-requests
def verify(request):
    # Parse params from the webhook verification request
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    # Check if required parameters are missing
    if not mode or not token:
        print("MISSING_PARAMETER")
        return jsonify({"status": "error", "message": "Missing parameters"}), 400

    # Check if mode and token are correct
    if mode == "subscribe" and token == verify_token:
        print("WEBHOOK_VERIFIED")
        return challenge, 200

    # Invalid verification
    print("VERIFICATION_FAILED")
    return jsonify({"status": "error", "message": "Verification failed"}), 403


# Sets homepage endpoint to serve index.html from deck directory
@app.route("/", methods=["GET"])
def home():
    return send_from_directory("deck", "index.html")


@app.route("/ping", methods=["GET"])
def ping():
    return "babycomeback is up"


# Accepts POST and GET requests at /webhook endpoint
@app.route("/webhook", methods=["POST", "GET"])  # pyright: ignore[reportArgumentType]
def webhook():
    if request.method == "GET":
        return verify(request)
    elif request.method == "POST":
        return handle_message(request)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
