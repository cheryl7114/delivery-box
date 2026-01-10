#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import os
import requests
from hx711 import HX711
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load cell configuration
DT_PIN = 5   # GPIO pin for data
SCK_PIN = 6  # GPIO pin for clock

EMPTY_THRESHOLD = 50  # Box is considered empty if weight < 50g
DELIVERY_THRESHOLD = 100  # Weight must exceed this to trigger delivery (in grams)

# Box configuration
BOX_ID = os.getenv('BOX_ID', '1')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5001')

class LoadCellSensor:
    def __init__(self, dt_pin=DT_PIN, sck_pin=SCK_PIN):
        """Initialize the load cell sensor"""
        self.hx = HX711(dt_pin, sck_pin)
        self.hx.set_reading_format("MSB", "MSB")
        self.hx.set_reference_unit(1)  
        self.hx.reset()
        self.hx.tare()
        
        self.previous_weight = 0
        self.delivery_detected = False
        self.was_empty = True  # Track previous empty state
        
        print("Load cell initialized and tared")
    
    def get_weight(self, samples=10):
        """Get average weight reading in grams"""
        try:
            weight = self.hx.get_weight(samples)
            return max(0, weight)  # Return 0 if negative
        except Exception as e:
            print(f"Error reading weight: {e}")
            return None
    
    def is_empty(self):
        """Check if box is empty (weight below threshold)"""
        weight = self.get_weight()
        if weight is None:
            return None  # Error reading sensor
        
        is_empty = weight < EMPTY_THRESHOLD
        
        # Only print when state changes
        if is_empty != self.was_empty:
            if is_empty:
                print("Box is empty")
            else:
                print("Weight present - parcel detected")
            self.was_empty = is_empty
        
        return is_empty
    
    def check_delivery(self):
        """Check if a delivery has been made (weight increased significantly)"""
        current_weight = self.get_weight()
        
        if current_weight is None:
            return False
        
        # Detect if weight increased above delivery threshold
        if current_weight >= DELIVERY_THRESHOLD and self.previous_weight < DELIVERY_THRESHOLD:
            print(f"🚨 DELIVERY DETECTED! Weight: {current_weight:.1f}g")
            self.delivery_detected = True
            self.previous_weight = current_weight
            return True
        
        self.previous_weight = current_weight
        return False
    
    def cleanup(self):
        """Clean up GPIO"""
        GPIO.cleanup()


def init_pubnub():
    """Initialize PubNub connection"""
    token = os.getenv('PUBNUB_TOKEN')  # PAM token
    
    pnconfig = PNConfiguration()
    pnconfig.subscribe_key = os.getenv('PUBNUB_SUBSCRIBE_KEY')
    pnconfig.publish_key = os.getenv('PUBNUB_PUBLISH_KEY')
    pnconfig.user_id = f"box-{BOX_ID}-device"  # Must match token's authorized_uuid
    pnconfig.ssl = True
    
    pubnub = PubNub(pnconfig)
    
    # Set PAM token if available
    if token:
        pubnub.set_token(token)
        print(f"🔐 PAM token enabled for box-{BOX_ID}-device")
    else:
        print("⚠️ No PAM token - connection may fail if Access Manager is enabled")
    
    return pubnub


def get_expected_parcel(box_id):
    """Query backend for parcel expected in this box"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/box/{box_id}/expected-parcel",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('parcel_id')
        return None
    except Exception as e:
        print(f"Error getting expected parcel: {e}")
        return None


def notify_delivery_http(box_id, parcel_id):
    """Notify backend via HTTP that parcel has been delivered"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/parcel-delivered",
            json={"parcel_id": parcel_id},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data.get('message', 'Delivery confirmed')}")
            return True
        else:
            data = response.json()
            print(f"❌ Failed: {data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to notify backend via HTTP: {e}")
        return False


def notify_delivery_pubnub(pubnub, box_id, parcel_id):
    """Notify via PubNub for real-time UI updates"""
    channel = "parcel-delivery"
    message = {
        "box_id": box_id,
        "parcel_id": parcel_id,
        "action": "delivered",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        pubnub.publish().channel(channel).message(message).sync()
        print(f"📡 Real-time notification sent via PubNub")
        return True
    except Exception as e:
        print(f"⚠️ Failed to send PubNub notification: {e}")
        return False


def monitor_deliveries(sensor, pubnub):
    """Continuously monitor for deliveries in this box"""
    print(f"📦 Monitoring Box {BOX_ID} for parcel deliveries...")
    print(f"Backend: {BACKEND_URL}")
    print("Press Ctrl+C to exit\n")
    
    try:
        while True:
            if sensor.check_delivery():
                # Delivery detected! Get expected parcel from backend
                print(f"📬 Delivery detected in Box {BOX_ID}")
                print("Checking which parcel is expected in this box...")
                
                parcel_id = get_expected_parcel(BOX_ID)
                
                if parcel_id:
                    print(f"Found expected parcel: {parcel_id}")
                    
                    # Notify via PubNub
                    pubnub_success = notify_delivery_pubnub(pubnub, BOX_ID, parcel_id)
                    
                    if pubnub_success:
                        print("✅ Delivery notification sent successfully")
                else:
                    print("⚠️ No parcel expected in this box. Delivery not recorded.")
                
                # Wait for parcel to be collected before detecting next delivery
                print("\nWaiting for parcel to be collected...")
                while not sensor.is_empty():
                    time.sleep(2)
                
                print("Box is empty again. Ready for next delivery.\n")
                sensor.delivery_detected = False
            
            time.sleep(1)  # Check every second
            
    except KeyboardInterrupt:
        print("\n⚠️ Stopping monitoring...")


def calibrate():
    """Calibration script - run this once to calibrate your load cell"""
    print("Starting load cell calibration...")
    print("Remove all weight from the load cell")
    input("Press Enter when ready...")
    
    sensor = LoadCellSensor()
    
    print("\nPlace a known weight on the load cell (e.g., 100g)")
    known_weight = float(input("Enter the weight in grams: "))
    
    print("Reading...")
    time.sleep(2)
    reading = sensor.hx.get_value(10)
    
    reference_unit = reading / known_weight
    print(f"\nCalibration complete!")
    print(f"Reference unit: {reference_unit}")
    print(f"Update the reference unit in load_cell.py: self.hx.set_reference_unit({reference_unit})")
    
    sensor.cleanup()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        calibrate()
    else:
        # Monitor mode - monitors the box specified in BOX_ID env variable
        sensor = LoadCellSensor()
        pubnub = init_pubnub()
        
        try:
            monitor_deliveries(sensor, pubnub)
        finally:
            sensor.cleanup()