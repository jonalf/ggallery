from os import remove, stat, path

DIR = path.dirname(__file__) or '.'
DIR += '/'
DATA_DIR = DIR + '../data/'

YEAR = 2017

def setup_year():
    path = DATA_DIR + str(YEAR)
    os.mkdir(path)
    path+= '/'
    os.mkdir(path + 'fullsize')
    os.mkdir(path + 'thumbs')
    os.mkdir(path + 'scale')

def add_file(image_file):

    pass
