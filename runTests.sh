for seed in {4..25}
do
    for numIgnite in {50..100}
    do
	filePrefix="results/CA"$seed"-"$numIgnite
	python3 neuronTestNoRobot.py $seed 0 $numIgnite
	cp "CA.pkl" $filePrefix".pkl"
    done
    textOutName="results/total"$seed".txt"
    cp tempOut.txt $textOutName
    rm tempOut.txt
done



