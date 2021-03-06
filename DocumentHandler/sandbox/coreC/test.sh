#!/bin/bash

TIME=0
SUM=0
AVG=0
STD=0

N=1 #NUMBER OF ITERATIONS

declare -A DATAFILE
DATAFILE["small"]="smb/small.txt"
DATAFILE["medium"]="smb/medium.txt"
DATAFILE["big"]="smb/big.txt"

make

standard_deviation(){

	TIMES=$1
	AVG=$2
	local N=$3

	if (($N == 1 )) ; then
		#There's no standard deviation
		echo 0
	elif (($N > 1 )) ; then		
		SUM=0
		STD=0

		for((i = 0; i < $N; i++))
		do	
			SUM=$(/usr/bin/awk "BEGIN{print (${TIMES[$i]}-$AVG)^2}")
			#SUM=$(/usr/bin/awk "BEGIN{print (${TIMES[$i]}-$AVG)**2}")
		done

		SUM=$(/usr/bin/awk "BEGIN{print $SUM/$N}")	
		STD=$(/usr/bin/awk "BEGIN{print sqrt($SUM 2)}")

		#Default computation
		echo $STD
	else
		#Error
		echo -1	
	fi

	
}


run_test(){
	
	DATAFILE_S=$1
	DATAFILE_T=$2
	STR_CHARACTERIZATION=$3

	echo "\n===========$STR_CHARACTERIZATION==========="
	echo "\nFile name (s): $DATAFILE_S"
	echo "\nFile name (t): $DATAFILE_T"

	echo "\n\n=-=-=-=-=-=-=-=-Sequential-=-=-=-=-=-=-=-="

	SUM=0
	for((i = 0; i < $N; i++))
	do	
		TIME=`./sequential_levenshtein -s $DATAFILE_S -t $DATAFILE_T`
		TIMES[i]=$TIME
		SUM=$(/usr/bin/awk "BEGIN{print $SUM+$TIME}") 
	done

	AVG=$(/usr/bin/awk "BEGIN{print $SUM/$N}")
	STD=$(standard_deviation $TIMES $AVG $N)
	echo "\nAverage:  $AVG"
	echo "\nStandard deviation: $STD"

	echo "\n=-=-=-=-=-=-=-=-Parallel-=-=-=-=-=-=-=-="

	SUM=0
	for((i = 0; i < $N; i++))
	do	
		TIME=`./parallel_levenshtein -s $DATAFILE_S -t $DATAFILE_T`
		TIMES[i]=$TIME
		SUM=$(/usr/bin/awk "BEGIN{print $SUM+$TIME}") 
	done

	AVG=$(/usr/bin/awk "BEGIN{print $SUM/$N}")
	STD=$(standard_deviation $TIMES $AVG $N)
	echo "\nAverage:  $AVG"
	echo "\nStandard deviation: $STD"
}



#====================================SMALL FILE WITH SMALL FILE======================================
DATAFILE_S=${DATAFILE["small"]}
DATAFILE_T=${DATAFILE["small"]}
STR_CHARACTERIZATION="SMALL_FILE_WITH_SMALL_FILE"
echo -e $(run_test $DATAFILE_S $DATAFILE_T $STR_CHARACTERIZATION)
#====================================================================================================

#====================================MEDIUM FILE WITH MEDIUM FILE====================================
DATAFILE_S=${DATAFILE["medium"]}
DATAFILE_T=${DATAFILE["medium"]}
STR_CHARACTERIZATION="MEDIUM_FILE_WITH_MEDIUM_FILE"
echo -e $(run_test $DATAFILE_S $DATAFILE_T $STR_CHARACTERIZATION)
#====================================================================================================

#====================================BIG FILE WITH BIG FILE==========================================
DATAFILE_S=${DATAFILE["big"]}
DATAFILE_T=${DATAFILE["big"]}
STR_CHARACTERIZATION="BIG_FILE_WITH_BIG_FILE"
echo -e $(run_test $DATAFILE_S $DATAFILE_T $STR_CHARACTERIZATION)
#====================================================================================================

#====================================SMALL FILE WITH MEDIUM FILE======================================
DATAFILE_S=${DATAFILE["small"]}
DATAFILE_T=${DATAFILE["medium"]}
STR_CHARACTERIZATION="SMALL_FILE_WITH_MEDIUM_FILE"
echo -e $(run_test $DATAFILE_S $DATAFILE_T $STR_CHARACTERIZATION)
#====================================================================================================

#====================================SMALL FILE WITH BIG FILE====================================
DATAFILE_S=${DATAFILE["small"]}
DATAFILE_T=${DATAFILE["big"]}
STR_CHARACTERIZATION="SMALL_FILE_WITH_BIG_FILE"
echo -e $(run_test $DATAFILE_S $DATAFILE_T $STR_CHARACTERIZATION)
#====================================================================================================

#====================================MEDIUM FILE WITH BIG FILE==========================================
DATAFILE_S=${DATAFILE["medium"]}
DATAFILE_T=${DATAFILE["big"]}
STR_CHARACTERIZATION="MEDIUM_FILE_WITH_BIG_FILE"
echo -e $(run_test $DATAFILE_S $DATAFILE_T $STR_CHARACTERIZATION)
#====================================================================================================


#Remove executable files
rm parallel_levenshtein
rm sequential_levenshtein
