for i in {1..50}
do
  ./good_client localhost:3434 ./Files/enum.txt "enum${i}.txt" &
  echo "Number: $i" >> enum.txt
done
