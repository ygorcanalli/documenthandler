import os
import io
import copy
import csv
import pickle

'''
Created on 02/03/2014

@author: fellipe
'''
from pprint import pprint
import re
from sklearn.feature_extraction.text import CountVectorizer

def load_token_list_from_file( path, encoding="utf-8", escape = False):
        if  os.path.exists(path) == False:
            print(" * Path doesn't exists:  %s"%(path))
            exit()
        result = []
        
        with open(path, "r", encoding=encoding) as f:
            line_content = ""
            for line in f:
                line_content += line
                if line_content[-1] == '\n' and line_content[-2] == ',':
                    line_content = line_content[:-2]
                    '''
                        first line starts with: ['
                        other lines starts witk: (emptyspace)'
                    '''
                    line_content = line_content[2:-1]
                    if escape:
                        line_content = re.escape(line_content)
                    result.append(line_content)
                    line_content = ""
                    
            if not line_content in result[-1]:
                # ends with ']\n
                line_content = line_content[2:-3]
                    
                if escape:
                    line_content = re.escape(line_content)
                result.append(line_content)
                line_content = ""
#         print(path)            
#         print("len(result) = %d"%len(result))
#         pprint(result)
#         exit(0)
        return result


class E():
    label = ""
    values = ()
    regExp = None
    
    def __init__(self, label, values):
        self.label = label.upper()
        self.values = values
        self.regExp = self._toRegExp(values)
        
    '''
        protected! 
    '''    
    def _toRegExp(self,token_array):
        string_result = ""
        for valuei in token_array:
            string_result += str(valuei)+'|'
            
        return [string_result[0:-1],]            
    
    def regular_expression(self):
        if self.regExp == None or len(self.regExp) == 0:
            self.regExp = self._toRegExp(self.values)
        return self.regExp
        
class EContainer(E):
    
    def _toRegExp(self,token_array):
        reg_exp_list = []
        for ei in self.values:
            reg_exp_list += ei.regular_expression()
        return reg_exp_list

    def __init__(self):
        super().__init__(self.__class__.__name__,self.values)
    

    def regular_expression(self):
        return super().regular_expression()

class Punctiation(EContainer):
    DOT = E("DOT",("\.",))
    COMMA = E("COMMA",(",",))
    SEMICOLON = E("SEMICOLON",(";",))
    QUERY = E("QUERY",("\?",))
    EXCLAMATION_MARK = E("EXCLAMATION_MARK",("!",))
    COLON = E("COLON",(":",))
    _3DOT = E("_3DOT",("\.{2,3}",))
    _3QUERY = E("_3QUERY",("\?{2,3}",))
    _3EXCLAMATION_MARK = E("_3EXCLAMATION_MARK",("\!{2,3}",))

    values = (DOT, COMMA,SEMICOLON, QUERY, EXCLAMATION_MARK, COLON, _3DOT,_3QUERY,_3EXCLAMATION_MARK)

class Function_words(EContainer):
    AUXILIARY_VERBS = E("AUXILIARY_VERBS",("be able to","can","could","dare","had better","have to","may","might","must","need to","ought","ought to","shall","should","used to","will","would"))
    CONJUNCTIONS = E("CONJUNCTIONS",("accordingly","after","albeit","although","and","as","because","before","both","but","consequently","either","for","hence","however","if","neither","nevertheless","nor","once","or","since","so","than","that","then","thence","therefore","tho","though","thus","till","unless","until","when","whenever","where","whereas","wherever","whether","while","whilst","yet"))
    DETERMINERS = E("DETERMINERS",("a","all","an","another","any","both","each","either","every","her","his","its","my","neither","no","other","our","per","some","that","the","their","these","this","those","whatever","whichever","your"))
    PREPOSITIONS = E("PREPOSITIONS",("aboard","about","above","absent","according to","across","after","against","ahead","ahead of","all over","along","alongside","amid","amidst","among","amongst","anti","around","as","as of","as to","aside","astraddle","astride","at","away from","bar","barring","because of","before","behind","below","beneath","beside","besides","between","beyond","but","by","by the time of","circa","close by","close to","concerning","considering","despite","down","due to","during","except","except for","excepting","excluding","failing","following","for","for all","from","given","in","in between","in front of","in keeping with","in place of","in spite of","in view of","including","inside","instead of","into","less","like","minus","near","near to","next to","notwithstanding","of","off","on","on top of","onto","opposite","other than","out","out of","outside","over","past","pending","per","pertaining to","plus","regarding","respecting","round","save","saving","similar to","since","than","thanks to","through","throughout","thru","till","to","toward","towards","under","underneath","unlike","until","unto","up","up to","upon","versus","via","wanting","with","within","without"))
    PRONOUNS = E("PRONOUNS",("all","another","any","anybody","anyone","anything","both","each","each other","either","everybody","everyone","everything","few","he","her","hers","herself","him","himself","his","I","it","its","itself","many","me","mine","myself","neither","no_one","nobody","none","nothing","one","one another","other","ours","ourselves","several","she","some","somebody","someone","something","such","that","theirs","them","themselves","these","they","this","those","us","we","what","whatever","which","whichever","who","whoever","whom","whomever","whose","you","yours","yourself","yourselves"))
    #"%, %, %, %, etc." ", , , , etc."
    QUANTIFIERS = E("QUANTIFIERS",(r"NUM\\%",r"NUM",r"etc",r"a bit of",r"a couple of",r"a few",r"a good deal of",r"a good many",r"a great deal of",r"a great many",r"a lack of",r"a little",r"a little bit of",r"a majority of",r"a minority of",r"a number of",r"a plethora of",r"a quantity of",r"all",r"an amount of",r"another",r"any",r"both",r"certain",r"each",r"either",r"enough",r"few",r"fewer",r"heaps of",r"less",r"little",r"loads",r"lots",r"many",r"masses of",r"more",r"most",r"much",r"neither",r"no",r"none",r"numbers of",r"one half, one third, one fourth, one quarter, one fifth, etc.",r"one, two, three, four, etc.",r"part",r"plenty of",r"quantities of",r"several",r"some",r"the lack of",r"the majority of",r"the minority of",r"the number of",r"the plethora of",r"the remainder of",r"the rest of",r"the whole",r"tons of",r"various"))

    values = (AUXILIARY_VERBS, CONJUNCTIONS, DETERMINERS, PREPOSITIONS, PRONOUNS, QUANTIFIERS)
    
    def to_dictionary(self):
        result = {}
        pos = 0
        for fw_listi in self.values:
            for fwi in fw_listi.values:
                if not fwi in result.keys():
                    result[fwi] = pos
                    pos += 1
        return result
'''
    Each language must be unique 
'''
class LanguageFactory():
    
    @classmethod
    def customize_language(self,language_label = "customize_language", language_elements=None, customized_token_list=None, stop_words = None):
        values = []
        
        if language_elements != None:
            for lei in language_elements:
                if not lei in values: 
                    values.append(lei)
#                 print("%s <> %s <> %s"%(lei.__class__.__name__,lei.label,lei.regular_expression()))
        
        if customized_token_list != None:
            if (isinstance(customized_token_list[0], EContainer) or isinstance(customized_token_list[0], E)):
                temp = EContainer()
                temp.values = customized_token_list
                temp.label = "customized_token_list"
                values.append(temp)
            else:
                values.append(E('customized_token_list',customized_token_list))                
            
#         pprint(values)
        result = EContainer()
        result.values = values
        result.label = language_label.upper()
        result.STOP_WORDS = stop_words
#         pprint(result.values)
#         print(result.regular_expression())
#         for lei in result.values:
#             print(" >>> %s"%(lei.regular_expression()))
        
        return result 

    class __English(EContainer):
        
        WORDS = E("WORDS",(r"(?u)\b\w\w+\b|(?u)\b\w\b",))
        NUMBERS = E("NUMBERS",("[0-9]+[\.,][0-9]+", "[0-9]+", ))
        
        #     APOSTROPHE = E("APOSTROPHE",("(?u)\b\w\w+'s\b",))
        APOSTROPHE = E("APOSTROPHE",("'s",))
    #     ''' 
    #     from wikipedia 
    #     TODO - can be inproved by http://www.enchantedlearning.com/grammar/contractions/list.shtml
    #     '''
        CONTRACTIONS = E("CONTRACTIONS",("'m","'ll","'d","'ve","'re","'s","'tis"))
        PUNCTUATION = Punctiation()
        FUNCTION_WORDS = Function_words()
        
        '''
            loading slangs from file
        '''
        slangs_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','resources',"slangs.txt")
        slangsArray = load_token_list_from_file(path = slangs_file_path, encoding = "utf-8", escape = True)

        SLANGS = E("SLANGS",slangsArray)
    
        values = (
                WORDS,
                NUMBERS,
                APOSTROPHE, 
                CONTRACTIONS, 
                PUNCTUATION,
                FUNCTION_WORDS, 
                SLANGS
                  )
        '''
            stop words must be removed (not parsed)
        '''
        STOP_WORDS = E("STOP_WORDS",("a", "be", "had", "it", "only", "she", "was", "about", "because", "has", "its", "of", "some", "we", "after", "been", "have", "last", "on", "such", "were", "all", "but", "he", "more", "one", "than", "when", "also", "by", "her", "most", "or", "that", "which", "an", "can", "his", "mr", "other", "the", "who", "any", "co", "if", "mrs", "out", "their", "will", "and", "corp", "in", "ms", "over", "there", "with", "are", "could", "inc", "mz", "s", "they", "would", "as", "for", "into", "no", "so", "this", "up", "at", "from", "is", "not", "says", "to"))

    ENGLISH = __English()

    
    @classmethod
    def createTokenizer(cls, results, language_label, ngram_range , words, numbers, apostrophe, contractions, punctiation, function_words, slangs, removeStopWords, lowercase):
        language = LanguageFactory.ENGLISH
        language_elements = []
        if words:
            language_elements.append(language.WORDS)
        if numbers:
            language_elements.append(language.NUMBERS)
        if apostrophe:
            language_elements.append(language.APOSTROPHE)
        if contractions:
            language_elements.append(language.CONTRACTIONS)
        if punctiation:
            language_elements.append(language.PUNCTUATION)
        if function_words:
            language_elements.append(language.FUNCTION_WORDS)
        if slangs:
            language_elements.append(language.SLANGS)
        

        if len(language_elements) == 0:
            language_elements = None     
        
        if removeStopWords:
            stop_words = language.STOP_WORDS
        else:
            stop_words = None     
            
        language = LanguageFactory.customize_language(language_label = language_label, language_elements = language_elements, stop_words = stop_words)
        
        results.append(Tokenizer(language=language, ngram_range = ngram_range, lowercase = lowercase).asDictionary())

    @classmethod
    def createCustomizelanguageTokenizer(cls, results, ngram_range, customized_token_list, label = None):
            
        if label != None:
            language = LanguageFactory.customize_language(customized_token_list=customized_token_list,language_label = label)
        else:
            language = LanguageFactory.customize_language(customized_token_list=customized_token_list)
        results.append(Tokenizer(language=language, ngram_range = ngram_range, lowercase = False).asDictionary())
        
class Tokenizer():
    language = None
    def __init__(self, language, ngram_range, lowercase):
        self.language = language
        self.ngram_range = ngram_range
        self.lowercase = lowercase
        self.vectorizer = CountVectorizer(tokenizer=self.tokenize)
        
    def createCountVectorizer(self, regular_expression, ngram_range, stop_list = None, lowercase = False):
        vectorizer = CountVectorizer(tokenizer=lambda doc1: re.compile(regular_expression).findall(doc1), lowercase = lowercase, ngram_range=ngram_range, stop_words = stop_list)
        return vectorizer
    
    def tokenize(self,s):
        
        result = []
        
        if self.language.STOP_WORDS != None:
            stop_list=self.language.STOP_WORDS.values
        else:
            stop_list = None

#         for valuei in language.values:           
#             rei = valuei.regular_expression()
#             pprint('\t%s ==> %s' % (valuei.label, rei))

        for rei in self.language.regular_expression():
#             print(rei)
            vectorizeri = self.createCountVectorizer(regular_expression = rei, ngram_range = self.ngram_range, stop_list = stop_list, lowercase = self.lowercase)
            analyzeri = vectorizeri.build_analyzer()
            analyzeri_token_list = analyzeri(s)
             
            result += analyzeri_token_list
             
#         print("BOW : len(result) = %d"%(len(result)))
#         print(result)
#         exit()
        return result

    def asDictionary(self):
        if self.language.STOP_WORDS == None:
            removeStopWords = False
        else:
            removeStopWords = True

        others = []            
        for valuei in self.language.values:
            others.append(valuei.label)
        
        result = {'label' : self.language.label, 
            'instance' : self, 
            'vectorizer': self.vectorizer,
            'parameters' : {
                'removeStopWords' : removeStopWords, 
                'lowercase' : self.lowercase,
                ' ngramRange' : self.ngram_range,
                'others' : others
                }
            }
        
        
        return result

def pprintToFile(folder_absolute_path, file_name,object_to_pprint):
    fo = open(os.path.join(folder_absolute_path,file_name), "wb")
    output = io.StringIO()
    pprint(object_to_pprint,stream=output)
    fo.write(output.getvalue().encode('utf-8'))
    fo.close()
    output.close()
    
def pickleObject(folder_absolute_path, file_name,object_to_pickle):    
    with open(os.path.join(folder_absolute_path,file_name), 'wb') as handle:
        pickle.dump(object_to_pickle, handle)
    
def create_ngram_range(start=1, end=1, overlapped=False):
    result = []
    for i in range(start,end):
        if overlapped:
            result.append((i,end))
        else:
            result.append((i,i))
            
    return result

def toPipelineConfigs(input_tuple):
#     pprint(input_tuple)
    pipe_input = []
    pipe_params = {}
    
    for ti in input_tuple:
        if ti != None:
            pipe_input.append( (ti.get('label'),copy.deepcopy(ti.get('instance'))) )
            for pj_ti in ti.get('parameters').keys():
                pipe_params[ti.get('label')+'__'+pj_ti] = ti.get('parameters').get(pj_ti)
            
#     pprint(pipe_input)
#     print('---------------')
#     pprint(pipe_params)

    return (pipe_input, pipe_params)
