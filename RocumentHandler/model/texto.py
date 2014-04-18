from model.paragrafo import Paragrafo

class Texto(object):
    
    conteudo = ""

    def __init__(self, path):
        self.paragrafos = []
        conteudo = open(str(path), "r").read()
        splited = conteudo.split("\n\n")
        for i in range(len(splited)):
            self.paragrafos.append(Paragrafo(splited[i]))
           # print "\n" + splited[i]
           # print self.paragrafos[i]
            
    def __str__(self):
        result = ""
        for paragrafoi in self.paragrafos:
            result += "\n\n" + paragrafoi.__str__()
        return result  
        
        