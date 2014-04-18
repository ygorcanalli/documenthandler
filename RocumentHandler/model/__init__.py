from model.content import Document

documentStr = str(open("input.txt", "r").read())
document = Document(documentStr)
print document.__str__()