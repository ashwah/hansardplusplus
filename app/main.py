from processes.process_test_2 import Process2
from processes.process_test_1 import Process1
from processes.process_hansard_data import ProcessHansardData
from processes.process_llm import ProcessLlm
import schedule
import signal 
import time

# Define our processes.
process_commons = ProcessHansardData('commons')
process_lords = ProcessHansardData('lords')
process_llm = ProcessLlm()

process_llm.process()
#process_commons.process()

# schedule.every(2).minutes.do(process_commons.thread)
# schedule.every(2).minutes.do(process_lords.thread)

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
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()