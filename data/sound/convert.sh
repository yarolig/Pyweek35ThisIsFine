for i in *wav; do
    ii=${i%%.wav}
    #echo sox $i $ii.mp3
    sox $i $ii.ogg
done
