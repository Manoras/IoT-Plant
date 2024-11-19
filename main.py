import signal
import sys
from Core import IoTPlantSystem

def signal_handler(sig, frame):
    print("\nReceived shutdown signal...")
    if 'system' in globals():
        system.stop()
    sys.exit(0)

def main():
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize and start the system
        global system
        system = IoTPlantSystem()
        system.start()
    except Exception as e:
        print(f"Fatal error: {e}")
        if 'system' in globals():
            system.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()