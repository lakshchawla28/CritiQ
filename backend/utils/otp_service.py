from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_otp(phone_number: str, otp_code: str) -> bool:
    """
    Send OTP via SMS.
    - In DEBUG: logs and prints the OTP.
    - In production: attempts to send via Twilio (if configured).
    Returns True on success, False on failure.
    """
    if getattr(settings, "DEBUG", False):
        logger.info(f"[DEV] OTP for {phone_number}: {otp_code}")
        # Keep a console-friendly print for local dev convenience
        print(f"\n{'='*40}")
        print(f"OTP CODE: {otp_code}")
        print(f"Phone: {phone_number}")
        print(f"{'='*40}\n")
        return True

    # Production: require Twilio settings
    try:
        from twilio.rest import Client
    except Exception as e:
        logger.error("Twilio client not available: %s", e)
        return False

    sid = getattr(settings, "TWILIO_ACCOUNT_SID", None)
    token = getattr(settings, "TWILIO_AUTH_TOKEN", None)
    from_number = getattr(settings, "TWILIO_PHONE_NUMBER", None)

    if not all([sid, token, from_number]):
        logger.error("Twilio configuration missing in settings.")
        return False

    try:
        client = Client(sid, token)
        client.messages.create(
            body=f"Your PopCult verification code is: {otp_code}",
            from_=from_number,
            to=phone_number
        )
        logger.info("OTP sent successfully to %s", phone_number)
        return True
    except Exception as e:
        logger.exception("Failed to send OTP to %s: %s", phone_number, e)
        return False

