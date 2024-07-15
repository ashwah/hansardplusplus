from threading import Thread
from processes.check_hansard_site import check_hansard_site
from db.db import Database
import schedule
import time
import datetime

db = Database()

def process_check_hansard_site():
    print("Checking Hansard site...")
    # Start from yesterday
    current_date = datetime.date.today() - datetime.timedelta(days=1) 
    processed = db.getProcessedDates()

    while True:
        already_processed = True if current_date in processed else False

        if current_date < datetime.date(2023, 11, 26):
            print(f"Hit stop date, don't go beyond.")
            break

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
    
    
    

# def process_topics(queue):
#     # Process topics data from data
#     response = requests.get(HANSARD_URL)
#     data = response.json()
#     queue.put(data)


# Main script
if __name__ == "__main__":

    # Create threads for each process
    download_thread = Thread(target=process_check_hansard_site)

    # Start threads
    download_thread.start()

    # Run script indefinitely
    while True:
        # Check for new data every hour
        schedule.every(5).minutes.do(process_check_hansard_site)
        schedule.run_pending()
        time.sleep(1)