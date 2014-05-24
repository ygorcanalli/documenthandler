all:
	gcc ../Parallel/parallel_levenshtein_v1.c -o pv1 -Wall -pthread -lpapi
	gcc ../Parallel/parallel_levenshtein_v2.c -o pv2 -Wall -pthread -lpapi
	gcc ../Parallel/parallel_levenshtein.c -o pv3 -Wall -pthread -lpapi
	gcc ../Sequential/sequential_levenshtein.c -o s -Wall -lpapi
	clear

	./pv1 -s "`cat 1.test`" -t "`cat 2.test`"
	./pv2 -s "`cat 1.test`" -t "`cat 2.test`"
	./pv3 -s "`cat 1.test`" -t "`cat 2.test`"
	./s -s "`cat 1.test`" -t "`cat 2.test`"

	./pv1 -s "`cat 1.test`" -t "`cat 1.test`"
	./pv2 -s "`cat 1.test`" -t "`cat 1.test`"
	./pv3 -s "`cat 1.test`" -t "`cat 1.test`"
	./s -s "`cat 1.test`" -t "`cat 1.test`"

	./pv1 -s "`cat 2.test`" -t "`cat 2.test`"
	./pv2 -s "`cat 2.test`" -t "`cat 2.test`"
	./pv3 -s "`cat 2.test`" -t "`cat 2.test`"
	./s -s "`cat 2.test`" -t "`cat 2.test`"
