'''
Created on Apr 30, 2014

@author: ygor
'''
# import numpy

DELETION_COST = 1
INSERTION_COST = 1
SUBSTITUITION_COST = 1

def levensthein(s, t):

    n = len(s) #size n
    m = len(t) #size m

    
    #d[n][m]
#     d = numpy.zeros((n+1)*(m+1)).reshape((n+1, m+1))
#     d.astype(int)
    
    d = [[0 for i in range(m+1)] for j in range(n+1)] 
    
    for i in range(0, n+1): #0..n
        d[i][0] = i

    for j in range(0, m+1): #0..m
        d[0][j] = j

    for i in range(1, n+1): #1..n
        for j in range(1, m+1): #1..m
            if s[i-1] == t[j-1]:
                d[i][j] = min(d[i-1][j] + DELETION_COST, d[i][j-1] + INSERTION_COST, d[i-1][j-1])
            else:
                d[i][j] = min(d[i-1][j] + DELETION_COST, d[i][j-1] + INSERTION_COST, d[i-1][j-1] + SUBSTITUITION_COST)

#     print d
    return d[n][m] #return d[n][m]