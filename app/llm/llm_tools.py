from db.db import Database

def get_full_debate(debate_id):

    # Set debate string to empty.
    full_debate = ''

    db = Database()

    # Get the debate from the database and get the date and title.
    debate = db.getDebateFromId(debate_id)
    debate_date = debate[3].strftime('%Y-%m-%d')
    debate_title = debate[4]

    # Add the debate title and date to the full debate string.
    full_debate += f"{debate_title} - {debate_date}\n\n"

    # Get the statements and anon statements from the database.
    statements = db.getStatementsFromDebate(debate_id)
    statements_anon = db.getStatementsAnonFromDebate(debate_id)
    
    # Merge and sort arrays based on the index values
    merged = statements + statements_anon
    merged.sort(key=lambda x: x[0])

    for statement in merged:
        # Get the length of the statement array.
        statement_length = len(statement)
        # Switch case for the length of the statement array.
        if statement_length == 3:
            # If the length is 3, add the speaker to the full debate string.
            full_debate += f"{statement[1]}:\n" 
            full_debate += f"{statement[2]}\n\n" 

        elif statement_length == 2:
            # If the length is 2, then the statement is anonymous.
            full_debate += f"[{statement[1]}]\n\n" 
    return full_debate