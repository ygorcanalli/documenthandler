from model.content import Document
from compare.distance import levensthein

# Read text
inputStr = str(open("input.txt", "r").read())
 
document = Document(inputStr)
paragraphs = document.get_paragraphs()
sentences = document.get_sentences()
words = document.get_words()
chars = document.get_chars()
 
documentStr = document.__str__()
 
paragraphsStr = ""
for paragraphsi in paragraphs:
    paragraphsStr += paragraphsi.__str__()
     
sentencesStr = ""
for elemi in sentences:
    sentencesStr += elemi.__str__()
     
wordsStr = ""
for elemi in words:
    wordsStr += elemi.__str__()
     
charsStr = ""
for elemi in chars:
    charsStr += elemi.__str__()
     
output = open("document.txt", "w")
output.write(documentStr)
 
output = open("paragraphs.txt", "w")
output.write(paragraphsStr)
 
output = open("sentences.txt", "w")
output.write(sentencesStr)
 
output = open("words.txt", "w")
output.write(wordsStr)
 
output = open("chars.txt", "w")
output.write(charsStr)

print levensthein("YgorCanalliu", "Ygor Canalli")


    




