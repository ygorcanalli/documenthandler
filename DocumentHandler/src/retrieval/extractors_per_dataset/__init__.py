import os
def write_on_file(path, content,file_name=None, encoding = 'latin'):
#     print(path)
#     print(file_name)
#     exit()
    if file_name == None:
        file_name = (path.split(os.sep))[-1]
        path = path.replace(file_name,'')
         
    if  os.path.exists(path) == False:
        os.makedirs(path)
                        
    fo = open(os.path.join(path,file_name), "wb")
    fo.write(content.encode(encoding))
    fo.close()