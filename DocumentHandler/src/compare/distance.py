"""
Created on Apr 30, 2014

@author: ygor
"""
# import numpy
from pprint import pprint


DELETION_COST = 1
INSERTION_COST = 1
SUBSTITUITION_COST = 1


def levensthein(s, t):

    #size n
    n = len(s)

    #size m
    m = len(t)

    #d[n][m]
#     d = numpy.zeros((n+1)*(m+1)).reshape((n+1, m+1))
#     d.astype(int)
    
    d = [[0 for i in range(m+1)] for j in range(n+1)]

    #0..n
    for i in range(0, n+1):
        d[i][0] = i

    #0..m
    for j in range(0, m+1):
        d[0][j] = j

    #1..n
    for i in range(1, n+1):
        #1..m
        for j in range(1, m+1):
            if s[i-1] == t[j-1]:
                d[i][j] = min(d[i-1][j] + DELETION_COST, d[i][j-1] + INSERTION_COST, d[i-1][j-1])
            else:
                d[i][j] = min(d[i-1][j] + DELETION_COST, d[i][j-1] + INSERTION_COST, d[i-1][j-1] + SUBSTITUITION_COST)

    return d[n][m] #return d[n][m]