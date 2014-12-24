import sys
import getopt
import multiprocessing

INS_COST = 1
DEL_COST = 1
EXC_COST = 1

vLock = multiprocessing.Semaphore(value = 0)
hLock = multiprocessing.Semaphore(value = 0)

def main():

	s = ''
	t = ''

	#parse command line options
	try:
		opts, args = getopt.getopt(sys.argv[1:], 's:t:')

	except getopt.GetoptError as err:
		print(str(err))
		sys.exit(2)

	for o, a in opts:
		if o == '-s':
			s = a
		elif o == '-t':
			t = a
	
	#call levensthein
	print("The levenshtein distance between words: '" + s + "' and '" + t + "' is " + str(levenshtein(s, t)))



#levenshtein distance dynamic programming
def levenshtein(s, t):

	len_s = len(s)
	len_t = len(t)

	#allocate distance matrix
	d = [[0 for j in range(len_t+1)] for i in range(len_s+1)]

	#initialization of distance matrix
	for j in range(0, len_t+1):
		d[0][j] = j

	for i in range(0, len_s+1):
		d[i][0] = i

	#call levenshtein
	vthread = multiprocessing.Process(target=vlevenshtein, args=(d, s, len_s, t, len_t)) 	#vertical in new thread
	vthread.start() #start new thread
	hlevenshtein(d, s, len_s, t, len_t)	#horizontal in main thread
	
	#join threads
	vthread.join()

	return d[len_s][len_t]


def hlevenshtein(d, s, len_s, t, len_t):

	rangeValue = min(len_s, len_t)
	flagMin = len_t <= len_s

	for i in range(1, rangeValue + 1):
		
		#decrease vertical sempahore
		if flagMin == 0 or i > 1:
			vLock.acquire ()

		#computing levenshtein distante for first case
		j = i + (flagMin == 0)
		if j < (len_t + 1):
			if s[i-1] == t[j-1]:
				d[i][j] = min(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1])
			else:
				d[i][j] = min(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1] + EXC_COST)

		#increase horizontal sempahore
		hLock.release()

		#computing levenshtein distante for others case
		for j in range(++j, len_t + 1):

			if s[i-1] == t[j-1]:
				d[i][j] = min(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1])
			else:
				d[i][j] = min(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1] + EXC_COST)



def vlevenshtein(d, s, len_s, t, len_t):

	rangeValue = min(len_s, len_t)
	flagMin = len_s < len_t

	for j in range(1, rangeValue + 1):
		
		#decrease vertical sempahore
		if flagMin == 0 or j > 1:
			hLock.acquire ()

		#computing levenshtein distante for first case
		i = j + (flagMin == 0)
		if i < (len_s + 1):
			if s[i-1] == t[j-1]:
				d[i][j] = min(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1])
			else:
				d[i][j] = min(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1] + EXC_COST)

		#increase horizontal sempahore
		vLock.release()

		#computing levenshtein distante for others case
		for i in range(++i, len_s + 1):

			if s[i-1] == t[j-1]:
				d[i][j] = min(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1])
			else:
				d[i][j] = min(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1] + EXC_COST)


#call main method
if __name__ == "__main__":
	main()
