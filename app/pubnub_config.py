import os
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory

def init_pubnub():
    """Initialize PubNub configuration"""
    subscribe_key = os.getenv('PUBNUB_SUBSCRIBE_KEY')
    publish_key = os.getenv('PUBNUB_PUBLISH_KEY')
    
    # Return None if keys are not configured
    if not subscribe_key or not publish_key:
        print("⚠️ PubNub keys not configured - notifications disabled")
        return None
    
    pnconfig = PNConfiguration()
    pnconfig.subscribe_key = subscribe_key
    pnconfig.publish_key = publish_key
    pnconfig.uuid = "delivery-box-server"
    pnconfig.ssl = True
    pnconfig.connect_timeout = 10
    pnconfig.non_subscribe_request_timeout = 10
    
    return PubNub(pnconfig)

def publish_message(pubnub, channel, message):
    """Helper function to publish messages to PubNub (non-blocking)"""
    if pubnub is None:
        print("PubNub not initialized - skipping publish")
        return False
    
    try:
        # Use async publish to avoid blocking
        def callback(envelope, status):
            if status.is_error():
                print(f"PubNub publish error: {status.error_data}")
            else:
                print(f"📡 Message published to {channel}")
        
        pubnub.publish().channel(channel).message(message).pn_async(callback)
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