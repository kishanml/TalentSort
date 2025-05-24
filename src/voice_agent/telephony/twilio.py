import os
import re
PHONE_NUMBER_FROM = os.getenv('TWILIO_PHONE_NUMBER')
BACKEND_DOMAIN    = re.sub(r'(^\w+:|^)\/\/|\/+$', '', os.getenv('DOMAIN', ''))

if not (PHONE_NUMBER_FROM and BACKEND_DOMAIN):
    raise ValueError(
        "Missing Twilio env variables. Please set them in the .env file."
    )
    
from logger import logging
logger = logging.getLogger(__name__)


async def is_valid_from_number(client, from_number):
    """
    Checks if the number is a valid caller ID or Twilio number
    """
    try:
        incoming = client.incoming_phone_numbers.list(phone_number=from_number)
        if incoming:
            return True
        
        outgoing = client.outgoing_caller_ids.list(phone_number=from_number)
        if outgoing:
            return True
        return False
    except Exception as e:
        logger.error(f"Error validating from number: {e}")
        return False

    
async def make_ob_call(client, phone_number_to_call: str):
    """
    Make/Initiate outbound call
    """
    if not phone_number_to_call:
        raise ValueError("Please provide a phone number to call.")

    is_from_valid = await is_valid_from_number(client, PHONE_NUMBER_FROM)
    if not is_from_valid:
        raise ValueError(f"FROM number {PHONE_NUMBER_FROM} is not valid or verified.")

    outbound_twiml = (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<Response><Connect><Stream url="wss://{BACKEND_DOMAIN}/api/outbound/voice-agent" /></Connect></Response>'
    )
    call = client.calls.create(
        from_ = PHONE_NUMBER_FROM,
        to    = phone_number_to_call,
        twiml = outbound_twiml,
        # status_callback=f"https://{BACKEND_DOMAIN}/api/callback/call-status", 
        # status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
        # status_callback_method='POST',
        # record=True,
        # recording_status_callback=f"{os.getenv("BACKEND_DOMAIN")}/api/callback/call-recording",
        # recording_status_callback_event=["completed"],
        # recording_status_callback_method="POST",
        # machine_detection="Enable", 
        # async_amd="true", 
        # async_amd_status_callback=f"https://{BACKEND_DOMAIN}/api/callback/voicemail",
        # async_amd_status_callback_method='POST'
    )
    return call.sid