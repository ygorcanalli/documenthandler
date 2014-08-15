"""
Created on Apr 17, 2014

@author: ygor
"""
import abc
import re
from container import List


class Content(object):
    """
    classdocs
    """

    __metaclass__ = abc.ABCMeta

    _documents = {}
    _paragraphs = {}
    _sentences = {}
    _words = {}
    _chars = {}

    _regex = None
    _default_separator = None

    @classmethod
    def create_document(cls, original_string):
        try:
            my_document = cls._documents[original_string]
        except KeyError, e:
            my_document = cls._documents[original_string] = Document(original_string)

        return my_document

    @classmethod
    def create_paragraph(cls, original_string):
        try:
            my_paragraph = cls._paragraphs[original_string]
        except KeyError, e:
            my_paragraph = cls._paragraphs[original_string] = Paragraph(original_string)

        return my_paragraph

    @classmethod
    def create_sentence(cls, original_string):
        try:
            my_sentence = cls._sentences[original_string]
        except KeyError, e:
            my_sentence = cls._sentences[original_string] = Sentence(original_string)

        return my_sentence

    @classmethod
    def create_word(cls, original_string):
        try:
            my_word = cls._words[original_string]
        except KeyError, e:
            my_word = cls._words[original_string] = Word(original_string)

        return my_word

    @classmethod
    def create_char(cls, original_string):
        try:
            my_char = cls._chars[original_string]
        except KeyError, e:
            my_char = cls._chars[original_string] = Char(original_string)

        return my_char

    def __init__(self, original_string):
        self.elements = Content_part()
        splited = re.split(self._regex, original_string)
        for splitedi in splited:
            if splitedi != "":
                self.elements.add(self._init_part(splitedi))

    # Initialize an instance of the type of the part of the current content type
    @abc.abstractmethod
    def _init_part(self, original_string):
        return None
    
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

    def __str__(self):
        result = ""
        len_list = len(self.elements.list)

        # Iterate over elements, exept the last
        for i in range(0, len_list-1):
            result += str(self.elements.list[i]) + self._default_separator
        # Cocatenate with the last element
        if(len_list > 0):
            result += str(self.elements.list[len_list-1])
        return result

    def __key(self):
        return self.__str__()

    def __eq__(self, y):
        return self.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())

    def __len__(self):
        return len(self.elements)


        
class Content_part(object):
    """
    classdocs
    """
    def __init__(self):
        """
        Constructor
        """
        self.list = List()
        
    # Add an element to the list 
    def add(self, elem):
        self.list.append(elem)
    
    def add_all(self, elements):
        for elementsi in elements:
            self.list.append(elementsi)

    def __len__(self):
        return len(self.list)
     
        
class Document (Content):

    # One new line and a sequence of blank characters (new line, tab, space)
    _regex = "\n\s*"
    _default_separator = "\n\n"

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

    # One dot and a sequence of new line spaces    
    _regex = "\.\s*"
    _default_separator = ". "
    
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
    
    # A sequence of new line spaces 
    _regex = "\s*"
    _default_separator = " "
     
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
    
    # Split on each character
    _regex = ""
    _default_separator = ""

    def __init__(self, original_string):

        self.elements = Content_part()
        splited = original_string
        for splitedi in splited:
	    # Trim commas
            if splitedi != "" and splitedi != ",":
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
