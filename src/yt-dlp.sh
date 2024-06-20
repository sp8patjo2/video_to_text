#
#../yt-dlp --no-check-certificate -f bestaudio -x --audio-format mp3 --audio-quality 0 --add-metadata --embed-thumbnail -o "%(artist)s - %(title)s.%(ext)s" "$1"
/usr/local/bin/yt-dlp --no-check-certificate -f bestaudio -x --audio-format mp3 --audio-quality 5 --add-metadata --embed-thumbnail -o "%(artist)s - %(title)s.%(ext)s" "$1"

