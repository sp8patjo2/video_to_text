#
#../yt-dlp --no-check-certificate -f bestaudio -x --audio-format mp3 --audio-quality 0 --add-metadata --embed-thumbnail -o "%(artist)s - %(title)s.%(ext)s" "$1"
#/usr/local/bin/yt-dlp --no-check-certificate -f bestaudio -x --audio-format mp3 --audio-quality 5 --add-metadata --embed-thumbnail -o "%(artist)s - %(title)s.%(ext)s" "$1"
#
/usr/local/bin/yt-dlp --no-check-certificate --skip-download --write-subs --write-auto-subs --sub-lang en --sub-format ttml --convert-subs srt --output "transcript.%(ext)s" $1
cat ./transcript.en.srt | sed '/^$/d' | grep -v '^[0-9]*$' | grep -v '\-->' | sed 's/<[^>]*>//g' | tr '\n' ' ' > output.txt
rm transcript.en.srt

echo "filen ligger i output.txt ... döp om den"
#

