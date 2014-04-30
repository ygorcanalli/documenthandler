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
		print "The levesthein distance between words: '" + s + "' and '" + t + "' is " + str(levensthein(s, t))
	else:
		print "The levesthein distance between words: '" + s + "' and '" + t + "' is " + str(levenstheinDistance(s, t))


#levensthein distance
def levenstheinDistance(s, t):
	
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


#levensthein distance dynamic programming
def levensthein(s, t):

	len_s = len(s) #size m
	len_t = len(t) #size n

	d = [[0 for i in range(len_t+1)] for j in range(len_s+1)] #d[m][n]

	for i in range(0, len_t+1): #0..m
		d[0][i] = i

	for j in range(0, len_s+1): #0..n
		d[j][0] = j

	for j in range(1, len_s+1): #1..n
		for i in range(1, len_t+1): #1..m
			if s[j-1] == t[i-1]:
				d[j][i] = d[j-1][i-1]
			else:
				d[j][i] = min(d[j-1][i] + DEL_COST, d[j][i-1] + INS_COST, d[j-1][i-1] + EXC_COST)

	return d[len_s][len_t] #return d[m][n]

#call main method
main()
