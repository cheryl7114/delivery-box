import RPi.GPIO as GPIO
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback
from time import sleep
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Servo setup
SERVO_PIN = 18
LOCKED = 7.5    # 90° - locked position
UNLOCKED = 2.5  # 0° - unlocked position

# PubNub setup
BOX_ID = os.getenv('BOX_ID', '1')  # Default to '1' if not set
CHANNEL = f"box-{BOX_ID}"

# Initialize GPIO
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)  # Start with no signal

def lock_door():
    """Lock the door"""
    print("🔒 Locking door...")
    pwm.ChangeDutyCycle(LOCKED)
    sleep(2)  
    pwm.ChangeDutyCycle(0)  # Stop signal after movement
    return "locked"

def unlock_door():
    """Unlock the door"""
    print("🔓 Unlocking door...")
    pwm.ChangeDutyCycle(UNLOCKED)
    sleep(2)  
    pwm.ChangeDutyCycle(0)  # Stop signal after movement
    return "unlocked"

class ServoListener(SubscribeCallback):
    def message(self, pubnub, message):
        try:
            msg = message.message
            print(f"Received message: {msg}")
            
            # Handle both string and integer box_id
            box_id = str(msg.get('box_id'))
            
            if box_id == BOX_ID:
                action = msg.get('action', '').lower()
                
                if action == 'lock':
                    status = lock_door()
                    print(f"✅ Door {status}")
                elif action == 'unlock':
                    status = unlock_door()
                    print(f"✅ Door {status}")
                else:
                    print(f"⚠️ Unknown action: {action}")
            else:
                print(f"ℹ️ Message for different box: {box_id} (expecting {BOX_ID})")
                
        except Exception as e:
            print(f"❌ Error processing message: {e}")
    
    def status(self, pubnub, status):
        print(f"Status: {status.category.name}")

def init_pubnub():
    """Initialize PubNub connection"""
    pnconfig = PNConfiguration()
    pnconfig.subscribe_key = os.getenv('PUBNUB_SUBSCRIBE_KEY')
    pnconfig.publish_key = os.getenv('PUBNUB_PUBLISH_KEY')
    pnconfig.uuid = f"box-{BOX_ID}"
    pnconfig.ssl = True
    
    pubnub = PubNub(pnconfig)
    pubnub.add_listener(ServoListener())
    
    return pubnub

try:
    print(f"🚀 Starting door lock system for Box {BOX_ID}")
    print(f"📡 Subscribing to channel: {CHANNEL}")
    
    # Initialize and subscribe to PubNub
    pubnub = init_pubnub()
    pubnub.subscribe().channels(CHANNEL).execute()
    
    print("✅ Connected! Waiting for messages...")
    print("Press Ctrl+C to exit")
    
    # Keep the script running
    while True:
        sleep(1)
        
except KeyboardInterrupt:
    print("\n⚠️ Exiting...")
finally:
    pwm.ChangeDutyCycle(LOCKED)
    sleep(1)
    pwm.stop()
    GPIO.cleanup()
    print("🔒 Door locked and system cleaned up")