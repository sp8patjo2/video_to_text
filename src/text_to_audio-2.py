import os
import argparse
from openai import OpenAI
from ai_utils.ai_utils import AIAutogenUtils

# Funktion för att läsa text från en fil
def read_text_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

def split_text(text, max_length=4096):
    """Dela upp texten i segment av en maximal längd."""
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

def main():
    # Definiera en lista av tillåtna röster
    allowed_voices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']

    # Initialisera AI Autogen Utils
    ai_autogen_utils = AIAutogenUtils()    
    ai_autogen_utils.set_config(api_key_env='OPENAI_API_KEY')  
    client = OpenAI(api_key=ai_autogen_utils.get_active_api_key())

    # Konfigurera argparse för att ta emot --file och --voice argument
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', default='till_text.txt', help='Filnamnet för texten som ska omvandlas')
    parser.add_argument('--voice', default='onyx', help='Rösten som ska användas för text-till-tal')
    args = parser.parse_args()

    # Kontrollera att den angivna rösten är en av de tillåtna
    if args.voice not in allowed_voices:
        raise ValueError(f"Ogiltig röst '{args.voice}'. Tillåtna röster är: {', '.join(allowed_voices)}")

    # Läs in texten, rösten och modellen från argumenten
    text_file = args.file
    text_content = read_text_from_file(text_file)
    voice = args.voice
    model = "tts-1"  # Ange din modell här om du använder en annan

    # Dela upp texten i segment
    text_segments = split_text(text_content)

    # Processa varje textsegment
    for i, segment in enumerate(text_segments, start=1):
        # Bygg filnamnet med sekvensnummer, röst och modell
        output_file = f"{os.path.splitext(text_file)[0]}-{voice}-{model}-{i:03d}.mp3"
        
        # Kontrollera om filen redan finns
        if os.path.exists(output_file):
            print(f"File {output_file} already exists, skipping.")
            continue

        print(f"Processing text segment {i} of {len(text_segments)} with voice '{voice}' and model '{model}' - Length: {len(segment)} characters")

        # Skapa audio från segmentet
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=segment
        )
        
        # Streama resultatet till en fil
        response.stream_to_file(output_file)
        print(f"Generated audio segment saved to {output_file}")

if __name__ == '__main__':
    main()
