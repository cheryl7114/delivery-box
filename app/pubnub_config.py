import os
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory, PNReconnectionPolicy
from pubnub.models.consumer.v3.channel import Channel

def init_pubnub():
    """Initialize PubNub configuration for server (with secret key)"""
    subscribe_key = os.getenv('PUBNUB_SUBSCRIBE_KEY')
    publish_key = os.getenv('PUBNUB_PUBLISH_KEY')
    secret_key = os.getenv('PUBNUB_SECRET_KEY')
    
    # Return None if keys are not configured
    if not subscribe_key or not publish_key:
        print("⚠️ PubNub keys not configured - notifications disabled")
        return None
    
    pnconfig = PNConfiguration()
    pnconfig.subscribe_key = subscribe_key
    pnconfig.publish_key = publish_key
    pnconfig.secret_key = secret_key  # Required for PAM
    pnconfig.uuid = "delivery-box-server"
    pnconfig.ssl = True
    pnconfig.connect_timeout = 10
    pnconfig.non_subscribe_request_timeout = 10
    pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR
    
    return PubNub(pnconfig)

def generate_token(pubnub, user_id=None, box_id=None, ttl=1440):
    """Generate PubNub access token
    
    Args:
        pubnub: PubNub instance
        user_id: User ID (required for user tokens)
        box_id: Box ID (required for hardware tokens)
        ttl: Token time-to-live in minutes (default 24 hours)
    
    Returns:
        str: Access token
    """
    if pubnub is None:
        return None
    
    try:
        # Build token permissions
        if box_id:
            # Hardware token (load cell, servo) - for Raspberry Pi
            channels = [
                Channel.id(f"box-{box_id}").read(),
                Channel.id(f"load-cell-control-{box_id}").read(),
                Channel.pattern("user-.*").write()  # Pattern for writing to any user channel
            ]
            
            envelope = pubnub.grant_token()\
                .ttl(ttl)\
                .authorized_uuid(f"box-{box_id}-device")\
                .channels(channels)\
                .sync()
                
        elif user_id:
            # User token (web frontend) - simple read access
            channels = [
                Channel.id(f"user-{user_id}").read()
            ]
            
            envelope = pubnub.grant_token()\
                .ttl(ttl)\
                .authorized_uuid(f"user-{user_id}")\
                .channels(channels)\
                .sync()
        else:
            raise ValueError("Either user_id or box_id must be provided")
        
        return envelope.result.token
    except Exception as e:
        print(f"❌ Error generating token: {e}")
        import traceback
        traceback.print_exc()
        return None

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