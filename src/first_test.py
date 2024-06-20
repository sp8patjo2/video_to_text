from openai import OpenAI
from moviepy.editor import VideoFileClip

client = OpenAI(api_key="sk-notakey")
#video = VideoFileClip("video.mp4")
#audio = video.audio
#audio.write_audiofile('output_audio.mp3')


audio_file= open("output_audio-2.mp3", "rb")
transcript = client.audio.transcriptions.create(
  model="whisper-1", 
  file=audio_file
)

print(transcript.text)
