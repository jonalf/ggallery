import os
import db
#from wand.image import Image
from PIL import Image


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


def resize_gif(img, new_size):
    frames = []
    for i in range(img.n_frames):
        img.seek(i)
        frames.append(img.resize((new_size, new_size)))
    return frames

def add_file(img, img_id, code):
    if img.format not in ALLOWED_TYPES:
        return False
    #thumb_img = img.clone()
    #scale_img = img.clone()
    #thumb_img = img.copy()
    #scale_img = img.copy()

    #thumb_img.resize(THUMB_SIZE, THUMB_SIZE)
    #scale_img.resize(SCALE_SIZE, SCALE_SIZE)

    path = DATA_DIR + str(YEAR)
    if not img.is_animated:
        thumb_img = img.resize((THUMB_SIZE, THUMB_SIZE))
        scale_img = img.resize((SCALE_SIZE, SCALE_SIZE))
        img.save(filename='%s/fullsize/%d.%s'%(path, img_id, img.format))
        thumb_img.save(filename='%s/thumbs/%d.%s'%(path, img_id, img.format))
        scale_img.save(filename='%s/scale/%d.%s'%(path, img_id, img.format))

    else:
        thumb_img = resize_gif(img, THUMB_SIZE)
        scale_img = resize_gif(img, SCALE_SIZE)
        imageio.mimsave('%s/fullsize/%d.%s'%(path, img_id, img.format), scale_img)
        imageio.mimsave('%s/thumbs/%d.%s'%(path, img_id, img.format), thumb_img)
        imageio.mimsave('%s/scale/%d.%s'%(path, img_id, img.format), scale_img)


    #img.save(filename='%s/fullsize/%d.%s'%(path, img_id, img.format))
    #thumb_img.save(filename='%s/thumbs/%d.%s'%(path, img_id, img.format))
    #scale_img.save(filename='%s/scale/%d.%s'%(path, img_id, img.format))

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
