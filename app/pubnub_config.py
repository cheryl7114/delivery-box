import os
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

def init_pubnub():
    """Initialize PubNub configuration"""
    pnconfig = PNConfiguration()
    pnconfig.subscribe_key = os.getenv('PUBNUB_SUBSCRIBE_KEY')
    pnconfig.publish_key = os.getenv('PUBNUB_PUBLISH_KEY')
    pnconfig.uuid = "delivery-box-server"
    pnconfig.ssl = True  # Enable SSL for production
    
    return PubNub(pnconfig)

def publish_message(pubnub, channel, message):
    # Helper function to publish messages to PubNub
    try:
        pubnub.publish().channel(channel).message(message).sync()
        return True
    except Exception as e:
        print(f"PubNub publish error: {e}")
        return False

def notify_user(pubnub, user_id, notification_type, data):
    # Send notification to a specific user
    channel = f"user-{user_id}"
    message = {
        "type": notification_type,
        **data
    }
    return publish_message(pubnub, channel, message)