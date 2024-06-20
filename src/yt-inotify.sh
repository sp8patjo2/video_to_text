#!/bin/bash

cd mp3
TARGET_DIR="../ytlinks"

while inotifywait -e create,modify,attrib "$TARGET_DIR"; do
    echo "Directory updated. Running script..."
    for X in $TARGET_DIR/*txt ; do
	    /usr/local/bin/yt-dlp --no-check-certificate -f bestaudio -x --audio-format mp3 --audio-quality 5 --add-metadata --embed-thumbnail -o "%(artist)s - %(title)s.%(ext)s" "`cat $X`"
	    if [ $? != 0 ] ; then
		    echo "gick åt h-e skippar"
	    else
		    rm --verbose $X
		    echo "konverterar mp3 till text"
		    sleep 3
		    cd ..
		    python video_to_text.py # kör med default-värden
		    cd mp3
	    fi
    done
done
