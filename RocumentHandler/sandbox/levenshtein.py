import sys
import getopt

INS_COST = 1
DEL_COST = 1
EXC_COST  = 1

def main():

	s = ''
	t = ''
	dynamicProgramming = 0

	#parse command line options
	try:
		opts, args = getopt.getopt(sys.argv[1:], 's:t:D')

	except getopt.GetoptError as err:
		print str(err)
		sys.exit(2)

	for o, a in opts:
		if o == '-s':
			s = a
		elif o == '-t':
			t = a
		elif o == '-D':
			dynamicProgramming = 1
	
	#call levensthein
	if(dynamicProgramming == 1):
		print "The levenshtein distance between words: '" + s + "' and '" + t + "' is " + str(levenshtein(s, t))
	else:
		print "The levenshtein distance between words: '" + s + "' and '" + t + "' is " + str(levenshteinDistance(s, t))


#levenshtein distance
def levenshteinDistance(s, t):
	
	len_s = len(s)
	len_t = len(t)

	if len_s == 0:
		return len_t

	if len_t == 0:
		return len_s

	if s[len_s - 1] == t[len_t - 1]:
		cost = 0
	else:
		cost = EXC_COST

	return min(levenstheinDistance(s[:len_s - 1], t[:len_t - 1]) + cost, levenstheinDistance(s, t[:len_t - 1]) + INS_COST, levenstheinDistance(s[:len_s - 1], t) + DEL_COST)


#levenshtein distance dynamic programming
def levenshtein(s, t):

	len_s = len(s) #size m
	len_t = len(t) #size n

	d = [[0 for j in range(len_t+1)] for i in range(len_s+1)] #d[m+1][n+1]

	for j in range(0, len_t+1): #0..m
		d[0][j] = j

	for i in range(0, len_s+1): #0..n
		d[i][0] = i

	for i in range(1, len_s+1): #1..n
		for j in range(1, len_t+1): #1..m
			if s[i-1] == t[j-1]:
				d[i][j] = min(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1])
			else:
				d[i][j] = min(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1] + EXC_COST)

	return d[len_s][len_t] #return d[m][n]

#call main method
if __name__ == "__main__":
	main()
