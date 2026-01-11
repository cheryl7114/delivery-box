import RPi.GPIO as GPIO
import time

# Pin Configuration
LED_PIN = 17
TRIG_PIN = 27
ECHO_PIN = 4  

# Motion detection settings
DISTANCE_THRESHOLD = 12  # Distance in cm to trigger motion detection
MOTION_SENSITIVITY = 3  # Change in distance (cm) to consider as motion

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

def get_distance():
    """Measure distance using ultrasonic sensor"""
    # Send trigger pulse
    GPIO.output(TRIG_PIN, GPIO.LOW)
    time.sleep(0.002)
    GPIO.output(TRIG_PIN, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, GPIO.LOW)
    
    # Wait for echo response
    timeout = time.time() + 1
    while GPIO.input(ECHO_PIN) == GPIO.LOW:
        pulse_start = time.time()
        if pulse_start > timeout:
            return -1
    
    timeout = time.time() + 1
    while GPIO.input(ECHO_PIN) == GPIO.HIGH:
        pulse_end = time.time()
        if pulse_end > timeout:
            return -1
    
    # Calculate distance
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # Speed of sound / 2
    distance = round(distance, 2)
    
    return distance

def led_on():
    """Turn LED on"""
    GPIO.output(LED_PIN, GPIO.HIGH)
    print("LED ON - Motion detected!")

def led_off():
    """Turn LED off"""
    GPIO.output(LED_PIN, GPIO.LOW)
    print("LED OFF")

def main():
    print("Motion Detection System Started")
    print(f"LED Pin: {LED_PIN}, Trigger Pin: {TRIG_PIN}, Echo Pin: {ECHO_PIN}")
    print(f"Detection threshold: {DISTANCE_THRESHOLD}cm, Sensitivity: {MOTION_SENSITIVITY}cm")
    print("Press Ctrl+C to exit\n")
    
    previous_distance = get_distance()
    led_on_duration = 10  # Keep LED on for 10 seconds after motion
    is_detecting = True  # Flag to control detection
    
    try:
        while True:
            if is_detecting:
                current_distance = get_distance()
                
                if current_distance > 0:
                    print(f"Distance: {current_distance} cm")
                    
                    # Check for motion (significant change in distance or object within threshold)
                    distance_change = abs(current_distance - previous_distance)
                    
                    if distance_change > MOTION_SENSITIVITY or current_distance < DISTANCE_THRESHOLD:
                        led_on()
                        is_detecting = False  # Stop detecting
                        print(f"Detection paused for {led_on_duration} seconds...")
                        time.sleep(led_on_duration)  # Wait for 10 seconds
                        led_off()
                        is_detecting = True  # Resume detecting
                        previous_distance = get_distance()  # Reset baseline distance
                        print("Detection resumed")
                    else:
                        previous_distance = current_distance
                
                time.sleep(0.1)
            else:
                time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        led_off()
        GPIO.cleanup()
        print("GPIO cleaned up")

if __name__ == "__main__":
    main()
