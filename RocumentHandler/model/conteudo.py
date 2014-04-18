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
        self.lista = Parte_documento()
        
    def __str__(self):
        result = self.__class__.__name__ + "->" + self.lista.__str__()
        
        return result  
        
        
        
class Parte_documento(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.lista_elementos = []
        
    def add(self, elem):
        self.lista_elementos.append(elem)
        
    def __str__(self):
        result = ""
        for listai in self.lista_elementos:
            result += listai.__str__() + "\n"
        return result
        
        
class Documento:
    
    def __init__(self, path):
        self.lista_paragrafos = Parte_documento()
        conteudo = open(str(path), "r").read()
        splited = conteudo.split("\n\n")
        for i in range(len(splited)):
            self.lista_paragrafos.add(Paragrafo(splited[i]))
            
    def __str__(self):
        return self.lista_paragrafos.__str__()
            
    
    
        
class Paragrafo (Conteudo):
    
    def __init__(self, content):
        self.lista = Parte_documento()
        splited = content.split(".")
        for i in range(len(splited)):
            self.lista.add(Frase(splited[i]))
            
class Frase (Conteudo):
    
    def __init__(self, content):
        self.lista = Parte_documento()
        splited = content.split(" ")
        for i in range(len(splited)):
            self.lista.add(splited[i])
        