'''
Created on 25/10/2013

@author: Fellipe
'''
import os
import re
from time import strftime, localtime

def extracted_koppel_dataset(source_path, target_path, hold_out_size = 3 ):
    if  os.path.exists(source_path) == False:
        print("path [%s] erro !"%source_path)
        exit(0)
        
    if  os.path.exists(target_path) == False:
        print("path [%s] erro !"%target_path)
        exit(0)
        
    if not(isinstance(hold_out_size, int) or hold_out_size < 0 or hold_out_size > 10):
        print('hold_out_size, must be an integer between 0 and 10')    
        exit(0)

    files_names = os.listdir(source_path)
    
#     pprint(files_names)
    
    dataset_keys = ['gender','age','work','horoscope']
    dataset = {}
    file_list = []
    
    for keyi in dataset_keys:
        dataset[keyi] = {}
        
    for filei in files_names:
        split = filei.split('.')
#         pprint(split)

        if int(split[2])> 30:
            age = '30s'
        elif int(split[2])> 20:
            age = '20s'
        else:
            age = '10s'
            
        document_dict = {'file_name':filei,
                        'gender':split[1],
                        'age':age,
                        'work':split[3],
                        'horoscope':split[4],
                         'posts':{'complete':[]}, 'profile':'', 'write_path':[]}

        file_list.append(document_dict)

        for keyi in dataset_keys:
            dataseti = dataset.get(keyi)
            if dataseti.get(document_dict[keyi]) == None:
                dataseti[document_dict[keyi]] = [document_dict]
            else: 
                dataseti[document_dict[keyi]].append(document_dict)
            
#         pprint(dataset)

    for keyi in dataset_keys:
        dataseti = dataset.get(keyi)
        log = keyi + ": "
        for classi in dataseti:
            log += " (%s:%d)"%(classi,len(dataseti.get(classi)))
        print(log)
        
    for keyi in dataset_keys:
        dataseti = dataset.get(keyi)
        for classi in dataseti:
            threshold = len(dataseti.get(classi))*hold_out_size/10
            i = 0
            for documenti in dataseti.get(classi):
                if i % 100 == 0:
                    print("%s|%s => document[%d]:%s"%(keyi, classi, i, documenti.get('file_name')))
                
                documenti.get('write_path').append(os.path.join(keyi, 'complete', classi))
                
                if i < threshold : 
                    documenti.get('write_path').append(os.path.join(keyi, '%d' % (hold_out_size*10), classi))
                else:
                    documenti.get('write_path').append(os.path.join(keyi, '%d' % ((10 -hold_out_size)*10), classi))

                i += 1
                
#                 pprint(documenti)

#     pprint(file_list)
    file_list_size = len(file_list)
    print('len(file_list) = %d'%file_list_size)
#     exit()

    i = 0
    for documenti in file_list:
        i += 1
        if i % 100 == 0:
            print("%s Writting on datasets [%d|%d]:%s"%(strftime("(%Y_%m_%d[%H:%M:%S])", localtime()), i, len(file_list), documenti.get('file_name')))

        documenti_post_lists = {'complete':[]}
        documenti_profile = ""
                
        '''
            brute force xml parsing!
        '''
        with open(os.path.join(source_path, documenti['file_name']),encoding='latin1') as file:
            content = file.read().replace('</post>','').replace('</Blog>','').replace('<Blog>','')
                     
            content = content.replace('\n\n\n','\n')
            content = content.replace('\n\n','\n')
                     
            for posti in content.split('<post>'):
                    m = re.search('<date>(.+?)</date>', posti)
                    if m:
                        found = m.group(0)
                        posti = posti.replace(found,'')
                                 
                    if posti.replace('\n','') != '':
                        documenti_post_lists.get('complete').append(posti)
#                         documenti['profile'] += "\n"+posti
                        documenti_profile += "\n"+posti
 
            posts_threshold = len(documenti_post_lists.get('complete'))*hold_out_size/10
            documenti_post_lists['%d'%(hold_out_size*10)] = []
            documenti_post_lists['%d'%((10 - hold_out_size)*10)] = []
                     
            j = 0
            for posti in documenti_post_lists.get('complete'):
                if j < posts_threshold:
                    documenti_post_lists['%d'%(hold_out_size*10)].append(posti)
                else:
                    documenti_post_lists['%d'%((10 - hold_out_size)*10)].append(posti)
                j+= 1
                    
        results_folder = 'Koppel dataset[extracted]'          
            
        '''
            writting age, gender, word an horoscope datasets!
        '''          
        for pathi in documenti['write_path']:
            final_path = os.path.join(target_path,results_folder,pathi)
#             print(final_path) 
            if  os.path.exists(final_path) == False:
                os.makedirs(final_path)
                        
            fo = open(os.path.join(final_path,documenti['file_name'].replace('.xml','')), "wb")
            fo.write(documenti_profile.encode('latin1'))
            fo.close()
                
                
        '''
            writting author by posts datasets!
        '''

#         for documenti_post_key in documenti_post_lists:
#             final_path = os.path.join(target_path,results_folder,'author_posts',documenti_post_key,documenti['file_name'].replace('.xml',''))
# #             print('-->'+final_path)
#             if  os.path.exists(final_path) == False:
#                 os.makedirs(final_path)
#  
#             post_count = 0    
#             for posti in documenti_post_lists[documenti_post_key]:
#                 post_count += 1
#  
#                 fo = open(os.path.join(final_path, "post%d"%post_count), "wb")
#                 fo.write(posti.encode('latin1'))
#                 fo.close()
                     
if __name__ == '__main__':        
    extracted_koppel_dataset(source_path='/media/dados/Colecoes de Dados/Authorship/Koppel blog authorship corpus/blogs', target_path='/media/dados/Colecoes de Dados/Authorship/Koppel blog authorship corpus/Koppel blog authorship corpus', hold_out_size=3)