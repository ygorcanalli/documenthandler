'''
Created on Apr 17, 2014

@author: ygor
'''

class Conteudo(object):
    '''
    classdocs
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        self.elements = Parte_documento()
        
    def __str__(self):
        result = self.__class__.__name__ + "->" + self.elements.__str__()
        
        return result  
        
        
        
class Parte_documento(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.list = []
        
    def add(self, elem):
        self.list.append(elem)
        
    def __str__(self):
        result = ""
        for listai in self.list:
            result += listai.__str__() + "\n"
        return result
        
        
class Documento:
    
    def __init__(self, original_string):
        self.elements = Parte_documento()
        conteudo = open(str(original_string), "r").read()
        splited = conteudo.split("\n\n")
        for i in range(len(splited)):
            self.elements.add(Paragrafo(splited[i]))
            
    def __str__(self):
        return self.elements.__str__()
            
    
    
        
class Paragrafo (Conteudo):
    
    def __init__(self, original_string):
        self.elements = Parte_documento()
        splited = original_string.split(".")
        for i in range(len(splited)):
            self.elements.add(Frase(splited[i]))
            
class Frase (Conteudo):
    
    def __init__(self, original_string):
        self.elements = Parte_documento()
        splited = original_string.split(" ")
        for i in range(len(splited)):
            self.elements.add(splited[i])
        