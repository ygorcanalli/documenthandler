import ctypes
from model.content import *
import distance

LIBRARY_PATH = 'liblevenshtein.so'

def main():
    '''Main entry point.'''

    # Load the library
    liblevenshtein = ctypes.CDLL(LIBRARY_PATH)

    # Define function arguments types
    liblevenshtein.parallel_levenshtein.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_int]
    # liblevenshtein.sequential_levenshtein.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]

    # Define function return type.
    liblevenshtein.parallel_levenshtein.restype = ctypes.c_int
    # liblevenshtein.sequential_levenshtein.restype = ctypes.c_int

    # Define the values of comparasion
    book1 = Document.create_document(open("../../files/document.txt", "r").read())
    book2 = Document.create_document(open("../../files/document.txt", "r").read())
    book_analysis = open("../../files/book_analysis.txt", "w")
    analysis_string = "\n"
    # analysis = []


    # Get the paragraphs
    paragraphs1 = book1.get_paragraphs()
    paragraphs2 = book2.get_paragraphs()

    # Iterata over all paragraphs of each book
    for i in range(0, len(paragraphs1)):
        for j in range(0, len(paragraphs2)):
            # Get the paragraphs
            p1 = str(paragraphs1.__getitem__(i))
            p2 = str(paragraphs2.__getitem__(j))

            #  Get the lenth
            p1_len = len(p1)
            p2_len = len(p2)

            # Convert the values to typec
            p1_c = (ctypes.c_char_p * p1_len)(*p1)
            p2_c = (ctypes.c_char_p * p2_len)(*p2)

            # Get the length in typec
            p1_len_c = ctypes.c_int(p1_len)
            p2_len_c = ctypes.c_int(p2_len)

            # Call function
            parallel_result = liblevenshtein.parallel_levenshtein(p1_c, p1_len_c, p2_c, p2_len_c)

            # parallel_result = distance.levensthein(p1,p2)
            #  results accumulation
            analysis_string += 'Distance(book1.p' + str(i) + ', book2.p' + str(j) + ') = ' + str(parallel_result) + '\n'

    # sequential_result = liblevenshtein.sequential_levenshtein(stringa_c, stringa_len, stringb_c, stringb_len)

    # analysis_string.join(analysis)
    book_analysis.write(analysis_string)

    book_analysis.close()

    # print 'Sequential: '
    # print sequential_result



if __name__ == '__main__':
    main()