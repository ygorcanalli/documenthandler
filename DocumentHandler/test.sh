#!/bin/bash

TIME=0
SUM=0
AVG=0
STD=0

N=10 #NUMBER OF ITERATIONS

if [$1 == '']; then
	FILE_NAME="benchmark"
else
	FILE_NAME=$1
fi
OUTPUT_FILE_NAME="$FILE_NAME.out"
ERROR_FILE_NAME="$FILE_NAME.error"
LOG_FILE_NAME="$FILE_NAME.log"



declare -A DATASET
#The first key means the number of files in the dataset
#The second one means the size of each file in dataset
DATASET["small", "small"]="instances/balanced_loren"
DATASET["small", "mix"]="instances/loren"
DATASET["big", "small"]="instances/extensive_balanced_loren"
DATASET["big", "mix"]="instances/extensive_loren"
DATASET["big", "big"]="instances/big_loren"

#cat $PBS_NODEFILE | uniq > hostfile_document_handler.txt

#MPI_PATH="/opt/intel/impi_latest/bin64/mpirun -r ssh"
MPI_PATH="/usr/bin/mpiexec"
HOST_FILE="src/distributed/hosts"
NUMBER_OF_PROCCESSES=17
PARALLEL_NUMBER_OF_PROCCESSES=9


standard_deviation(){

	TIMES=$1
	AVG=$2
	N=$3

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

	CURRENT_DATASET=$1
	STR_CHARACTERIZATION=$2
	DATE=`date`
	echo -e "==================================================\n===========$DATE===========\n=================================================="
	echo -e "\n\n===========$STR_CHARACTERIZATION==========="
	echo -e "Base name: $CURRENT_DATASET"

	echo -e "=-=-=-=-=-=-=-=-No distributed-=-=-=-=-=-=-=-="
	#--------------Word--------------
	SUM=0
	for((i = 0; i < $N; i++))
	do	
		DATE=`date`
		echo -e "[$DATE [i=$i] /usr/bin/python src/distributed/no_distributed.py --alignment_mode=word --alignment_function=sequential_levenshtein -D $CURRENT_DATASET/" >> $LOG_FILE_NAME
		
		TIME=`/usr/bin/python src/distributed/no_distributed.py --alignment_mode=word --alignment_function=sequential_levenshtein -D $CURRENT_DATASET/`
		TIMES[i]=$TIME
		SUM=$(/usr/bin/awk "BEGIN{print $SUM+$TIME}") 
	done

	AVG=$(/usr/bin/awk "BEGIN{print $SUM/$N}")
	STD=$(standard_deviation $TIMES $AVG $N)
	echo -e "--------------------Words--------------------"
	echo -e "Average:  $AVG"
	echo -e "Standard deviation: $STD"

	#--------------Paragraph by words--------------
	SUM=0
	for((i = 0; i < $N; i++))
	do	
		DATE=`date`
		echo -e "[$DATE [i=$i] /usr/bin/python src/distributed/no_distributed.py --alignment_mode=paragraph_by_words --alignment_function=sequential_levenshtein -D $CURRENT_DATASET/" >> $LOG_FILE_NAME

		TIME=`/usr/bin/python src/distributed/no_distributed.py --alignment_mode=paragraph_by_words --alignment_function=sequential_levenshtein -D $CURRENT_DATASET/`
		TIMES[i]=$TIME
		SUM=$(/usr/bin/awk "BEGIN{print $SUM+$TIME}") 
	done

	AVG=$(/usr/bin/awk "BEGIN{print $SUM/$N}")
	STD=$(standard_deviation $TIMES $AVG $N)
	echo -e "--------------Paragraph by words--------------"
	echo -e "Average:  $AVG"
	echo -e "Standard deviation: $STD"


	echo -e "=-=-=-=-=-=-=-=-Distributed ($NUMBER_OF_PROCCESSES)-=-=-=-=-=-=-=-="
	#--------------Word--------------
	SUM=0
	for((i = 0; i < $N; i++))
	do	
		DATE=`date`
		echo -e "[$DATE [i=$i] $MPI_PATH -hostfile $HOST_FILE -wdir src -np $NUMBER_OF_PROCCESSES python distributed/ --alignment_mode=word --alignment_function=sequential_levenshtein -D ../$CURRENT_DATASET/" >> $LOG_FILE_NAME

		TIME=`$MPI_PATH -hostfile $HOST_FILE -wdir src -np $NUMBER_OF_PROCCESSES python distributed/ --alignment_mode=word --alignment_function=sequential_levenshtein -D ../$CURRENT_DATASET/`
		TIMES[i]=$TIME
		SUM=$(/usr/bin/awk "BEGIN{print $SUM+$TIME}") 
	done

	AVG=$(/usr/bin/awk "BEGIN{print $SUM/$N}")
	STD=$(standard_deviation $TIMES $AVG $N)
	echo -e "--------------------Words--------------------"
	echo -e "Average:  $AVG"
	echo -e "Standard deviation: $STD"

	#--------------Paragraph by words--------------
	SUM=0
	for((i = 0; i < $N; i++))
	do	
		DATE=`date`
		echo -e "[$DATE [i=$i] $MPI_PATH -hostfile $HOST_FILE -wdir src -np $NUMBER_OF_PROCCESSES python distributed/ --alignment_mode=paragraph_by_words --alignment_function=sequential_levenshtein -D ../$CURRENT_DATASET/" >> $LOG_FILE_NAME

		TIME=`$MPI_PATH -hostfile $HOST_FILE -wdir src -np $NUMBER_OF_PROCCESSES python distributed/ --alignment_mode=paragraph_by_words --alignment_function=sequential_levenshtein -D ../$CURRENT_DATASET/`
		TIMES[i]=$TIME
		SUM=$(/usr/bin/awk "BEGIN{print $SUM+$TIME}") 
	done

	AVG=$(/usr/bin/awk "BEGIN{print $SUM/$N}")
	STD=$(standard_deviation $TIMES $AVG $N)
	echo -e "--------------Paragraph by words--------------"
	echo -e "Average:  $AVG"
	echo -e "Standard deviation: $STD"



	echo -e "=-=-=-=-=-=-=-=-Distributed ($PARALLEL_NUMBER_OF_PROCCESSES)-=-=-=-=-=-=-=-="
	#--------------Word--------------
	SUM=0
	for((i = 0; i < $N; i++))
	do	
		DATE=`date`
		echo -e "[$DATE [i=$i] $MPI_PATH -hostfile $HOST_FILE -wdir src -np $PARALLEL_NUMBER_OF_PROCCESSES python distributed/ --alignment_mode=word --alignment_function=sequential_levenshtein -D ../$CURRENT_DATASET/" >> $LOG_FILE_NAME

		TIME=`$MPI_PATH -hostfile $HOST_FILE -wdir src -np $PARALLEL_NUMBER_OF_PROCCESSES python distributed/ --alignment_mode=word --alignment_function=sequential_levenshtein -D ../$CURRENT_DATASET/`
		TIMES[i]=$TIME
		SUM=$(/usr/bin/awk "BEGIN{print $SUM+$TIME}") 
	done

	AVG=$(/usr/bin/awk "BEGIN{print $SUM/$N}")
	STD=$(standard_deviation $TIMES $AVG $N)
	echo -e "--------------------Words--------------------"
	echo -e "Average:  $AVG"
	echo -e "Standard deviation: $STD"

	#--------------Paragraph by words--------------
	SUM=0
	for((i = 0; i < $N; i++))
	do	
		DATE=`date`
		echo -e "[$DATE [i=$i] $MPI_PATH -hostfile $HOST_FILE -wdir src -np $PARALLEL_NUMBER_OF_PROCCESSES python distributed/ --alignment_mode=paragraph_by_words --alignment_function=sequential_levenshtein -D ../$CURRENT_DATASET/" >> $LOG_FILE_NAME


		TIME=`$MPI_PATH -hostfile $HOST_FILE -wdir src -np $PARALLEL_NUMBER_OF_PROCCESSES python distributed/ --alignment_mode=paragraph_by_words --alignment_function=sequential_levenshtein -D ../$CURRENT_DATASET/`
		TIMES[i]=$TIME
		SUM=$(/usr/bin/awk "BEGIN{print $SUM+$TIME}") 
	done

	AVG=$(/usr/bin/awk "BEGIN{print $SUM/$N}")
	STD=$(standard_deviation $TIMES $AVG $N)
	echo -e "--------------Paragraph by words--------------"
	echo -e "Average:  $AVG"
	echo -e "Standard deviation: $STD"


	echo -e "=-=-=-=-=-=-=-=-Distributed with parallel ($PARALLEL_NUMBER_OF_PROCCESSES)-=-=-=-=-=-=-=-="
	#--------------Word--------------
	SUM=0
	for((i = 0; i < $N; i++))
	do	
		DATE=`date`
		echo -e "[$DATE [i=$i] $MPI_PATH -hostfile $HOST_FILE -wdir src -np $PARALLEL_NUMBER_OF_PROCCESSES python distributed/ --alignment_mode=word --alignment_function=parallel_levenshtein -D ../$CURRENT_DATASET/" >> $LOG_FILE_NAME

		TIME=`$MPI_PATH -hostfile $HOST_FILE -wdir src -np $PARALLEL_NUMBER_OF_PROCCESSES python distributed/ --alignment_mode=word --alignment_function=parallel_levenshtein -D ../$CURRENT_DATASET/`
		TIMES[i]=$TIME
		SUM=$(/usr/bin/awk "BEGIN{print $SUM+$TIME}") 
	done

	AVG=$(/usr/bin/awk "BEGIN{print $SUM/$N}")
	STD=$(standard_deviation $TIMES $AVG $N)
	echo -e "--------------------Words--------------------"
	echo -e "Average:  $AVG"
	echo -e "Standard deviation: $STD"

	#--------------Paragraph by words--------------
	SUM=0
	for((i = 0; i < $N; i++))
	do	
		DATE=`date`
		echo -e "[$DATE [i=$i] $MPI_PATH -hostfile $HOST_FILE -wdir src -np $PARALLEL_NUMBER_OF_PROCCESSES python distributed/ --alignment_mode=paragraph_by_words --alignment_function=parallel_levenshtein -D ../$CURRENT_DATASET/" >> $LOG_FILE_NAME

		TIME=`$MPI_PATH -hostfile $HOST_FILE -wdir src -np $PARALLEL_NUMBER_OF_PROCCESSES python distributed/ --alignment_mode=paragraph_by_words --alignment_function=parallel_levenshtein -D ../$CURRENT_DATASET/`
		TIMES[i]=$TIME
		SUM=$(/usr/bin/awk "BEGIN{print $SUM+$TIME}") 
	done

	AVG=$(/usr/bin/awk "BEGIN{print $SUM/$N}")
	STD=$(standard_deviation $TIMES $AVG $N)
	echo -e "--------------Paragraph by words--------------"
	echo -e "Average:  $AVG"
	echo -e "Standard deviation: $STD"
}


#====================================SMALL BASE WITH SMALL FILES=====================================
CURRENT_DATASET=${DATASET["small", "small"]}
STR_CHARACTERIZATION="SMALL_BASE_WITH_SMALL_FILES"
run_test $CURRENT_DATASET $STR_CHARACTERIZATION >> $OUTPUT_FILE_NAME 2>> $ERROR_FILE_NAME
#====================================================================================================

#====================================SMALL BASE WITH MIX FILES=======================================
CURRENT_DATASET=${DATASET["small", "mix"]}
STR_CHARACTERIZATION="SMALL_BASE_WITH_MIX_FILES"
run_test $CURRENT_DATASET $STR_CHARACTERIZATION >> $OUTPUT_FILE_NAME 2>> $ERROR_FILE_NAME
#====================================================================================================

#====================================BIG BASE WITH SMALL FILES=======================================
CURRENT_DATASET=${DATASET["big", "small"]}
STR_CHARACTERIZATION="BIG_BASE_WITH_SMALL_FILES"
run_test $CURRENT_DATASET $STR_CHARACTERIZATION >> $OUTPUT_FILE_NAME 2>> $ERROR_FILE_NAME
#====================================================================================================

#====================================BIG BASE WITH MIX FILES=========================================
CURRENT_DATASET=${DATASET["big", "mix"]}
STR_CHARACTERIZATION="BIG_BASE_WITH_MIX_FILES"
run_test $CURRENT_DATASET $STR_CHARACTERIZATION >> $OUTPUT_FILE_NAME 2>> $ERROR_FILE_NAME
#====================================================================================================

#====================================BIG BASE WITH BIG FILES=========================================
CURRENT_DATASET=${DATASET["big", "big"]}
STR_CHARACTERIZATION="BIG_BASE_WITH_BIG_FILES"
run_test $CURRENT_DATASET $STR_CHARACTERIZATION >> $OUTPUT_FILE_NAME 2>> $ERROR_FILE_NAME
#====================================================================================================
