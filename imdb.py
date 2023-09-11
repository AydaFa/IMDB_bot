import requests
import telebot
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

API_TOKEN = 'your api token'
bot = telebot.TeleBot(API_TOKEN)

SELECT_MOVIE, SHOW_MOVIE = range(2)

def movie_search(update, context):
    search_phrase = update.message.text[0:]

    # log if it recieves messages
    logging.debug(f"Received message: '{update.message.text}'")


    response = requests.get(f'http://www.omdbapi.com/?apikey=37cc61e1&s={search_phrase}')

    if response.status_code == 200:
        movies = response.json().get('Search', [])

        if movies:
            movie_list = ''
            for m in movies:
                movie_list += f"{m['Title']}\n"
            update.message.reply_text(f"Here are the movies I found for '{search_phrase}':\n\n{movie_list}")

            update.message.reply_text("Now enter the title of the movie which you want to get more information about:")

            context.user_data['movies'] = movies
            return SELECT_MOVIE

        else:
            update.message.reply_text(f"Sorry, I couldn't find any movies for '{search_phrase}'.")
    else:
        update.message.reply_text("Sorry, there was an error while processing your request.")

        # Log the error
        logging.error(f"Failed to get movies for search phrase '{search_phrase}'. Response code: {response.status_code}")

        return ConversationHandler.END

def select_movie(update, context):
    chosen_movie = update.message.text[0:]
    movies = context.user_data['movies']

    for m in movies:
        if m['Title'] == chosen_movie:
            context.user_data['chosen_movie'] = m
            break
    
    chosen_movie = context.user_data['chosen_movie']
    imdb_id = chosen_movie['imdbID']

    response = requests.get(f'http://www.omdbapi.com/?apikey=37cc61e1&i={imdb_id}')
    if response.status_code == 200:
        movie_details = response.json()

        title = movie_details['Title']
        rating = movie_details['imdbRating']
        duration = movie_details['Runtime']
        year = movie_details['Released']
        genre = movie_details['Genre']
        storyline = movie_details['Plot']
        poster = movie_details['Poster']
        

    bot.send_photo(chat_id=update.effective_chat.id, photo=poster, caption=f"Title: {title}\n\nRating: {rating}\nDuration: {duration}\nRelease Date: {year}\n\nGenre: {genre}\n\nStory Line: {storyline}")

    update.message.reply_text("Type /start to search for another movie.")
    return ConversationHandler.END


def main():

    updater = Updater(API_TOKEN, use_context=True)

    # Create a conversation handler
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text & (~Filters.command), movie_search)],
        states={
            SELECT_MOVIE: [MessageHandler(Filters.text & (~Filters.command), select_movie)],
        },
        fallbacks=[],
    )
    updater.dispatcher.add_handler(CommandHandler('start', lambda update, context: update.message.reply_text('Hello! Send me a search phrase to get a list of movies.')))
    updater.dispatcher.add_handler(conv_handler)

    updater.start_polling()

    # Log that the bot has started
    logging.info('Bot has started!')

    updater.idle()

if __name__ == '__main__':
    main()
