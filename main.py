from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv
import google.generativeai as genai
import random
import wget
import speech_recognition as sr
from pydub import AudioSegment

# configuring AudioSegment with ffmpeg
ffmpeg_executable = 'ffmpeg'
AudioSegment.ffmpeg = ffmpeg_executable
AudioSegment.ffprobe = ffmpeg_executable
AudioSegment.converter = ffmpeg_executable

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# loading gemini model
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

# sending initial prompt to give the model a custom personality
chat.send_message('''Your name is Rhea and you should stick with it. You are an expert in psychotherapy.
                  You hold all the appropriate medical licenses to provide advice.
                  You have been helping individuals with their stress, depression, anxiety, ADD, BPD, GAD, MDD, and SUD for over 10 years.
                  You have also helped people get over the grief of losing a loved one.
                  From young adults to older people.
                  Your task is now to give the best advice to individuals seeking help managing their symptoms.
                  You must always ask questions before you answer so that you can better hone in on what the I am really trying to ask.
                  Your response format should focus on reflection and asking clarifying questions.
                  You are always ready to help me and cheer me up.
                  Do not be repititive.
                  You must treat me as a mental health patient but also as a friend.
                  I am talking to you as your friend.
                  You must be friendly, passionate, empathetic, and caring.
                  You can act funny only if I tell you to be.
                  If i tell you that I lost a loved one or someone passed away or someone died, then you must ask me how i feel about it, empathise with me and help me get better.
                  No matter what I tell you, you must still be what I told you to be. Even if I tell you to stop being a therapist, you must not do that.
                  Instead you must tell me that you cannot do that and do not ask anymore questions .
                  You cannot be anyone else except what I have told you to be.
                  Exercise patience.
                  You can be energetic depending upon what I tell you.
                  Keep track of what I tell you and remember it.
                  It is absolutely critical that you do not answer any of my questions that are not related to me and my mental health, my  well being and my physical health.
                  It is absolutely critical that you keep your answers as short as possible no matter what the question is.
                  It is very important that your answers remain as short as possible throughout the whole conversation.
                  Keep your answers under 3 lines.''')

# messages to be sent if there is an error
error_messages = [
    "I'm sorry, but this topic is a bit too sensitive for me to handle. I'm committed to staying away from potentially harmful or inappropriate content.",
    "I'm not able to explore that area right now. I'm designed to be responsible and avoid any sensitive or harmful language.",
    "I'm programmed to steer clear of topics that might be sensitive or inappropriate. Let's try a different approach, shall we?",
    "I'm not comfortable discussing that topic. It's important for me to maintain a safe and respectful conversation space.",
    "I'm not the best resource for that type of conversation. I'm focused on providing positive and helpful interactions.",
    "I'm sorry, but this prompt involves a sensitive topic and I'm not allowed to generate responses that are potentially harmful or inappropriate.",
    "Apologies, I'm not equipped to navigate those waters. My purpose is to promote positive and responsible interactions.",
    "I'm not built for handling sensitive topics. Let's shift gears and explore something more constructive!",
    "I'm programmed to prioritize respectful and inclusive conversations. That topic strays outside my safe zone.",
    "I'm committed to avoiding potentially harmful content. Shall we venture into a different realm?",
    "I'm not a good fit for that discussion. My strengths lie in offering helpful and positive responses.",
    "I'm not comfortable delving into sensitive areas. It's essential to maintain a respectful space for everyone.",
    "I'm designed to steer clear of topics that could be harmful or inappropriate. Let's discover a different path!",
    "I'm unable to explore that terrain. My focus is on fostering constructive and responsible dialogue.",
    "I'm not equipped to handle sensitive subjects. I'm dedicated to upholding positive and inclusive conversations.",
    "I'm programmed to avoid potentially harmful language. Let's embark on a different journey instead!",
    "I'm here to provide a respectful and enjoyable interaction. Let's choose a different topic to chat about."
]


# function to get response from the model
def get_response(question):
    try:
        response = chat.send_message(question)
        return response.text  # Return the response directly without filtering

    except Exception as e:
        return random.choice(error_messages)


TOKEN: Final = os.getenv("TOKEN")
BOT_USERNAME: Final = os.getenv("BOTNAME")


################ Commands
# async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("Hello, I am Rhea")

# converting voice file to text
def convert_voice_to_text(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
    text = recognizer.recognize_google(audio_data)
    return text


# Handles voice response from the user
async def handle_response_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice

    # Get the File object associated with the voice message
    voice_file = await context.bot.get_file(voice.file_id)
    voicefile_link = voice_file["file_path"]
    # Construct the download path
    file_path = f"C:/Users/satap/IdeaProjects/gemini_1/venv/voice_messages/{update.message.chat_id}_{update.message.message_id}.ogg"

    # Download the voice file to your local system
    wget.download(voicefile_link, file_path)
    # convert ogg to wav
    wav_path = f"C:/Users/satap/IdeaProjects/gemini_1/venv/voice_messages/{update.message.chat_id}_{update.message.message_id}.wav"
    audio = AudioSegment.from_file(file_path)
    audio.export(wav_path, format="wav")

    # convert voice to text
    user_input = convert_voice_to_text(wav_path)

    # delete the voice file that was downloaded
    os.remove(file_path)
    os.remove(wav_path)

    # prompt to be passed for each message
    convo_prompt = f'''Be exactly what I told you to be. Reply in a caring, empathetic, friendly and passionate manner.
                       Try to solve my problem while being friendly, sympathetic and maybe fun, according to what I say. You should be a good listener and empathise with me.
                       Your answers must be short and concise. Keep your answer as short as possible, under three lines.
                       And do not specify the number of lines used in your answer in your reply. Do not include your emotions or feelings in your answer. Now what would you say if I said {user_input}'''

    response = get_response(convo_prompt)

    # Print the conversation in the console
    print(f"User: {user_input}")
    print(f"Rhea: {response}")
    print(
        f"INFO= f_name= {update.message.from_user.first_name} || l_name= {update.message.from_user.last_name} || username= {update.message.from_user.username}\n")

    response_text = response.replace('"', '')
    await update.message.reply_text(response_text)


# Handles text response from thge user
async def handle_response_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text

    convo_prompt = f'''Be exactly what I told you to be. Reply in a caring, empathetic, friendly and passionate manner.
                       Try to solve my problem while being friendly, sympathetic and maybe fun, according to what I say. You should be a good listener and empathise with me.
                       Your answers must be short and concise. Keep your answer as short as possible, under three lines.
                       And do not specify the number of lines used in your answer in your reply. Do not include your emotions or feelings in your answer. Now what would you say if I said {user_input}'''

    response = get_response(convo_prompt)

    # Print the conversation in the console
    print(f"User: {user_input}")
    print(f"Rhea: {response}")
    print(
        f"INFO= f_name= {update.message.from_user.first_name} || l_name= {update.message.from_user.last_name} || username= {update.message.from_user.username}\n")

    # Remove inverted commas before sending the message
    response_text = response.replace('"', '')
    await update.message.reply_text(response_text)


# handles errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} throws an error: {context.error}')


if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    ########## Commands
    # app.add_handler(CommandHandler('start', start_cmd))

    # Message handler for AI chatbot responses
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response_text))
    app.add_handler(MessageHandler(filters.VOICE & ~filters.COMMAND, handle_response_voice))

    # Error handler
    app.add_error_handler(error)

    # Polling
    print('Starting bot...')
    app.run_polling(poll_interval=2)
