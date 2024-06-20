# echo kör något som
echo "kör något som (OBS ..p. kör en dry-run nedan - bara ett exempel ... enter för att fortsätta"
echo "rsync -vrHx --delete --size-only . /mnt/d/Min\ enhet/Mio/OpenAI/whisper_video_tts/."
read DUMMY
rsync -vrHxn --delete --size-only . /mnt/d/Min\ enhet/Mio/OpenAI/whisper_video_tts/.
echo
echo "det var alltså en dryrun ovan... "
