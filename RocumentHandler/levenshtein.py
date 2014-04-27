import sys
import getopt

COST_ADD = 1
COST_SUB = 1
COST_EXC  = 1

def main():

	s = ''
	t = ''

	#parse command line options
	try:
		opts, args = getopt.getopt(sys.argv[1:], 's:t:')

	except getopt.GetoptError as err:
		print str(err)
		sys.exit(2)

	for o, a in opts:
		if o == '-s':
			s = a
		elif o == '-t':
			t = a
	
	#call levensthein
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
		cost = COST_EXC

	return min(levenstheinDistance(s[:len_s - 1], t[:len_t - 1]) + cost, levenstheinDistance(s, t[:len_t - 1]) + COST_ADD, levenstheinDistance(s[:len_s - 1], t) + COST_SUB)


#call main method
main()
