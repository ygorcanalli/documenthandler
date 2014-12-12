import os

def get_documents_path(root):
    
    filenames_list =[
            #('courts','PA_court_files.txt'),
            ('showbiz','PA_showbiz_files.txt')
    ]
    
    index_path = []


    for filenamesi in filenames_list:
        folder_path = os.path.join(root,'file_index',filenamesi[0])
        pa_file = open(os.path.join(folder_path,filenamesi[1]), 'r')
       
        for document_pathi in pa_file.readlines():
            document_pathi = document_pathi.rstrip()
            index_path.append(document_pathi)
    
    return index_path

def get_queries_path(root):
    filenames_list =[
            #('courts','wholly_derived.txt'),
            ('showbiz','partially_derived.txt')
    ]
    
    queries_path = []
    index_path = []
    relevants_path = {}

    relevants_map = {}

    for filenamesi in filenames_list:
        folder_path = os.path.join(root,'file_index',filenamesi[0])
        pa_file = open(os.path.join(folder_path,filenamesi[1]), 'r')
       
        for query_pathi in pa_file.readlines():
            query_pathi = query_pathi.rstrip()
            as_array =  query_pathi.split('/')[0:-1]
            as_array[0] = root
            as_array[1] = 'PA' 
            index_root_path = "/".join((as_array))
            queryi_relevants = os.listdir(index_root_path)

            relevants_map[query_pathi] = []
            queries_path.append(query_pathi)
            
            for indexi in queryi_relevants:
                index_path.append(indexi)
                relevants_map[query_pathi].append(index_root_path + "/" + indexi)
           
            relevants_path[query_pathi] = queryi_relevants
    return queries_path, relevants_map
    
def pickled_path(path):
    path = path.replace("/meter_corpus", "meter_corpus")
    path = path.replace("/", "_._")
    path = path.replace(".txt", ".pkl")
    path = "documenthandler/pickled/" + path
    return path

def real_path(path):
    path = path.replace("documenthandler/pickled/meter_corpus", "/meter_corpus")
    path = path.replace("_._", "/")
    path = path.replace(".pkl", ".txt")
    return path      