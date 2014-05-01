'''
Created on Apr 17, 2014

@author: ygor
'''

class Content(object):
    '''
    classdocs
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        self.elements = Content_part()
        
    def __str__(self):
        result = self.__class__.__name__ + ":\n" + self.elements.__str__()
        
        return result
    
    def get_paragraphs(self):
        result = []
        for listi in self.elements.list:
            for wordsi in listi.get_paragraphs():
                result.append(wordsi)
            
        return result
    
    def get_sentences(self):
        result = []
        for listi in self.elements.list:
            for sentencesi in listi.get_sentences():
                result.append(sentencesi)
        return result
    
    def get_words(self):
        result = []
        for listi in self.elements.list:
            for wordsi in listi.get_words():
                result.append(wordsi)
        
        return result
    
    def get_chars(self):
        result = []
        for listi in self.elements.list:
            for charsi in listi.get_chars():
                result.append(charsi)
        return result
        
        
        
class Content_part(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.list = []
        
#     add an element to the list 
    def add(self, elem):
        self.list.append(elem)
    
    def add_all(self, elements):
        for elementsi in elements:
            self.list.append(elementsi)
        
    def __str__(self):
        result = ""
        for listi in self.list:
            result += listi.__str__()
        return result
        
        
class Document (Content):
    
    def __init__(self, original_string):
        self.elements = Content_part() 
        splited = original_string.split("\n\n")
        for splitedi in splited:
            if splitedi != "":
                self.elements.add(Paragraph(splitedi))
                        
    def __str__(self):
        return "========" + self.__class__.__name__ + "========" + self.elements.__str__()

    
    def get_paragraphs(self):
        return super(Document, self).get_paragraphs()
    
    '''
    def get_paragraphs(self):
        result = []
        for listi in self.elements.list:
            for wordsi in listi.get_paragraphs():
                result.append(wordsi)
            
        return result     
    '''      
    def get_sentences(self):
        return super(Document, self).get_sentences()
    
    def get_words(self):
        return super(Document, self).get_words()
    
    def get_chars(self):
        return super(Document, self).get_chars()
        
              
        
class Paragraph (Content):
    
    def __init__(self, original_string):
        self.elements = Content_part()
        splited = original_string.split(".")
        for splitedi in splited:
            if splitedi != "":
                self.elements.add(Sentence(splitedi))
                
    def __str__(self):
        result = "\n-------" + self.__class__.__name__ + "-------\n" + self.elements.__str__() + "-----------------------\n"
        
        return result
            
    def get_paragraphs(self):
        return [self]
            
    def get_sentences(self):
        return super(Paragraph, self).get_sentences()
            
    def get_words(self):
        return super(Paragraph, self).get_words()
    
    def get_chars(self):
        return  super(Paragraph, self).get_chars()
               
class Sentence (Content):
    
    def __init__(self, original_string):
        self.elements = Content_part()
        splited = original_string.split(" ")
        for splitedi in splited:
            if splitedi != "":
                self.elements.add(Word(splitedi))
    
    def get_paragraphs(self):
        return None
    
    def get_sentences(self):
        return [self]
            
    def get_words(self):
        return super(Sentence, self).get_words()
    
    def get_chars(self):
        return  super(Sentence, self).get_chars()
            
class Word (Content):
    
    def __init__(self, original_string):
        self.elements = Content_part()
        for original_stringi in original_string:
            if original_stringi != "":
                self.elements.add(Char(original_stringi))
            
    def __str__(self):
        result = "\t" + self.__class__.__name__ + ": " + self.elements.__str__() + "\n"
        return result
           
    def get_paragraphs(self):
        return None
    
    def get_sentences(self):
        return None
            
    def get_words(self):
        return [self]
    
    def get_chars(self):
        return super(Word, self).get_chars()
        
            
class Char (Content):
    
    def __init__(self, original_string):
        self.elements = Content_part()
        if original_string != "":
            self.elements.add(original_string)
        
    def __str__(self):
        return self.elements.list[0]
    
    def get_paragraphs(self):
        return None
    
    def get_sentences(self):
        return None
            
    def get_words(self):
        return None
    
    def get_chars(self):
        return [self]
    
    def __key(self):
        return self.elements.list[0]

    def __eq__(self, y):
        return self.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())

        