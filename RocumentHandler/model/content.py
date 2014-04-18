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
        result = self.__class__.__name__ + "->" + self.elements.__str__()
        
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
        
    def __str__(self):
        result = ""
        for listi in self.list:
            result += listi.__str__() + "\n"
        return result
        
        
class Document:
    
    def __init__(self, original_string):
        self.elements = Content_part() 
        splited = original_string.split("\n\n")
        for splitedi in splited:
            self.elements.add(Paragraph(splitedi))
            
    def __str__(self):
        return self.elements.__str__()
              
        
class Paragraph (Content):
    
    def __init__(self, original_string):
        self.elements = Content_part()
        splited = original_string.split(".")
        for splitedi in splited:
            self.elements.add(Sentence(splitedi))
            
class Sentence (Content):
    
    def __init__(self, original_string):
        self.elements = Content_part()
        splited = original_string.split(" ")
        for splitedi in splited:
            self.elements.add(Word(splitedi))
            
class Word (Content):
    
    def __init__(self, original_string):
        self.elements = Content_part()
        for original_stringi in original_string:
            self.elements.add(Char(original_stringi))
            
class Char (Content):
    
    def __init__(self, original_string):
        self.elements = Content_part()
        self.elements.add(original_string)
        
    def __str__(self):
        return self.elements.list[0]
        

        