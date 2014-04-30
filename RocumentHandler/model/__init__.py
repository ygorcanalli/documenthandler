from model.content import Document
from compare.distance import levensthein
from model.container import *

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

print "\n"
print document

s = "YgorCanalliu"
t =  "Ygor Canalli"
print "\nlevenshtein(" + s +  ", " + t + ") = " + str(levensthein(s, t))
print 

#Container casts test
my_list = List(["a", "b", "c", "a", "a", "c"])
my_bag = my_list.to_bag()
my_set = my_list.to_set()


print "\n==From List=="
print my_list
print my_list.to_bag()
print my_list.to_set()

print "\n==From Bag=="
print my_bag.to_list()
print my_bag
print my_bag.to_set()

print "\n==From set=="
print my_set.to_list()
print my_set.to_bag()
print my_set
