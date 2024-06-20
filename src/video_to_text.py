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


# Directory containing all the videos and audios
video_directory      = "videos"
transcript_directory = "transcripts"
audio_directory      = "mp3"        
summary_directory    = "summaries"

#
openai_client     = None
ai_autogen_utils  = None



def initialize_autogen(ai_autogen_utils):
    
    assistant = autogen.AssistantAgent(
        name="Copywriter",
        
        system_message="""    
        You are a copywriter and specialize in proof-reading video computer generated transcriptions.
        You check for grammar errors, sentence construction errors and syntactic errors and your most important job is to correct them.
        
        Once you are done you answer with the adjusted text.
        Then, as the last word on a line by itself you write the word "TERMINATE"
        """,

        llm_config=ai_autogen_utils.get_llm_config()
    )
    
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get("content","").find("TERMINATE") != -1,
        code_execution_config={
            "work_dir": "txt",
            "use_docker": False
        },
        llm_config=ai_autogen_utils.get_llm_config(),
        system_message="""    
        You send texts to a Copywriter. 
        When the Copywriter answers TERMINATE you will exit immediatly.
        """
    )

    ai_autogen_utils.set_agents(user_proxy,assistant)




def transcribe_audio(audio_filename, transcript_filename):
    print(f"Transcribing audio from {audio_filename}...")
    
    audio_clip = AudioFileClip(audio_filename)
    duration_minutes = audio_clip.duration / 60  # Convert seconds to minutes
    print(f"Audio duration: {duration_minutes:.2f} minutes")

    with open(audio_filename, "rb") as audio_file:
        transcript = openai_client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )

    if transcript is None or not hasattr(transcript, 'text'):
        raise Exception("Transcription failed")
    with open(transcript_filename, "w") as transcript_file:
        transcript_file.write(transcript.text)
        
    return transcript_filename


def transcribe_video(video_filename):
    base_name = os.path.splitext(video_filename)[0]
    audio_filename = base_name + ".mp3"
    transcript_filename = base_name + ".txt"
    audio_path = os.path.join(audio_directory, audio_filename)
    transcript_path = os.path.join(transcript_directory, transcript_filename)
    
    video_path = os.path.join(video_directory, video_filename)
    print(f"Converting {video_filename} to audio...")
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_path)
    transcribed_path = transcribe_audio(audio_path, transcript_path)
    return transcript_filename


def transcribe_videos_from_directory(directory):
    # Check and create directories if they don't exist
    for folder in [transcript_directory, audio_directory]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # List all MP4 videos
    videos = [f for f in os.listdir(directory) if f.endswith(".mp4")]
    total_videos = len(videos)

    # Iterate over all video files in the directory
    for index, filename in enumerate(videos, start=1):
        print(f"Working on video {index} of {total_videos}...")
        transcript_filename = os.path.splitext(filename)[0] + ".txt"
        transcript_path = os.path.join(transcript_directory, transcript_filename)
        if os.path.exists(transcript_path):
            print(f"Transcript for {filename} already exists. Skipping.")
            continue
        try:
            transcribed_file = transcribe_video(filename)
            print(f"Transcript for {filename} saved to {transcribed_file}.")
        except Exception as e:
            print(f"Failed to transcribe {filename}: {e}")
            sys.exit()


def sanitize_filename(filename, replacement_char='_'):
    """kör den på Linux - men eftersom jag använder den på windows så städa"""
    illegal_chars = '<>:"/\\|?*'
    illegal_chars += '' if os.name == 'posix' else '/'
    illegal_re = '[' + re.escape(illegal_chars) + ']'
    
    return re.sub(illegal_re, replacement_char, filename)


def transcribe_audio_from_directory(directory):
    transcript_directory = "transcripts"  # Assuming this is your intended directory

    # Check and create transcript directory if it doesn't exist
    if not os.path.exists(transcript_directory):
        os.makedirs(transcript_directory)

    # List all MP3 audios
    audios = [f for f in os.listdir(directory) if f.endswith(".mp3")]
    total_audios = len(audios)

    # Iterate over all audio files in the directory
    for index, filename in enumerate(audios, start=1):
        print(f"Working on audio {index} of {total_audios} - {filename}...")
        sanitized_basename = sanitize_filename(os.path.splitext(filename)[0])
        transcript_filename = sanitized_basename + ".txt"
        transcript_path = os.path.join(transcript_directory, transcript_filename)
        audio_path = os.path.join(directory, filename)

        if os.path.exists(transcript_path):
            print(f"Transcript for {filename} already exists. Skipping.")
            continue

        try:
            # Ensure the path for transcribe_audio is also sanitized
            sanitized_transcript_path = os.path.join(transcript_directory, transcript_filename)
            transcribed_path = transcribe_audio(audio_path, sanitized_transcript_path)
            print(f"Transcript for {filename} saved to {transcribed_path}.")
        except Exception as e:
            print(f"Failed to transcribe {filename}: {e}")
            sys.exit()

  
  
def ai_get_prompt_for_short_summary_of_transcription(text):
  if text is None:
    raise ValueError("Missing param")
  if len(text) < 100: # antagligen är något fel, om det strängen är kortare än 100 tecken
    raise ValueError(f"No use to summarize such a short text length - assume an erro, lenght is: {len(text)}")
  
  prompt = f"""
can you:

1. summerize
2. at the beginning make an even shorter (like a TDLR) in a a few bullet points.

the following text:

{text}
  """
  
  return prompt



def ai_get_prompt_for_correcting_and_formating_transcription(video_title, transcribed_text):
  #FIXME skicka in lite längdkontroller här sedan

  prompt = f"""
Kan du göra en analys av följande text.
Det är en transcribering och den är inte helt korrekt. Det är en människa som pratar korrekta meningar så kan du rätta upp och gissa vilka ord som är mest rimliga att personen har sagt.
Jag har originalet så du får ändra vad du vill.

Om det är till någon nytta så heter videon: {video_title}

här är texten
{transcribed_text}
  """

  return prompt



  

def autogen_long_summary(video_title, transcribed_text):
    
    prompt_task = ai_get_prompt_for_correcting_and_formating_transcription(video_title,transcribed_text)
    result_long = parse_return_ai_text(ai_autogen_utils.query_AI(prompt_task))
    if result_long is None:
      raise Exception("Fel vid försök att korrigera text med Autogen")
  
    prompt_task  = ai_get_prompt_for_short_summary_of_transcription(result_long)
    result_short = parse_return_ai_text(ai_autogen_utils.query_AI(prompt_task))
    
    result = f"""# <span style="color:#FFF000"><i>⏩⚡Den korta summeringen ⏩⚡</i></span>

{result_short}
    
# 📜☝️<span style="color:#FFF000"><i>Den långa summeringen</i></span>☝️📜

{result_long}
"""
    
    
    return result


def parse_return_ai_text(user_proxy__last_msg):
    if user_proxy__last_msg is None or 'content' not in user_proxy__last_msg:
        return None  # Return undefined value
      
    text_to_parse = user_proxy__last_msg['content']
    text_to_parse = re.sub(r'[\s\n]*TERMINATE[\s\n]*$', '', text_to_parse, flags=re.MULTILINE)
    return text_to_parse.replace("\\n","\n")
  

def generate_summaries_from_transcripts(directory):
    summary_directory = "summaries"  # Assuming this is your intended directory

    # Ensure the summary directory exists
    if not os.path.exists(summary_directory):
        os.makedirs(summary_directory)

    # List all text files in the transcript directory
    transcripts = [f for f in os.listdir(directory) if f.endswith(".txt")]
    total_transcripts = len(transcripts)

    # Iterate over all transcript files in the directory
    for index, filename in enumerate(transcripts, start=1):
        print(f"Working on summary {index} of {total_transcripts}...")
        sanitized_basename = sanitize_filename(os.path.splitext(filename)[0])
        summary_filename = sanitized_basename + ".md"
        summary_path = os.path.join(summary_directory, summary_filename)
        transcript_path = os.path.join(directory, filename)

        # Check if the summary already exists
        if os.path.exists(summary_path):
            print(f"Summary for {filename} already exists. Skipping.")
            continue

        # If the summary doesn't exist, read the transcript and generate a summary
        try:
            with open(transcript_path, "r") as transcript_file:
                transcribed_text = transcript_file.read()

            # Generate summary from the transcribed text
            summary_text = autogen_long_summary(sanitized_basename, transcribed_text)  # Assumed autogen_long_summary exists

            # Write the summary to a new file
            with open(summary_path, "w") as summary_file:
                summary_file.write(summary_text)

            print(f"Summary for {filename} saved to {summary_path}.")
        except Exception as e:
            print(f"Failed to generate summary for {filename}: {e}")
            sys.exit()

        # FIXME om det är jag lägg på frontmatter - lägger den för sig och återööpnar filen eftersom det enbart gäller för mig, sopa dessa innan publisering
        tags = ['todo', 'AI/Transcribe🤖']
        add_frontmatter(summary_path, tags)



def add_frontmatter(filename, tags):
    # Get the creation and modification times
    ctime = os.path.getctime(filename)
    mtime = os.path.getmtime(filename)
    created = datetime.datetime.fromtimestamp(ctime).strftime('%Y-%m-%d')
    a_modified = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')

    root, _ = os.path.splitext(filename)
    file_title = os.path.basename(root) 

    # Construct the frontmatter
    frontmatter = f"""---
title: {file_title}
created: {created}
a_modified: {a_modified}
tags:
  - {'\n  - '.join(tags)}
---

"""

    # Read the existing content of the file
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

    # Combine the frontmatter with the existing content
    new_content = frontmatter + content

    # Write the new content back to the file
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(new_content)



# använder yt-dlp för att dra ner, kör något som:
# yt-dlp --no-check-certificate -f bestaudio -x --audio-format mp3 --audio-quality 5 --add-metadata --embed-thumbnail -o "%(artist)s - %(title)s.%(ext)s" "$1"
# drar ner kvaliteten för att hålla nere storleken på filen ... denna kombination verkar ok.
def main():
    global openai_client
    global ai_autogen_utils
  
    ai_autogen_utils = AIAutogenUtils()    
    ai_autogen_utils.set_config(api_key_env='OPENAI_API_KEY_T',api_org_env='OPENAI_ORGID_T',model='gpt-4o')
    initialize_autogen(ai_autogen_utils)
    openai_client = OpenAI(api_key=ai_autogen_utils.get_active_api_key())
        
    
    # Transcribe videos from the video directory
    #transcribe_videos_from_directory(video_directory)
    # Transcribe audios from the audio directory
    transcribe_audio_from_directory(audio_directory)
    # Generate summaries
    generate_summaries_from_transcripts(transcript_directory)

if __name__ == '__main__':
    main()
