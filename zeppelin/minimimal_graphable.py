%python
LOOKUP=["foo","bar","baz"]
labels=["id","lookup","squared","inverted"]
a=[ "\t".join([str(x),LOOKUP[x%len(LOOKUP)],str(x*x),str(1.0/x)]) for x in range(1,100)]
print ("%%table %s\n%s" % ("\t".join(labels), "\n".join(a)))
