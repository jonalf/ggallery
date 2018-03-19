import os
import db
from wand.image import Image

DIR = os.path.dirname(__file__) or '.'
DIR += '/'
DATA_DIR = DIR + '../static/images/'

YEAR = db.YEAR
THUMB_SIZE = 200
SCALE_SIZE = 500

ALLOWED_TYPES = ['PNG', 'JPEG', 'GIF']

def setup_year():
    path = DATA_DIR + str(YEAR)
    os.mkdir(path)
    path+= '/'
    os.mkdir(path + 'fullsize')
    os.mkdir(path + 'thumbs')
    os.mkdir(path + 'scale')
    os.mkdir(path + 'code')

def add_file(img, img_id, code):
    if img.format not in ALLOWED_TYPES:
        return False
    thumb_img = img.clone()
    scale_img = img.clone()

    thumb_img.transform(resize='%d>'%THUMB_SIZE)
    thumb_img.transform(resize='%d>'%SCALE_SIZE)

    path = DATA_DIR + str(YEAR)
    img.save(filename='%s/fullsize/%d.%s'%(path, img_id, img.format))
    thumb_img.save(filename='%s/thumbs/%d.%s'%(path, img_id, img.format))
    scale_img.save(filename='%s/scale/%d.%s'%(path, img_id, img.format))

    if code:
        f = open('%s/code/%d.txt'%(path, img_id), 'w')
        f.write(code)
        f.close()

    return True

def get_code(image_id):
    path = DATA_DIR + str(YEAR)
    if db.code_exists(image_id):
        f = open('%s/code/%d.txt'%(path, image_id), 'r')
        return f.read()
    return ''

def remove_file(img_id, img_format):
    path = DATA_DIR + str(YEAR)
    os.remove('%s/fullsize/%d.%s'%(path, img_id, img_format))
    os.remove('%s/thumbs/%d.%s'%(path, img_id, img_format))
    os.remove('%s/scale/%d.%s'%(path, img_id, img_format))
    if db.code_exists(img_id):
        os.remove('%s/code/%d.%s'%(path, img_id, 'txt'))
