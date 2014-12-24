'''
Created on 21/03/2014

@author: fellipe
'''
import os
import csv
import xml.dom.minidom
import html.parser
from pprint import pprint

def add_per_classification_paper(papers_per_classification,paperi):
	per_classification_array = papers_per_classification.get(paperi.get('classification'))
	if per_classification_array == None :
		per_classification_array = []
	papers_per_classification[paperi.get('classification')] = per_classification_array
	per_classification_array.append(paperi)


if __name__ == '__main__':
    

    filenames_list =[
                ('courts','PA_court_files.txt'),
                ('showbiz','PA_showbiz_files.txt')
        ]
    
    root = "/media/dados/Colecoes de Dados/meter_corpus"
    
    papers = {}
    papers_per_classification = {}
    
    for filenamesi in filenames_list:
        folder_path = os.path.join(root,'file_index',filenamesi[0])
        pa_file = open(os.path.join(folder_path,filenamesi[1]), 'r')
        
        for linei in pa_file.readlines():
            linei = linei.replace('\n','')
            features = linei.split('/')
            paperi = {'path':linei, 'newspaper':features[2], 'catchline':features[-2], 'date':features[-3], 'domain':features[4], 'filename':features[-1],'classification':'source'}
#            pprint(features)
#            pprint(paperi)
#            exit(0)
            with open(root.replace('/meter_corpus', linei),'r', encoding ='latin1') as content_file:
                content = content_file.read()
                paperi['content'] = content
                
            papers[linei] = paperi
            add_per_classification_paper(papers_per_classification,paperi)
        
        print(("folder_path:%s"%folder_path))
        
        for classification_file in ('partially_derived', 'wholly_derived', 'non_derived'):
            pa_file = open(os.path.join(folder_path,classification_file+'.txt'), 'r')
            for linei in pa_file.readlines():
                linei = linei.replace('\n','')
                features = linei.split('/')
                #meter_corpus/newspapers/rawtexts/showbiz/27.09.99/beegees/beegees119_times.txt
                newspaper_name = features[6].split('_')[1].replace('.txt','') 
                paperi = {'path':linei, 'newspaper':newspaper_name, 'domain':features[3], 'date':features[4], 'catchline':features[5], 'filename':features[6],'classification':classification_file}
    
#                 print(classification_file)
#                 print(root.replace('meter_corpus', linei))
#                 exit(0) 
                with open(root.replace('meter_corpus', linei),'r', encoding ='latin1') as content_file:
                    content = content_file.read()
                    paperi['content'] = content
                    
                papers[linei] = paperi
                add_per_classification_paper(papers_per_classification,paperi)
        
    '''
        papers 			  : Papers dictionary (path as keys)    
        papers_per_classification : Papers list grouped by derived type (partially_derived, wholly_derived, source, non_derived) 
    '''
    # dumping derived type group paper count
    for classification_keyi in papers_per_classification:
            print(("%s = %d"%(classification_keyi,len(papers_per_classification.get(classification_keyi)))))

    # dumping papers per derived type group
    for classificationi in list(papers_per_classification.values()):
     for paperi in classificationi:
      print(("%s\t%s\t%s\t%s"%(paperi.get('domain'),paperi.get('classification'),paperi.get('catchline'),paperi.get('filename'))))

