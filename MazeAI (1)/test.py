import operator
t= [(1, "a"), (4, "d"),(2, "b"),(3, "c")]
for item in sorted(t, key=operator.itemgetter(0)):
    print(item)
queue = [1,4,3,2]
queue.sort(reverse=True)
for i in queue:
    print(i)
