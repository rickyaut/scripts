str="${*:1}" 
IFS=' '     # space is set as delimiter
read -ra youid <<< "$str"   # str is read into an array as tokens separated by IFS

for i in "${youid[@]}"; do   # access each element of array
  #Download best video (that also has audio) that is closest in size to 50 MB  
  #yt-dlp -f "b" -S "filesize~50M" $i
  # yt-dlp -f "b" -S "height:700" $1
  yt-dlp -f "ba" -x --audio-format mp3 $i
done
mv *.mp3 mp3

say Download finished
