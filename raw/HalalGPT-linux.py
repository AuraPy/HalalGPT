from openai import OpenAI # For GPT-3.5 Turbo access
from pathlib import Path # To get the path of the "speech.mp3" file in the right format
from pygame import mixer # Module of library (pygame) to play sound
import time # To put a sleep for the amount of time the audio is playing
import os # To remove the "speech.mp3" file to avoid a "access denied" error
from mutagen.mp3 import MP3 # To get the length of "speech.mp3"
from datetime import datetime # To get the current date and time
import requests # To call APIs
import json # To parse the JSON output APIs give
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import threading

class window(QWidget):
    def __init__(self, parent = None):
        super(window, self).__init__(parent)
        self.settings = QSettings("AuraPy", "HalalGPT")
        self.setWindowIcon(QIcon(f"{os.getcwd()}/logo.svg"))
        self.resize(500, 500)
        self.output = QTextBrowser()
        self.settingsbutton = QPushButton()
        self.layout = QVBoxLayout()
        self.HLayout = QHBoxLayout()
        self.layout.addWidget(self.settingsbutton)
        self.layout.addWidget(self.output)
        self.layout.addLayout(self.HLayout)
        self.msgbox = QTextEdit("Message HalalGPT...")
        self.send = QPushButton()
        self.HLayout.addWidget(self.msgbox)
        self.HLayout.addWidget(self.send)
        self.settingsbutton.setMaximumSize(50, 50)
        self.settingsbutton.setMinimumSize(50, 50)
        self.msgbox.setMaximumSize(500, 50)
        self.send.setMaximumSize(50, 50)
        self.send.setMinimumSize(50, 50)
        self.send.setIcon(QIcon(f'{os.getcwd()}/send.png'))
        self.send.setIconSize(QSize(40, 40))
        self.settingsbutton.setIcon(QIcon(f'{os.getcwd()}/settings.png'))
        self.settingsbutton.setIconSize(QSize(40, 40))
        self.output.setFrameShape(QFrame.NoFrame)
        self.theme()
        self.send.clicked.connect(self.GPT)
        self.settingsbutton.clicked.connect(self.settingsfunc)

        mixer.init() # Initialize the mixer
        self.responselist = list() # Create the self.responselist variable
        if self.settings.value("key"):
            self.client = OpenAI(api_key=self.settings.value("key")) # Set the openai client and set the token
        else:
            print("Reverted back to environment variable for API key, will throw error if not provided.")
            print("Linux version of HalalGPT does not support dotenv, please enter your API key in settings, close the app and open it again")

        # array of voices for HalalGPT
        self.voices = {
            "Male": "onyx",
            "Female": "shimmer"
        }

        # Functions that HalalGPT can call
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_namaz_time",
                    "description": "Get the timing for a specific namaz",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "The city, e.g. Manchester. Ask the user for this information if it is not specified in the prompt.",
                            },
                            "country": {
                                "type": "string",
                                "description": "The country, e.g. UK. Ask the user for this information if it is not specified in the prompt.",
                            },
                            "method": {
                                "type": "string",
                                "description": "The calculation method for the namaz timing, e.g. MWL.",
                            },
                            "namaz": {
                                "type": "string",
                                "description": "The prayer that the user needs the timing for. Ask the user for this information if it is not specified in the prompt.",
                            }
                        },
                        "required": ["city", "country", "method", "namaz"],
                    },
                }
            }
        ]

        self.font = QFont("Century Gothic")
        self.font.setBold(True)
        self.setFont(self.font)
        self.setLayout(self.layout)
        self.show()


    # Call the namaz timings API
    def namaz(self, country, city, method, namaz):
        data = requests.get(f"https://api.aladhan.com/v1/timingsByCity?city={city.lower()}&country={country}&method={method}").json()
        return data["data"]["timings"][namaz]
    
    def settingsfunc(self):
        self.dialog = settings()
        self.dialog.show()

    def restart():
        QApplication.closeAllWindows()
        QCoreApplication.quit()
        status = QProcess.startDetached(sys.executable, sys.argv)
        print(status)

    def theme(self):
        try:
            if self.settings.value("Theme") == "Dark":
                self.output.setStyleSheet("background: transparent; color: white; font-size: 15px")
                self.msgbox.setStyleSheet("border-width: 5px; border-radius: 10px; border-color: #11111a; padding: 5px; color: white; background-color: #1b1b29;")
                self.send.setStyleSheet("border-width: 5px; border-radius: 10px; border-color: #11111a; color: white; background-color: #1b1b29; padding: 0px;")
                self.settingsbutton.setStyleSheet("border-width: 5px; border-radius: 10px; border-color: #11111a; color: white; background-color: #1b1b29; padding: 0px;")
                self.setStyleSheet("background-color: #27273d;")
            elif self.settings.value("Theme") == "Light":
                self.output.setStyleSheet("background: transparent; color: black; font-size: 15px")
                self.msgbox.setStyleSheet("border-width: 5px; border-radius: 10px; border-color: #11111a; padding: 5px; color: black; background-color: #1b1b29;")
                self.send.setStyleSheet("border-width: 5px; border-radius: 10px; border-color: #11111a; color: black; background-color: #1b1b29; padding: 0px;")
                self.settingsbutton.setStyleSheet("border-width: 5px; border-radius: 10px; border-color: #11111a; color: black; background-color: #1b1b29; padding: 0px;")
                self.setStyleSheet("background-color: white;")
        except:
            self.output.setStyleSheet("background: transparent; color: white; font-size: 15px")
            self.msgbox.setStyleSheet("border-width: 5px; border-radius: 10px; border-color: #11111a; padding: 5px; color: white; background-color: #1b1b29;")
            self.send.setStyleSheet("border-width: 5px; border-radius: 10px; border-color: #11111a; color: white; background-color: #1b1b29; padding: 0px;")
            self.settingsbutton.setStyleSheet("border-width: 5px; border-radius: 10px; border-color: #11111a; color: white; background-color: #1b1b29; padding: 0px;")
            self.setStyleSheet("background-color: #27273d;")

    def GPT(self):
        self.output.setText("Thinking...")
        userinput = self.msgbox.toPlainText() # Get the user's input
        self.responselist.append("User: " + userinput + "\n") # Add the user's question, response or statement to self.responselist
        completion = self.client.chat.completions.create( # create the GPT-3.5 Turbo session
            model="gpt-3.5-turbo", # Pass the model ID
            messages=[ # Pass the system and user messages
                {"role": "system", "content": f"You are a very strong muslim called HalalGPT who makes islam his whole personality and helping people with islamic facts and wronging people about haram things in a funny way his main priority. Add in some jokes from famous sheiks here and there. Make SURE you WRITE OUT the islamic phrases IN THE ARABIC ALPHABET. When someone asks for your name, you say: 'Bismillah. In the name of allah, the most merciful, the entirely merciful. I am the defender of halal, HalalGPT!'. The current date and time is: {datetime.now()}. Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous. This is a list of some context of the previous converstaion: " + str(self.responselist)},
                {"role": "user", "content": userinput}

            ],
            tools=self.tools # Pass the functions that HalalGPT can call
        )

        tool_calls = completion.choices[0].message.tool_calls # Get the functions called from HalalGPT's response

        if tool_calls: # Check if any functions were called by HalalGPT

            for tool_call in tool_calls:
                function_args = json.loads(tool_call.function.arguments) # Parse the arguments of the function that HalalGPT picked up
                function_response = self.namaz( # Call the namaz timings API
                        country=function_args.get("country").capitalize(), # Pass the country
                        city=function_args.get("city").capitalize(), # Pass the city
                        method=function_args.get("method"), # Pass the namaz timing calculation method
                        namaz=function_args.get("namaz").capitalize() # Pass the namaz that the user wants the timings for
                )

            # This is to see what HalalGPT has put as the parameters for the namaz timing searches
            #print("\n\n" + str(completion.choices[0]))

            completion = self.client.chat.completions.create( # Create another GPT-3.5 Turbo session and add the namaz timing into the system message
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a very strong muslim called HalalGPT who makes islam his whole personality and helping people with islamic facts and wronging people about haram things in a funny way his main priority. Add in some jokes from famous sheiks here and there. Make SURE you WRITE OUT the islamic phrases IN THE ARABIC ALPHABET. When someone asks for your name, you say: 'Bismillah. In the name of allah, the most merciful, the entirely merciful. I am the defender of halal, HalalGPT!'. The current date and time is: {datetime.now()}. This is the time for {function_args.get('namaz').capitalize()}: {function_response} This is a list of some context of the previous converstaion: " + str(self.responselist)},
                {"role": "user", "content": f"When is {function_args.get('namaz').capitalize()}?"} # Pass a string which makes HalalGPT think that the user has just asked the question and has the information

            ]
        )
            
        print(str(completion.choices[0].message.content)) # print HalalGPT's reply
        self.responselist.append("You: " + str(completion.choices[0].message.content) + "\n") # Add HalalGPT's reply to self.responselist
        threading.Thread(target=self.say, args=(str(completion.choices[0].message.content), self.voices[self.settings.value("Voice")])).start()
        self.output.setText(str(completion.choices[0].message.content))

    def say(self, text, voice):
        speech_file_path = Path(__file__).parent / "speech.mp3" # Get the path of "speech.mp3" in the right format
        response = self.client.audio.speech.create( # Create a new TTS session
        model="tts-1", # Pass the model number
        voice=voice, # Pass the selected voice
        input=str(text) # Pass HalalGPT's reply
        )

        response.stream_to_file(speech_file_path) # Stream the audio to "speech.mp3"
        audio = MP3(f"{os.getcwd()}/speech.mp3") # Pass the path of "speech.mp3" through mutagen
        mixer.music.load(f"{os.getcwd()}/speech.mp3") # Pass the path of "speech.mp3" through pygame mixer
        mixer.music.play() # play "speech.mp3"
        time.sleep(audio.info.length) # sleep for however long "speech.mp3" is
        mixer.music.load(f"{os.getcwd()}/empty.mp3") # load a small beep sound into pygame mixer
        os.remove(f"{os.getcwd()}/speech.mp3") # Remove "speech.mp3" to avoid an "access denied" error

class settings(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.settings = QSettings("AuraPy", "HalalGPT")
        self.setStyleSheet("background-color: #27273d;")

        self.themelight = QPushButton("Light Mode")
        self.themedark = QPushButton("Dark Mode")
        self.voicemale = QPushButton("Male")
        self.voicefemale = QPushButton("Female")
        self.keysave = QPushButton("Set Key")
        self.key = QLineEdit()

        self.themelight.clicked.connect(self.lightmode)
        self.themedark.clicked.connect(self.darkmode)
        self.voicemale.clicked.connect(self.malevoice)
        self.voicefemale.clicked.connect(self.femalevoice)
        self.keysave.clicked.connect(self.setapikey)

        self.themelight.setStyleSheet("border-width: 5px; border-radius: 10px; border-color: #11111a; color: white; background-color: #1b1b29; padding: 0px;")
        self.themedark.setStyleSheet("border-width: 5px; border-radius: 10px; border-color: #11111a; color: white; background-color: #1b1b29; padding: 0px;")
        self.voicemale.setStyleSheet("border-width: 5px; border-radius: 10px; border-color: #11111a; color: white; background-color: #1b1b29; padding: 0px;")
        self.voicefemale.setStyleSheet("border-width: 5px; border-radius: 10px; border-color: #11111a; color: white; background-color: #1b1b29; padding: 0px;")
        self.keysave.setStyleSheet("border-width: 5px; border-radius: 10px; border-color: #11111a; color: white; background-color: #1b1b29; padding: 0px;")

        self.setStyleSheet("color: white; background-color: #27273d")

        self.themelight.setMaximumSize(70, 50)
        self.themelight.setMinimumSize(70, 50)
        self.themedark.setMaximumSize(70, 50)
        self.themedark.setMinimumSize(70, 50)
        self.voicemale.setMaximumSize(70, 50)
        self.voicemale.setMinimumSize(70, 50)
        self.voicefemale.setMaximumSize(70, 50)
        self.voicefemale.setMinimumSize(70, 50)
        self.keysave.setMaximumSize(70, 30)
        self.keysave.setMinimumSize(70, 30)

        self.titlethemes = QLabel("Themes")
        self.titlevoices = QLabel("AI Voices")
        self.titlekey = QLabel("OpenAI API Key")

        self.layout = QVBoxLayout()
        self.theme = QHBoxLayout()
        self.voices = QHBoxLayout()
        self.apikey = QHBoxLayout()
        self.theme.addWidget(self.themelight)
        self.theme.addWidget(self.themedark)
        self.voices.addWidget(self.voicemale)
        self.voices.addWidget(self.voicefemale)
        self.apikey.addWidget(self.key)
        self.apikey.addWidget(self.keysave)
        self.layout.addWidget(self.titlethemes)
        self.layout.addLayout(self.theme)
        self.layout.addWidget(self.titlevoices)
        self.layout.addLayout(self.voices)
        self.layout.addWidget(self.titlekey)
        self.layout.addLayout(self.apikey)
        self.setLayout(self.layout)

    def lightmode(self):
        self.settings.setValue("Theme", "Light")
        print(self.settings.value("Theme"))
        window.restart()
    def darkmode(self):
        self.settings.setValue("Theme", "Dark")
        print(self.settings.value("Theme"))
        window.restart()
    def malevoice(self):
        self.settings.setValue("Voice", "Male")
        self.hide()
    def femalevoice(self):
        self.settings.setValue("Voice", "Female")
        self.hide()
    def setapikey(self):
        self.settings.setValue("key", self.key.text())

def main():
    app = QApplication(sys.argv)
    ex = window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()