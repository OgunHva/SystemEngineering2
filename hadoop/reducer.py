 #!/usr/bin/env python

from operator import itemgetter
import sys

sum = []

for line in sys.stdin:
    try:
        sum.append(line)
    except ValueError:
        continue

sum = sorted(sum)
sum = list(set(sum))

for name in sum:
    print (name)
