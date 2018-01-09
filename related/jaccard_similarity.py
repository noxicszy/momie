from math import *
def jaccard_similarity(x,y):
    intersection_cardinality = len(set.intersection(*[set(x),set(y)]))
    union_cardinality = len(set.union(*[set(x),set(y)]))
    return intersection_cardinality/float(union_cardinality)

a= [1,2,3]
b= [1]
print jaccard_similarity(a,b)
