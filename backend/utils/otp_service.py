from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_otp(phone_number, otp_code):
    """
    Send OTP via SMS
    For development: prints to console
    For production: uses Twilio
    """
    
    if settings.DEBUG:
        # Development mode - print to console
        logger.info(f"🔐 OTP for {phone_number}: {otp_code}")
        print(f"\n{'='*50}")
        print(f"📱 OTP CODE: {otp_code}")
        print(f"📞 Phone: {phone_number}")
        print(f"{'='*50}\n")
        return True
    
    else:
        # Production mode - use Twilio
        try:
            from twilio.rest import Client
            
            client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            
            message = client.messages.create(
                body=f"Your PopCult verification code is: {otp_code}",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            
            logger.info(f"OTP sent successfully to {phone_number}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send OTP: {str(e)}")
            return False