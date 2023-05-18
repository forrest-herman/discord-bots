from firestore_methods import get_current_books_from_store, get_last_updated, convert_timestamp_to_datetime, set_firestore_document


def get_book_progress():
    # get the current book progress from gcloud firestore
    current_book_details = get_current_books_from_store()

    # get the last discord message timestamp from firestore
    last_message_date = get_last_updated('discord_readingUpdates')

    messages = []

    for _key, book_details in current_book_details.items():
        book_last_updated = convert_timestamp_to_datetime(book_details.get('last_updated'))
        # if book last updated is older than reading_last_message
        if (last_message_date and book_last_updated and
                book_last_updated < last_message_date):
            continue  # skip books that have not changed since last message

        progress = book_details['progress']

        if progress == 100:
            message = f"Forrest is finished {book_details['title']}"
        else:
            # post the current progress to the channel
            message = f"Forrest is currently {progress}% through {book_details['title']}"
        messages.append(message)
    return messages
