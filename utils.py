import time
import sys
import os
import numpy as np
import mmap
import multiprocessing
import time

cpus = multiprocessing.cpu_count()

mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')  # e.g. 4015976448
mem_mib = mem_bytes/(1024.**2) 
proc_mem = mem_mib / (cpus +1)

def progressBar(value, endvalue, bar_length=20):

    percent = float(value) / endvalue
    arrow = '-' * int(round(percent * bar_length)-1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write("\rPercent: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
    sys.stdout.flush()
    
def timing_function(some_function):

    """
    Outputs the time a function takes  to execute.
    """

    def wrapper(*args,**kwargs):
        t1 = time.time()
        some_function(*args)
        t2 = time.time()
        print("Time it took to run the function: " + str((t2 - t1)))

    return wrapper


def make_sure_path_exists(path):
    import errno
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise                


def file_exists(fname):
    if os.path.isfile(fname):
        return str(fname)
    else:
        print('File does not exist')
        sys.exit(1)



    

def pretty_print(string,l = 30):
    l = l-int(len(string)/2)
    print('-'*l + '> ' + string + ' <' + '-'*l)
    


def mapcount(filename):
    '''
    Counts line in file
    '''
    f = open(filename, "r+")
    buf = mmap.mmap(f.fileno(), 0)
    lines = 0
    readline = buf.readline
    while readline():
        lines += 1
    return lines

class SliceMaker(object):
    '''
    allows to pass around slices
    '''
    def __getitem__(self, item):
        return item

def line_iterator(f,separator ='\t',count = False,columns = SliceMaker()[:],dtype = str,skiprows = 0):
    '''
    Function that iterates through a file and returns each line as a list with separator being used to split.
    N.B. it requires that all elements are the same type
    '''
    if f.split('.')[-1] != 'gz':
        i = open(f,'rt')

    elif f.split('.')[-1] == 'gz':
        i = gzip.open(f,'rt')

    for x in range(skiprows):next(i)

    if count is False:
        for line in i:
            yield np.array(line.strip().split(separator),dtype = str)[columns].astype(dtype)
    else:
        row = 0
        for line in i:
            row +=1 
            yield row,np.array(line.strip().split(separator),dtype = str)[columns].astype(dtype)



def basic_iterator(f,separator ='\t',skiprows = 0,count = False,columns = 'all'):
    '''
    Function that iterates through a file and returns each line as a list with separator being used to split.
    '''
    if f.split('.')[-1] != 'gz':
        i = open(f,'rt')

    elif f.split('.')[-1] == 'gz':
        i = gzip.open(f,'rt')

    for x in range(skiprows):next(i)

    if count is False:
        for line in i:
            line =line.strip().split(separator)
            line = return_columns(line,columns)
            yield line
    else:
        row = 0
        for line in i:
            line =line.strip().split(separator)
            line = return_columns(line,columns)
            row += 1   
            yield row,line

        
def return_columns(l,columns):
    '''
    Returns all columns, or rather the elements, provided the columns
    '''
    if columns == 'all':
        return l
    elif len(columns) == 1:
        return l[columns]
    else:
        return map(l.__getitem__,columns)
