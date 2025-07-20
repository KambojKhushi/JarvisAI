import speech_recognition as sr
import pyttsx3
import os
import webbrowser
import datetime
from ollama import Client
import cv2

# Initialize Ollama + Voice
client = Client()  # connects to Ollama running in the background
engine = pyttsx3.init()

# Sites list
sites = [
    ["youtube", "https://www.youtube.com"],
    ["google", "https://www.google.com"],
    ["wikipedia", "https://www.wikipedia.com"]
]


def say(text):
    engine.say(text)
    #now this runs first by making other code stop
    engine.runAndWait()


def takeCommand():
    #recognize our content
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.pause_threshold = 1  # wait for 1 sec when we finish speaking
        audio = recognizer.listen(source)
        try:
            query = recognizer.recognize_google(audio, language='en-in')
            print(f"User said: {query}")
            return query
        except:
            say("Sorry, I didn't catch that.")
            return ""


#Sets the behavior of the assistant: stay short, helpful, and only act like Jarvis.
chat_history = [
    {"role": "system",
     "content": "You are Jarvis, a helpful, concise assistant. Keep replies short and never pretend to be the user."}
]


def chat(query):
    chat_history.append({"role": "user", "content": query})

    #Sends the full conversation to the tinyllama model via Ollama.
    response = client.chat(model='tinyllama', messages=chat_history)
    reply = response['message']['content'].strip()

    # Clean and shorten
    reply = reply.split("User:")[0].strip()  #gives only jarvis reply not user

    if len(reply.split()) > 30:  #counts how many words in the reply
        reply = ' '.join(reply.split()[:30]) + "..."  #select only first 30 words

    print("Jarvis:", reply)
    say(reply)

    chat_history.append({"role": "assistant", "content": reply})


if __name__ == '__main__':
    print("Jarvis Running...")
    say("Hello Khushi, I am your JarvisAI.")

    while True:
        query = takeCommand()
        #if not said anything keep listening
        if not query:
            continue

        query_lower = query.lower()

        # Check in sites list
        opened = False
        for site in sites:
            if f"open {site[0]}" in query_lower:
                say(f"Opening {site[0]}...")
                webbrowser.open(site[1])
                opened = True
                break
        if opened:
            continue

        # Play music
        if "open music" in query_lower:
            musicPath = "C:\\Users\\khush\\Downloads\\Hass Hass Diljit Dosanjh 128 Kbps.mp3"
            try:
                os.startfile(musicPath)
                say("Playing your song.")
            except:
                say("Sorry, I couldn't find your music file.")


        elif "play players" in query_lower:
            vcPath = "C:\\Users\\khush\\Downloads\\Players - Badshah Ft Karan Aujla_HD-(Hd9video).mp4"
            try:
                os.startfile(vcPath)
                say("Playing your song.")
            except:
                say("Sorry, I couldn't find your video file.")

        elif "open camera" in query_lower:
            say("Opening camera")
            cap = cv2.VideoCapture(0)  #opening default camera laptop webcam
            if not cap.isOpened():
                say("Sorry, I couldn't access the camera.")
                continue

            #reads frame from cam
            while True:
                ret, frame = cap.read()  #bool=r(true)
                if not ret:
                    say("Failed to grab frame.")
                    break
                cv2.imshow("Camera", frame)  #titleframe

                # Press 'q' to quit the camera window
                if cv2.waitKey(1) & 0xFF == ord(
                        'q'):  #gives the ascii code of the key pressedwaitkey and only compare last 8 bit
                    break

            cap.release()
            cv2.destroyAllWindows()
            say("Camera closed.")


        # Time
        elif "the time" in query_lower:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")  #convert into string format
            say(f"The time is {strTime}")

        # Exit
        elif "jarvis quit" in query_lower or "exit" in query_lower:
            say("Goodbye Khushi")
            break

        # Chat
        else:
            chat(query)
