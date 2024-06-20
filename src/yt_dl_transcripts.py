import argparse
from youtube_transcript_api import YouTubeTranscriptApi

def download_transcript(video_id, output_file):
    try:
        # Fetching the transcript.
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Combining the text into one long string.
        full_text = ' '.join([entry['text'] for entry in transcript])
        
        # Writing the transcript to a file.
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_text)
        print(f"Transcript has been saved to {output_file}")
        return output_file
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
        
        
        

def main():
    # Creating an ArgumentParser object
    parser = argparse.ArgumentParser(description="Download YouTube video transcripts and save to a file.")
    
    # Adding the --id and --output arguments
    parser.add_argument("--id", help="YouTube video ID", required=True)
    parser.add_argument("--output", help="Output file name", required=True)
    
    # Parsing command-line arguments
    args = parser.parse_args()
    
    # Calling the function to download transcript and save to file
    download_transcript(args.id, args.output)



if __name__ == "__main__":
    main()
