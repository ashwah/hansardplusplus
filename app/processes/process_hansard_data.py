from processes.process_base import ProcessBase
from db.db import Database
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import time
import datetime
import cloudscraper

class ProcessHansardData(ProcessBase):

    BASE_URL = 'https://hansard.parliament.uk/'
    

    def __init__(self, collection):
        super().__init__() 
        self.collection = collection


    def process(self):

        self.db = Database()

        print("Checking Hansard site...")
            
        # Start from yesterday
        current_date = datetime.date.today() - datetime.timedelta(days=1) 

        processed = self.db.getProcessedDateList(self.collection)

        loop = True
        while loop:

            # Set the URL for this collection and date.
            url = self.BASE_URL + self.collection + '/' + current_date.isoformat()

            if current_date < datetime.date(2023, 11, 26):
                print(f"Hit stop date, don't go beyond.")
                loop = False
                continue

            already_processed = True if current_date in processed else False
            if already_processed:
                print(f"Already processed {current_date}.")
                current_date -= datetime.timedelta(days=1) 
                continue

            current_date_age = (datetime.date.today() - current_date).days
            
            # See if the current date has a log entry.
            processed_id = self.db.getProcessedDate(self.collection, current_date.isoformat())
            if processed_id:
                self.db.updateProcessed(processed_id, processed_state="pending", updated=datetime.datetime.now())
            else:
                # Log the date as pending.
                processed_id = self.db.insertProcessed(current_date, url, self.collection, "pending", 0, datetime.datetime.now(), datetime.datetime.now())
            
            # Check the Hansard site for debates on the current date.
            debates_processed = self.check_hansard_site(self.collection, current_date.isoformat(), processed_id)
            if debates_processed > 0 :
                # If there were debates to process, log the date as processed and stop.
                print(f"Processed {debates_processed} debates in {self.collection} for {current_date}.")
                self.db.updateProcessed(processed_id, processed_state="completed", updated=datetime.datetime.now(), processed_count=debates_processed)
                loop = False
                continue
            
            elif current_date_age > 3:
                print(f"No debates found in {self.collection} for {current_date} and it was more that 3 days ago so we log it as 'no_debates'.")
                self.db.updateProcessed(processed_id, processed_state="no_debates", updated=datetime.datetime.now())
                current_date -= datetime.timedelta(days=1)
                continue

            else:
                print(f"No debates found in {self.collection} for {current_date} but it was less that 3 days ago so we log it as 'unready'.")
                self.db.updateProcessed(processed_id, processed_state="unready", updated=datetime.datetime.now())
                current_date -= datetime.timedelta(days=1)
                continue

    def check_hansard_site(self, collection, date, processed_id):
        scraper = cloudscraper.create_scraper() 

        html = scraper.get(self.BASE_URL + collection + '/' + date).text
        
        soup = BeautifulSoup(html, 'html.parser')

        a_tags = soup.find_all('a', class_='card-section')
        count = 0
        for a_tag in a_tags:
            count += 1
            href = a_tag.get('href')
            if href and href!= '#' and not href.startswith('#'):
                # Log the debate in the database with a status of 'pending'.
                debate_id = self.db.insertDebate(processed_id, collection, date, '', href, 'pending', datetime.datetime.now(), datetime.datetime.now())

                # Wait five seconds before scraping the page so CF doesn't get spooked.
                time.sleep(5)   


                print(f"Debate URL: {href}")

                # Scrape the debate.
                self.scrape_debate(href, collection, date, debate_id)

        return count
    
    def scrape_debate(self, url, collection, date, debate_id):
        scraper = cloudscraper.create_scraper() 
        response = scraper.get(self.BASE_URL + url)

        try:
            if response.status_code != 200:
                time.sleep(10)
                response = scraper.get(self.BASE_URL + url)
                if response.status_code != 200:
                    time.sleep(15)
                    response = scraper.get(self.BASE_URL + url)
                    if response.status_code != 200:
                        return
        except:
            return


        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        debate_container = soup.find('div', class_='hero-banner-debate')
        
        if not debate_container:
            return
        
        title_element = debate_container.find('h1')
        subtitle_element = debate_container.find('h2')

        title = title_element.text.strip() if title_element else ''
        subtitle = subtitle_element.text.strip() if subtitle_element else ''
        title_combined = title + '\n' + subtitle
        title_combined = title_combined.strip()

        # Update the debate with the title.
        self.db.updateDebate(debate_id, debate_title=title_combined)

        # Find all the types of elements that we're interested in.
        debate_items = soup.select('div.debate-item-contributiondebateitem, div.debate-item-otherdebateitem, div.debate-item-columnnumber')

        for i, debate_item in enumerate(debate_items):

            # If the debate item is a contribution.
            if 'debate-item-contributiondebateitem' in debate_item.attrs['class']:
                # Get the primary and secondary names.
                primary_element = debate_item.find('div', class_='primary-text')
                secondary_element = debate_item.find('div', class_='secondary-text')
                
                primary = primary_element.text.strip() if primary_element else ''
                secondary = secondary_element.text.strip() if secondary_element else ''
                
                speaker = primary + ' ' + secondary
                speaker = speaker.strip()

                speaker_link = debate_item.find('a', class_='attributed-to-details')

                if (speaker_link):
                    href = speaker_link.get('href')
                    speaker_id = int(parse_qs(urlparse(href).query).get('memberId')[0])
                else:
                    speaker_id = 0

                content_paras = debate_item.find_all('p', class_='hs_Para')

                if speaker and content_paras:
                    print('Speaker: ' + speaker)
                    print('')
                    
                    statement = ''
                    for content_para in content_paras:
                        content_para_text = content_para.text.strip()
                        if content_para_text:
                            statement += content_para_text + '\n\n'
                            print(content_para_text)
                    print('')

                    self.db.insertStatement(debate_id, i, speaker, statement, speaker_id)

            # If the debate item is an anon statement.
            if 'debate-item-otherdebateitem' in debate_item.attrs['class']:
                anon_statement_paragraph = debate_item.find('p')
                if anon_statement_paragraph:
                    print('Anon: ' + anon_statement_paragraph.text.strip())
                    self.db.insertStatementAnon(debate_id, i, anon_statement_paragraph.text.strip())
        
        self.db.updateDebate(debate_id, debate_state="completed", updated=datetime.datetime.now())