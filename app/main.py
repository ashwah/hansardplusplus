from threading import Thread, Lock
from processes.check_hansard_site import check_hansard_site
from db.db import Database
import schedule
import time
import datetime
from abc import ABC, abstractmethod
from processes.process_test_1 import Process1
from processes.process_test_2 import Process2
import signal 

db = Database()

def process_check_hansard_site():
    print("Checking Hansard site...")
    # Start from yesterday
    current_date = datetime.date.today() - datetime.timedelta(days=1) 
    processed = db.getProcessedDates()

    loop = True
    while loop:

        if current_date < datetime.date(2023, 11, 26):
            print(f"Hit stop date, don't go beyond.")
            loop = False
            break

        already_processed = True if current_date in processed else False
        if already_processed:
            print(f"Already processed {current_date}.")
            current_date -= datetime.timedelta(days=1) 
            continue

        current_date_age = (datetime.date.today() - current_date).days
        debates_processed = check_hansard_site('commons', current_date.isoformat())
        if debates_processed > 0 :
            # If there were debates to process, log the date as processed and stop.
            print(f"Processed {debates_processed} debates for {current_date}.")
            db.insertProcessedDate(current_date)
            loop = False
            break
        
        elif current_date_age > 3:
            print(f"No debates found for {current_date} and it was more that 3 days ago so we log it as processed.")
            db.insertProcessedDate(current_date)
            current_date -= datetime.timedelta(days=1)
            continue

        else:
            print(f"No debates found for {current_date} but it was less that 3 days ago so we don't log it as processed.")
            current_date -= datetime.timedelta(days=1)
            continue
    
    
    

# def process_mp_ids(queue):

# def process_topics(queue):

# def process_statement_vectors(queue):





p1 = Process1()
p2 = Process2()

schedule.every(3).seconds.do(p1.thread)
schedule.every(2).seconds.do(p2.thread)

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
        print("Running...")
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()