'''
Created on Apr 17, 2014

@author: ygor
'''

class Content(object):
    '''
    classdocs
    '''
    _separator = None
        
    def __init__(self, original_string):
        self.elements = Content_part() 
        splited = original_string.split(self._separator)
        for splitedi in splited:
            if splitedi != "":
                self.elements.add(self._init_part(splitedi))
        
        
    # initialize an instance of the type of the part of the current content type
    def _init_part(self, original_string):
        return None
        
    def __str__(self):
        result = ""
        
        # iterate over elements, exept the last
        for i in range(0, len(self.elements.list)-1):
            result += str(self.elements.list[i]) + self._separator
        # cocatenate with the last element
        result += str(self.elements.list[len(self.elements.list)-1])
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
    
    def __key(self):
        return self.__str__()

    def __eq__(self, y):
        return self.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())
        
        
        
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
        
        
class Document (Content):
    
    _separator = "\n\n"
    
    def _init_part(self, original_string):
        return Paragraph(original_string)
    
    def get_paragraphs(self):
        return super(Document, self).get_paragraphs()
    
    def get_sentences(self):
        return super(Document, self).get_sentences()
    
    def get_words(self):
        return super(Document, self).get_words()
    
    def get_chars(self):
        return super(Document, self).get_chars()
        
              
        
class Paragraph (Content):
    
    _separator = ". "
    
    def _init_part(self, original_string):
        return Sentence(original_string)
            
    def get_paragraphs(self):
        return [self]
            
    def get_sentences(self):
        return super(Paragraph, self).get_sentences()
            
    def get_words(self):
        return super(Paragraph, self).get_words()
    
    def get_chars(self):
        return  super(Paragraph, self).get_chars()
               
class Sentence (Content):
    
    _separator = " "
     
    def _init_part(self, original_string):
        return Word(original_string)
    
    def get_paragraphs(self):
        return None
    
    def get_sentences(self):
        return [self]
            
    def get_words(self):
        return super(Sentence, self).get_words()
    
    def get_chars(self):
        return  super(Sentence, self).get_chars()
            
class Word (Content):
    
    _separator = ""
    
    def __init__(self, original_string):
        self.elements = Content_part() 
        splited = original_string
        for splitedi in splited:
            if splitedi != "":
                self.elements.add(self._init_part(splitedi))
    
    def _init_part(self, original_string):
        return Char(original_string)
           
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

        