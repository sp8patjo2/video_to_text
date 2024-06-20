import os
import sys
import re
import datetime
import autogen
from ai_utils.ai_utils import AIAutogenUtils
from openai import OpenAI
from moviepy.editor import VideoFileClip
from moviepy.editor import AudioFileClip  

# Initialize OpenAI client


#
openai_client     = None



# använder yt-dlp för att dra ner, kör något som:
# yt-dlp --no-check-certificate -f bestaudio -x --audio-format mp3 --audio-quality 5 --add-metadata --embed-thumbnail -o "%(artist)s - %(title)s.%(ext)s" "$1"
# drar ner kvaliteten för att hålla nere storleken på filen ... denna kombination verkar ok.
def main():
    global openai_client

    ai_autogen_utils = AIAutogenUtils()    
    ai_autogen_utils.set_config(api_key_env='OPENAI_API_KEY')  
    client = OpenAI(api_key=ai_autogen_utils.get_active_api_key())


    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input="""
Personerna som greps i Säkerhetspolisens räd har kopplingar till IS i Somalia. Det säger Fredrik Hallström, operativ chef på Säkerhetspolisen, till SVT.

– Jag utesluter inte att fler kan frihetsberövas, säger han.

Fyra personer sitter anhållna efter torsdagens tillslag mot en rad adresser i Stockholmsområdet. Brottsrubriceringen är förberedelse till terroristbrott och grovt vapenbrott.

– Vi har kunnat konstatera att det finns kopplingar till IS i Somalia, säger Fredrik Hallström, operativ chef på Säkerhetspolisen.
Säpoinsats i Tyresö efter misstänkta terrorplaner

    Efter Säpotillslaget – Sveriges muslimska förbund kan förlora statsbidrag
    polis med vapen
    Fyra gripna misstänkta för terrorbrott – det här vet vi

SVT har kunnat berätta att två av de gripna är män i 20-årsåldern som har dömts för brott upprepade gånger.
”Systematisk brottslighet”

Enligt SVT:s uppgifter ska båda männen regelbundet ha besökt en lokal som tillhör en islamisk förening. Föreningslokalen var en av de adresser som polisen slog till mot på torsdagen.

– Generellt ser vi att individer i den våldsbejakande extremistmiljön bedriver en form av systematisk brottslighet. Det kan vara för att finansiera sitt eget uppehälle eller för att finansiera terroristorganisationer utomlands. Vi ser också vissa kopplingar till organiserad brottslighet på individnivå, säger Fredrik Hallström.
Inte kopplat till andra tillslag

Tidigare i veckan greps flera personer i Belgien misstänkta för att ha förberett en terrorattack. Men enligt Fredrik Hallström har det inte någon koppling till gripandena i Sverige.

– Vi har haft en egen operation som inte är kopplad till några internationella tillslag, säger han.

Männens försvarare kan inte uttala sig om misstankarna på grund av yppandeförbud.

– Jag kan inte gå in på hans inställning, säger advokat Nils Svantemark.

        """
    )

    response.stream_to_file("output-svensk-alloy.mp3")


if __name__ == '__main__':
    main()
