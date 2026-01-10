#!/usr/bin/env python3
"""
Helper script to generate PubNub tokens for hardware devices
Usage: python3 get_token.py
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import pubnub_config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from pubnub_config import init_pubnub, generate_token

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'app', '.env'))

def main():
    print("\n" + "="*60)
    print("🔐 PubNub Token Generator for Hardware")
    print("="*60)
    
    # Get box ID
    box_id = os.getenv('BOX_ID')
    if not box_id:
        box_id = input("\nEnter Box ID (default: 1): ").strip() or "1"
    
    # Initialize PubNub
    print("\n📡 Initializing PubNub...")
    pubnub = init_pubnub()
    
    if not pubnub:
        print("❌ Failed to initialize PubNub. Check your .env configuration.")
        return
    
    # Generate token
    print(f"🔑 Generating hardware token for Box {box_id}...")
    token = generate_token(pubnub, box_id=box_id, ttl=43200)  # 30 days
    
    if token:
        print("\n✅ Token generated successfully!")
        print("\n" + "="*60)
        print("Add this to your hardware .env file:")
        print("="*60)
        print(f"\nPUBNUB_TOKEN={token}")
        print("\n" + "="*60)
        print("\nThis token will expire in 30 days.")
        print("It grants access to:")
        print(f"  - Read from: box-{box_id} (servo commands)")
        print(f"  - Read from: load-cell-control-{box_id} (load cell commands)")
        print(f"  - Write to: user-* (notifications to any user)")
    else:
        print("❌ Failed to generate token")

if __name__ == "__main__":
    main()
