'''
Created on Apr 17, 2014

@author: ygor
'''
import abc
from container import List

class Content(object):
    '''
    classdocs
    '''

    __metaclass__ = abc.ABCMeta

    _documents = {}
    _paragraphs = {}
    _sentences = {}
    _words = {}
    _chars = {}

    _separator = None

    @classmethod
    def create_document(self, original_string):
        try:
            my_document = self._documents[original_string]
        except KeyError, e:
            my_document = self._documents[original_string] = Document(original_string)

        return my_document

    @classmethod
    def create_paragraph(self, original_string):
        try:
            my_paragraph = self._paragraphs[original_string]
        except KeyError, e:
            my_paragraph = self._paragraphs[original_string] = Paragraph(original_string)

        return my_paragraph

    @classmethod
    def create_sentence(self, original_string):
        try:
            my_sentence = self._sentences[original_string]
        except KeyError, e:
            my_sentence = self._sentences[original_string] = Sentence(original_string)

        return my_sentence

    @classmethod
    def create_word(self, original_string):
        try:
            my_word = self._words[original_string]
        except KeyError, e:
            my_word = self._words[original_string] = Word(original_string)

        return my_word

    @classmethod
    def create_char(self, original_string):
        try:
            my_char = self._chars[original_string]
        except KeyError, e:
            my_char = self._chars[original_string] = Char(original_string)

        return my_char

    def __init__(self, original_string):
        self.elements = Content_part() 
        splited = original_string.split(self._separator)
        for splitedi in splited:
            if splitedi != "":
                self.elements.add(self._init_part(splitedi))
        
        
    # initialize an instance of the type of the part of the current content type
    @abc.abstractmethod
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
        result = List()
        for listi in self.elements.list:
            for wordsi in listi.get_paragraphs():
                result.append(wordsi)
            
        return result
    
    def get_sentences(self):
        result = List()
        for listi in self.elements.list:
            for sentencesi in listi.get_sentences():
                result.append(sentencesi)
        return result
    
    def get_words(self):
        result = List()
        for listi in self.elements.list:
            for wordsi in listi.get_words():
                result.append(wordsi)
        
        return result
    
    def get_chars(self):
        result = List()
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
        self.list = List()
        
#     add an element to the list 
    def add(self, elem):
        self.list.append(elem)
    
    def add_all(self, elements):
        for elementsi in elements:
            self.list.append(elementsi)
        
        
class Document (Content):
    
    _separator = "\n\n"

    def _init_part(self, original_string):
        return Content.create_paragraph(original_string)
    
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
        return Content.create_sentence(original_string)
            
    def get_paragraphs(self):
        result = List()
        result.append(self)
        return result
            
    def get_sentences(self):
        return super(Paragraph, self).get_sentences()
            
    def get_words(self):
        return super(Paragraph, self).get_words()
    
    def get_chars(self):
        return  super(Paragraph, self).get_chars()
               
class Sentence (Content):
    
    _separator = " "
     
    def _init_part(self, original_string):
        return Content.create_word(original_string)
    
    def get_paragraphs(self):
        return None
    
    def get_sentences(self):
        result = List()
        result.append(self)
        return result
            
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
        return Content.create_char(original_string)
           
    def get_paragraphs(self):
        return None
    
    def get_sentences(self):
        return None
            
    def get_words(self):
        result = List()
        result.append(self)
        return result
    
    def get_chars(self):
        return super(Word, self).get_chars()
        
            
class Char (Content):
    
    def __init__(self, original_string):
        self.elements = Content_part()
        if original_string != "":
            self.elements.add(original_string)

    def _init_part(self, original_string):
        return None

    def __str__(self):
        return self.elements.list[0]
    
    def get_paragraphs(self):
        return None
    
    def get_sentences(self):
        return None
            
    def get_words(self):
        return None
    
    def get_chars(self):
        result = List()
        result.append(self)
        return result

Content.register(Paragraph)
Content.register(Sentence)
Content.register(Word)
Content.register(Char)