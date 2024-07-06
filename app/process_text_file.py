from db.db import Database
import os
import pprint

db = Database()

def process_text_file(file_path):

    statements_started = False
    previous_line = None
    tags = []
    statements = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            
            line = line.strip()
            
            if previous_line is None:
                previous_line = line
                continue

            if len(line) > 0 and len(previous_line) > 0:
                statements_started = True
                # previous_line is a person
                new_speaker = {"speaker": previous_line, "lines": []}
                statements.append(new_speaker)

            elif len(line) == 0 and len(previous_line) > 0: 
                if statements_started:
                    # previous_line is a comment
                    statements[-1]["lines"].append(previous_line)
                else:
                    # previous_line is a tag
                    tags.append(previous_line)
            
            previous_line = line

        # pprint.pprint(tags)
        # pprint.pprint(statements)

    result = {"tags": tags, "statements": statements}
    return result

if __name__ == '__main__':

    collection = 'commons' 
    date = '2024-04-30'
    title = 'Heathrow Airport_ Western Rail Link 2024-04-30.txt'
    file_path = os.path.join('docs', collection, date, title)
    
    doc_id = db.insertDocument(collection, date, title)
    
    # Process this text file. This populated tags and comments arrays.
    results = process_text_file(file_path)

    for i, statement in enumerate(results['statements']):
        speaker = statement['speaker']
        lines_joined = '\n'.join(statement['lines'])

        db.insertStatement(doc_id, i, speaker, lines_joined)
    
    for tag in results['tags']:
        db.insertTag(doc_id, tag)
