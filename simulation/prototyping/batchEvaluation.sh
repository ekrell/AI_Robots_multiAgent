#/bin/bash

START=4
END=15
for ((i=START;i<=END;i++)); do
	python3 predictPath.py -n susan,anton,django -w ../inData/round$i/ -p ../outData/round$i/ > ../outData/round$i/susanDjangoAnton_coverage__10m__5s.csv
	python3 predictPath.py -n susan,anton -w ../inData/round$i/ -p ../outData/round$i/ > ../outData/round$i/susanAnton_coverage__10m__5s.csv
	python3 predictPath.py -n susan,django -w ../inData/round$i/ -p ../outData/round$i/ > ../outData/round$i/susanDjango_coverage__10m__5s.csv
	python3 predictPath.py -n anton,django -w ../inData/round$i/ -p ../outData/round$i/ > ../outData/round$i/djangoAnton_coverage__10m__5s.csv
	python3 predictPath.py -d 1 -n susan,anton,django -w ../inData/round$i/ -p ../outData/round$i/ > ../outData/round$i/susanDjangoAnton_coverage__10m__5s.csv
	python3 predictPath.py -d 1 -n susan,anton -w ../inData/round$i/ -p ../outData/round$i/ > ../outData/round$i/susanAnton_coverage_NoWay__10m__5s.csv
	python3 predictPath.py -d 1 -n susan,django -w ../inData/round$i/ -p ../outData/round$i/ > ../outData/round$i/susanDjango_coverage_NoWay__10m__5s.csv
	python3 predictPath.py -d 1 -n anton,django -w ../inData/round$i/ -p ../outData/round$i/ > ../outData/round$i/djangoAnton_coverage_NoWay__10m__5s.csv
done

for ((i=START;i<=END;i++)); do
	python3 evaluate.py -n susan,anton,django -w ../inData/round$i/ -p ../outData/round$i/ -f ../outData/round$i/susanDjangoAnton_coverage__10m__5s.csv >> ../results/batch__10m__5s.csv
	python3 evaluate.py -n susan,anton -w ../inData/round$i/ -p ../outData/round$i/ -f ../outData/round$i/susanAnton_coverage__10m__5s.csv >> ../results/batch__10m__5s.csv
	python3 evaluate.py -n susan,django -w ../inData/round$i/ -p ../outData/round$i/ -f ../outData/round$i/susanDjango_coverage__10m__5s.csv >> ../results/batch__10m__5s.csv
	python3 evaluate.py -n anton,django -w ../inData/round$i/ -p ../outData/round$i/ -f ../outData/round$i/djangoAnton_coverage__10m__5s.csv >> ../results/batch__10m__5s.csv
	python3 evaluate.py -n susan,anton,django -w ../inData/round$i/ -p ../outData/round$i/ -f ../outData/round$i/susanDjangoAnton_coverage__10m__5s.csv >> ../results/batch__10m__5s.csv
	python3 evaluate.py -n susan,anton -w ../inData/round$i/ -p ../outData/round$i/ -f ../outData/round$i/susanAnton_coverage_NoWay__10m__5s.csv >> ../results/batch__10m__5s.csv
	python3 evaluate.py -n susan,django -w ../inData/round$i/ -p ../outData/round$i/ -f ../outData/round$i/susanDjango_coverage_NoWay__10m__5s.csv >> ../results/batch__10m__5s.csv
	python3 evaluate.py -n anton,django -w ../inData/round$i/ -p ../outData/round$i/ -f ../outData/round$i/djangoAnton_coverage_NoWay__10m__5s.csv >> ../results/batch__10m__5s.csv
###
done

for ((i=START;i<=END;i++)); do
	echo "$i,SAD,TRUE,50" >> ../results/info__10__5.csv
	echo "$i,SA,TRUE,50" >> ../results/info__10__5.csv
	echo "$i,SD,TRUE,50" >> ../results/info__10__5.csv
	echo "$i,AD,TRUE,50" >> ../results/info__10__5.csv
	echo "$i,SAD,FALSE,50" >> ../results/info__10__5.csv
	echo "$i,SA,FALSE,50" >> ../results/info__10__5.csv
	echo "$i,SD,FALSE,50" >> ../results/info__10__5.csv
	echo "$i,AD,FALSE,50" >> ../results/info__10__5.csv
done
