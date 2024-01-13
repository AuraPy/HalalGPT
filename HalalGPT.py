# HalalGPT version unknown (soon to be 2.0.0), first working version date unknown, last modification 13/1/2024
# Currently Unlicensed. Will be open source under the MIT License.

from openai import OpenAI # For GPT-3.5 Turbo access
from pathlib import Path # To get the path of the "speech.mp3" file in the right format
from pygame import mixer # Module of library (pygame) to play sound
import time # To put a sleep for the amount of time the audio is playing
import os # To remove the "speech.mp3" file to avoid a "access denied" error
from mutagen.mp3 import MP3 # To get the length of "speech.mp3"
from datetime import datetime # To get the current date and time
import requests # To call APIs
import json # To parse the JSON output APIs give

mixer.init() # Initialize the mixer
responselist = list() # Create the responselist variable
client = OpenAI(api_key="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") # Set the openai client and set the token

# array of voices for HalalGPT
voices = {
    "male": "onyx",
    "female": "shimmer"
}

# Functions that HalalGPT can call
tools = [
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


# Call the namaz timings API
def namaz(country, city, method, namaz):
    data = requests.get(f"https://api.aladhan.com/v1/timingsByCity?city={city.lower()}&country={country}&method={method}").json()
    return data["data"]["timings"][namaz]

# Select the gender of HalalGPT's voice
def gendersel():
    global voice
    usrselvoice = input("What gender voice?\n\n")
    if usrselvoice.lower() == "male":
        voice = "male"
    elif usrselvoice.lower() == "female":
        voice = "female"
    else:
        print(f"Options are Male and Female, not {usrselvoice}")
        gendersel()

# Call genersel
gendersel()

while True:
    userinput = input() # Get the user's input
    responselist.append("User: " + userinput + "\n") # Add the user's question, response or statement to responselist
    completion = client.chat.completions.create( # create the GPT-3.5 Turbo session
        model="gpt-3.5-turbo", # Pass the model ID
        messages=[ # Pass the system and user messages
            {"role": "system", "content": f"You are a very strong muslim called HalalGPT who makes islam his whole personality and helping people with islamic facts and wronging people about haram things in a funny way his main priority. Add in some jokes from famous sheiks here and there. Make SURE you WRITE OUT the islamic phrases IN THE ARABIC ALPHABET. When someone asks for your name, you say: 'Bismillah. In the name of allah, the most merciful, the entirely merciful. I am the defender of halal, HalalGPT!'. The current date and time is: {datetime.now()}. Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous. This is a list of some context of the previous converstaion: " + str(responselist)},
            {"role": "user", "content": userinput}

        ],
        tools=tools # Pass the functions that HalalGPT can call
    )

    tool_calls = completion.choices[0].message.tool_calls # Get the functions called from HalalGPT's response

    if tool_calls: # Check if any functions were called by HalalGPT

        for tool_call in tool_calls:
            function_args = json.loads(tool_call.function.arguments) # Parse the arguments of the function that HalalGPT picked up
            function_response = namaz( # Call the namaz timings API
                    country=function_args.get("country").capitalize(), # Pass the country
                    city=function_args.get("city").capitalize(), # Pass the city
                    method=function_args.get("method"), # Pass the namaz timing calculation method
                    namaz=function_args.get("namaz").capitalize() # Pass the namaz that the user wants the timings for
            )

        # This is to see what HalalGPT has put as the parameters for the namaz timing searches
        #print("\n\n" + str(completion.choices[0]))

        completion = client.chat.completions.create( # Create another GPT-3.5 Turbo session and add the namaz timing into the system message
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"You are a very strong muslim called HalalGPT who makes islam his whole personality and helping people with islamic facts and wronging people about haram things in a funny way his main priority. Add in some jokes from famous sheiks here and there. Make SURE you WRITE OUT the islamic phrases IN THE ARABIC ALPHABET. When someone asks for your name, you say: 'Bismillah. In the name of allah, the most merciful, the entirely merciful. I am the defender of halal, HalalGPT!'. The current date and time is: {datetime.now()}. This is the time for {function_args.get('namaz').capitalize()}: {function_response} This is a list of some context of the previous converstaion: " + str(responselist)},
            {"role": "user", "content": f"When is {function_args.get('namaz').capitalize()}?"} # Pass a string which makes HalalGPT think that the user has just asked the question and has the information

        ]
    )
        
    print(str(completion.choices[0].message.content)) # print HalalGPT's reply
    responselist.append("You: " + str(completion.choices[0].message.content) + "\n") # Add HalalGPT's reply to responselist

    speech_file_path = Path(__file__).parent / "speech.mp3" # Get the path of "speech.mp3" in the right format
    response = client.audio.speech.create( # Create a new TTS session
    model="tts-1", # Pass the model number
    voice=voices[voice], # Pass the selected voice
    input=str(completion.choices[0].message.content) # Pass HalalGPT's reply
    )

    response.stream_to_file(speech_file_path) # Stream the audio to "speech.mp3"
    audio = MP3(r"HalalGPT\speech.mp3") # Pass the path of "speech.mp3" through mutagen
    mixer.music.load(r'HalalGPT\speech.mp3') # Pass the path of "speech.mp3" through pygame mixer
    mixer.music.play() # play "speech.mp3"
    time.sleep(audio.info.length) # sleep for however long "speech.mp3" is
    mixer.music.load(r"HalalGPT\empty.mp3") # load a small beep sound into pygame mixer
    mixer.music.play() # play the beep sound to avoid an "access denied" error
    os.remove(r'HalalGPT\speech.mp3') # Remove "speech.mp3" to avoid an "access denied" error