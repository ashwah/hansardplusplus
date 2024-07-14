from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from db.db import Database

import time
import cloudscraper

BASE_URL = 'https://hansard.parliament.uk/'

db = Database()

def check_hansard_site(collection, date):

    scraper = cloudscraper.create_scraper() 

    html = scraper.get(BASE_URL + collection + '/' + date).text
    
    soup = BeautifulSoup(html, 'html.parser')

    content_elements = soup.find_all('div', class_='contents')
    count = 0
    for content_element in content_elements:
        a_tags = content_element.find_all('a')
        for a_tag in a_tags:
            count += 1
            href = a_tag.get('href')
            if href and href!= '#' and not href.startswith('#'):
                # Wait five seconds before scraping the page so we don't get blocked.
                time.sleep(5)   
                print(f"Debate URL: {href}")
                scrape_debate(href, collection, date)
    return count
    

def scrape_debate(url, collection, date):
    scraper = cloudscraper.create_scraper() 
    html = scraper.get(BASE_URL + url).text
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

    # Create a document in the database.
    doc_id = db.insertDebate(collection, date, title_combined)

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
            
            name = primary + ' ' + secondary
            name = name.strip()

            content_paras = debate_item.find_all('p', class_='hs_Para')

            if name and content_paras:
                print('Name: ' + name)
                print('')
                
                statement = ''
                for content_para in content_paras:
                    content_para_text = content_para.text.strip()
                    if content_para_text:
                        statement += content_para_text + '\n\n'
                        print(content_para_text)
                print('')

                db.insertStatement(doc_id, i, name, statement)

        # If the debate item is an anon statement.
        if 'debate-item-otherdebateitem' in debate_item.attrs['class']:
            anon_statement_paragraph = debate_item.find('p')
            if anon_statement_paragraph:
                print('Anon: ' + anon_statement_paragraph.text.strip())
                db.insertStatementAnon(doc_id, i, anon_statement_paragraph.text.strip())
