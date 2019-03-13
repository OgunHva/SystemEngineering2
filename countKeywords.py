count = 0
keyword = "randy"


searchfile = open("document3", "r")
for line in searchfile:
    if keyword in line: 
            print line
            count +=1
searchfile.close()

print count
