from model.content import Document

documentStr = str(open("input.txt", "r").read())

document = Document(documentStr)
words = document.get_words()

# print document.__str__()
'''
for wordsi in words:
    print wordsi
'''   

for wordsi in words:
    print wordsi.__str__()
    
outputStr = document.__str__()
# print outputStr

output = open("output.txt", "w")
output.write(outputStr)


