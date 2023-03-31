
for i in snake_head snake_body snake_tail snake_bodyL; do
    convert "$i"W.png -rotate 90 "$i"D.png
    convert "$i"W.png -rotate 180 "$i"S.png
    convert "$i"W.png -rotate 270 "$i"A.png
done


