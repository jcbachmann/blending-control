while true; do
A=$RANDOM
for i in {3..8}; do echo $[$i]00 $[$i]00; sleep 0.$RANDOM; done
A=$RANDOM
for i in {3..8}; do echo $[10-$i]00 $[10-$i]00; sleep 0.$RANDOM; done
done
