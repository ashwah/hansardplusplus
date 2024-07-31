from processes.process_base import ProcessBase
from db.db import Database
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import time
import datetime
import cloudscraper

class ProcessHansardData(ProcessBase):

    BASE_URL = 'https://hansard.parliament.uk'
    

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

            if current_date < datetime.date(2023, 11, 1):
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
            
            if debates_processed == -1 :
                # If the function returned -1 it means the site didn't respond with a 200 status code.
                # We leave the date as pending and try again in another process.
                print(f"Failed to obtain hansard page in {self.collection} for {current_date}. ")
                continue
            elif debates_processed > 0 :
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

        try:
            # Check that we get a 200 response from the site. If not retry, then give up.
            response = scraper.get(self.BASE_URL+ '/' + collection + '/' + date)
            if response.status_code != 200:
                time.sleep(10)
                response = scraper.get(self.BASE_URL+ '/' + collection + '/' + date)
                if response.status_code != 200:
                    return -1
        except:
            return -1

        html = response.text
        soup = BeautifulSoup(html, 'html.parser')


        # Target the div that contains the download links. We search for the div that contains
        # an h2 element with the text "Downloads".
        download_widget_divs = soup.select('div.widget:has(> * > h2:-soup-contains("Downloads"))')

        if not download_widget_divs:
            return 0

        # We assume the first item in download_divs is the one we want. Then we search for all 
        # the links in that div with the class 'dropdown-item'.
        # aggregate_page_links = [div.select('a.dropdown-item') for div in download_widget_divs[0]]
        aggregate_page_links = download_widget_divs[0].select('a.dropdown-item')



        
        
        # The "Card folder divs" are the top level containers for the individual debates.
        card_folder_divs = soup.select('div.widget > div.content > div.card-folder')

        # TODO aggregate_page_links and card_folder_divs should be the same length, if not throw an error.

        count = 0
        for i, card_folder_div in enumerate(card_folder_divs):
            debate_links = card_folder_div.find_all('a', class_='card-section')
            debate_ids = []
            agg_href = self.BASE_URL + aggregate_page_links[i].attrs['href']
            for debate_link in debate_links:
                href = self.BASE_URL + debate_link.attrs['href']
                title_div = debate_link.find('div', class_='primary-info')
                for span in title_div.find_all('span'):
                    span.decompose()
                title = title_div.get_text(strip=True)

                debate_id = self.db.insertDebate(processed_id, collection, date, title, href, agg_href, 'pending', datetime.datetime.now(), datetime.datetime.now())
                #debate_ids.append(debate_id)
                count += 1
            self.scrape_aggregate_page(agg_href, collection, date, processed_id)

            # Update 
            
        return count

    
    def scrape_aggregate_page(self, url, collection, date, processed_id):
        scraper = cloudscraper.create_scraper() 

        try:
            response = scraper.get(url)
            if response.status_code != 200:
                time.sleep(10)
                response = scraper.get(url)
                if response.status_code != 200:
                    time.sleep(15)
                    response = scraper.get(url)
                    if response.status_code != 200:
                        return
        except:
            return


        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        debate_list = soup.find('div', class_='child-debate-list')
        
        if not debate_list:
            return
        
        debate_items = debate_list.find_all('div', class_='child-debate')

        for i, debate_item in enumerate(debate_items):
            self.scrape_debate(debate_item, collection, date, url, processed_id)
            
    def scrape_debate(self, debate_item, collection, date, agg_href, processed_id):
        
        title_element = debate_item.find('h2')
        title = title_element.text.strip() if title_element else ''

        # Try to load the debate that matches the current title, date and colleciton. Due to a 
        # quirk on the aggregated pages, there may be things that look like debates but don't 
        # have a corresponding debate page in the menu page. In which case we need to create a
        # new debate.
        matching_debate_ids = self.db.getDebatesWithMatchingTitle(collection, date, title)

        if matching_debate_ids:
            debate_id = matching_debate_ids[0]
        else:
            debate_id = self.db.insertDebate(processed_id, collection, date, title, '', agg_href, 'pending', datetime.datetime.now(), datetime.datetime.now())

        # Find all the types of elements that we're interested in.
        debate_items = debate_item.select('div.debate-item-contributiondebateitem, div.debate-item-otherdebateitem, div.debate-item-columnnumber')

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
                if not content_paras:
                    content_paras = debate_item.find_all('p', class_='hs_para')
                if not content_paras:
                    content_paras = debate_item.find_all('questiontext')


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

 