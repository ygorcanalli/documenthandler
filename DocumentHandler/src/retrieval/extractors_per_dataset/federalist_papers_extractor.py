'''
Created on 21/03/2014

@author: fellipe
'''
import os
import csv
import xml.dom.minidom
import html.parser
from pprint import pprint
from ufrrj.extractors_per_dataset import write_on_file

if __name__ == '__main__':
    
    path = "/media/fellipe/dados/Colecoes de Dados/Authorship/Federalist Papers/papers" 
    f = open(os.path.join(path,"Paper_x_Author_List.csv"), 'r') # opens the csv file
    h = html.parser.HTMLParser()
    
    htm_papers = []
    with open(os.path.join(path,"papers.htm"), 'r', encoding ='latin1') as content_file:
        lines = content_file.readlines()
        current_content = ""
        for li in lines:
            if li.find('<?xml') != -1 or li.find('<html') != -1 or li.find('</html') != -1 or li =='\n' != -1 or li.find('<p> <br /><br /><br /><br /></p>')!= -1:
                continue
            if li.find('<h2>') != -1  and current_content != "":
                
                htm_papers.append(current_content)
                current_content = ""

            current_content += h.unescape(li)
            
    htm_papers.append(current_content)
    papers = []
    for i in range(0,len(htm_papers)):
        current_content = htm_papers[i].replace('<p>', '').replace('</p>', '').replace('<h3>', '').replace('</h3>', '').replace('<h2>', '').replace('</h2>', '')
        papers.append({'id':(i+1),'content':current_content,'author':''})
            
    print('len:%d'%len(htm_papers))

    try:
        reader = csv.reader(f)  # creates the reader object
        for row in reader:   # iterates the rows of the file in orders
            if row[0] == 'number':
                continue
#             print(row)
            paper_id = int(row[0]) - 1 
            papers[paper_id]['author'] = row[1]
            papers[paper_id]['disputed'] = row[2].replace(';','')
            if len(row) > 3:
                papers[paper_id]['obs'] = row[3]
    finally:
        f.close()      # closing
    
    for paperi in papers:
        write_on_file(path = os.path.join(path.replace('papers','papers_per_author'),paperi['author'],str(paperi['id'])),content = paperi['content'], encoding='utf8')
    pprint(papers)