from model.frase import Frase

class Paragrafo(object):
    
    def __init__(self, original_string):
        self.frases = []
        splited = original_string.split(".")
        for i in range(len(splited)):
            self.frases.append(Frase(splited[i]))
    
    def __str__(self):
        result = ""
        for frasei in self.frases:
            result += "\n" + frasei.__str__()
        return result  