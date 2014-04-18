from model.content import Document

documentStr = str(open("input.txt", "r").read())


document = Document(documentStr)

outputStr = document.__str__()
print outputStr

output = open("output.txt", "w")
output.write(outputStr)
