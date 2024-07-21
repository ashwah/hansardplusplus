from processes.process_test_2 import Process2
from processes.process_test_1 import Process1
from processes.process_hansard_data import ProcessHansardData
import schedule
import signal 
import time

# Define our processes.
p1 = Process1()
p2 = Process2()
process_hansard = ProcessHansardData()

schedule.every(3).seconds.do(p1.thread)
schedule.every(2).seconds.do(p2.thread)
schedule.every(5).seconds.do(process_hansard.thread)

running = True

def signal_handler(sig, frame):
    global running

    print("Received SIGINT signal. Shutting down...")

    # Clear the schedule.
    schedule.clear()

    # Set the running flag to False to stop the main loop.
    running = False

    print("Shutdown complete.")

def main():
    global running
    while running:
        # print("Running...")
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()