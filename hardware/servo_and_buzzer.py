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

# Buzzer setup
BUZZER_PIN = 23  

# PubNub setup
BOX_ID = os.getenv('BOX_ID', '1')  # Default to '1' if not set
CHANNEL = f"box-{BOX_ID}"

# Initialize GPIO
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
servo_pwm = GPIO.PWM(SERVO_PIN, 50)
servo_pwm.start(0)  # Start with no signal
buzzer_pwm = GPIO.PWM(BUZZER_PIN, 500)  # 500Hz tone for piezo buzzer

def beep(duration=0.1, times=1):
    """Make the buzzer beep using PWM"""
    for _ in range(times):
        buzzer_pwm.start(50)  # 50% duty cycle
        sleep(duration)
        buzzer_pwm.stop()
        sleep(duration)

def lock_door():
    """Lock the door"""
    print("🔒 Locking door...")
    servo_pwm.ChangeDutyCycle(LOCKED)
    sleep(2)  
    servo_pwm.ChangeDutyCycle(0)  # Stop signal after movement
    beep(0.1, 2)  # Short double beep
    return "locked"

def unlock_door():
    """Unlock the door"""
    print("🔓 Unlocking door...")
    servo_pwm.ChangeDutyCycle(UNLOCKED)
    sleep(2)  
    servo_pwm.ChangeDutyCycle(0)  # Stop signal after movement
    beep(0.2, 1)  # Single longer beep
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
    servo_pwm.ChangeDutyCycle(LOCKED)
    sleep(1)
    servo_pwm.stop()
    buzzer_pwm.stop()
    GPIO.cleanup()
    print("🔒 Door locked and system cleaned up")