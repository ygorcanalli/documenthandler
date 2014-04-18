class Frase(object):
    
    def __init__(self, content):
        self.palavras = []
        splited = content.split(" ")
        for i in range(len(splited)):
            self.palavras.append(splited[i])
    
    def __str__(self):
        result = ""
        for palavrai in self.palavras:
            result += " " + palavrai.__str__()
        return result
        