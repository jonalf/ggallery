#start of year
#change YEAR up top
#run setup_year to clear old users and make new tables
#run filer.setup_year to create new folders for images
#make sure the owner for the new directories is www-data 
#run add_user to add individual users or populate_users to batch add from file

import sqlite3, csv
from os import remove, stat, path
from sys import argv

DIR = path.dirname(__file__) or '.'
DIR += '/'
DBFILE = DIR + 'ggallery.db'
USER_FILE = DIR + '../data/users.csv'

USER = 0
ADMIN = 1
ARCHIVE = 2

VISIBLE = 0
EDITABLE = 1

YEAR = 2022

#create the database
def setup():
    build_galleries()
    build_users()
    build_images(YEAR)
    build_code(YEAR)
    add_gallery('intro', YEAR, EDITABLE)

def setup_year():
    build_users()
    build_images(YEAR)
    build_code(YEAR)

def build_galleries():
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()

    try:
        cmd = "DROP TABLE galleries"
        cur.execute( cmd )
        db.commit()
    except:
        print("galleries table does not exist")
    cmd = 'CREATE TABLE galleries (id INTEGER PRIMARY KEY, name TEXT, year INTEGER, perm INTEGER, size INTEGER)'
    cur.execute(cmd)
    db.commit()

def add_gallery(name, permission):
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()

    #cmd = 'INSERT INTO galleries VALUES(null, "%s", "%d", %d, 0)'%(name, year, permission)
    cmd = 'INSERT INTO galleries VALUES(null, ?, ?, ?, 0)'
    cur.execute(cmd, (name, YEAR, permission))
    db.commit()

# This should change to archive the old users (set priv to 2)
# this was the SQL command used in spirng 2021
# UPDATE users SET priv = 2 WHERE priv = 0;
def build_users():
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()

    '''
    #do not delte old users anymore
    try:
        cmd = "DROP TABLE users"
        cur.execute( cmd )
        db.commit()
    except:
        print "users table does not exist"
    cmd = 'CREATE TABLE users (id INTEGER PRIMARY KEY, stuyd TEXT, name TEXT, priv INTEGER)'
    '''
    cmd = 'UPDATE users SET priv = 2 WHERE priv = 0'
    cur.execute(cmd)
    db.commit()
    populate_users()

def add_user(stuyd, name, priv):
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()
    #cmd = 'INSERT INTO users VALUES(null, "%s", "%s", "%d")'%(stuyd, name, priv)
    cmd = 'INSERT INTO users VALUES(null, ?, ?, ?)'
    cur.execute(cmd, (stuyd, name, priv))
    db.commit()

def populate_users():
    f = open(USER_FILE)
    users = csv.DictReader(f)
    for user in users:
        rights = USER
        if user['rights'] == 'admin':
            rights = ADMIN
        add_user(user['stuyd'], user['name'], rights)

def build_images(year):
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()
    try:
        cmd = "DROP TABLE images_%d"%year
        cur.execute( cmd )
        db.commit()
    except:
        print "images table does not exist"
    cmd = 'CREATE TABLE images_%d (id INTEGER PRIMARY KEY, author TEXT, gallery TEXT, format TEXT, title TEXT)'%year
    cur.execute(cmd)
    db.commit()

def build_code(year):
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()
    try:
        cmd = "DROP TABLE code_%d"%year
        cur.execute( cmd )
        db.commit()
    except:
        print "code table does not exist"
    cmd = 'CREATE TABLE code_%d (id INTEGER, author TEXT, gallery TEXT)'%year
    cur.execute(cmd)
    db.commit()

def add_image(author, year, gallery, img_format, code, title):
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()
    #cmd = 'INSERT INTO images_%d VALUES(null, "%s", "%s", "%s", "%s")'%(year, author, gallery, img_format, title)
    cmd = 'INSERT INTO images_%d VALUES(null, ?, ?, ?, ?)'%year
    cur.execute(cmd, (author, gallery, img_format, title))
    image_id = cur.lastrowid
    db.commit()
    if code:
        cmd = 'INSERT INTO code_%d VALUES(?, ?, ?)'%year
        cur.execute(cmd, (image_id, author, gallery))
    cmd = 'UPDATE galleries SET size = size + 1 WHERE name = ? AND year = ?'
    cur.execute(cmd, (gallery, year))
    db.commit()
    return image_id

def remove_image(id):
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()

    #cmd = 'SELECT gallery, format FROM images_%d WHERE id=%d'%(year, id)
    cmd = 'SELECT gallery, format FROM images_%d WHERE id=?'%YEAR
    cur.execute(cmd, (id,))
    entry = cur.fetchone()
    gallery = entry[0]
    img_format = entry[1]

    #cmd = 'DELETE FROM images_%d WHERE id=%d'%(year, id)
    cmd = 'DELETE FROM images_%d WHERE id=?'%YEAR
    cur.execute(cmd, (id,))
    cmd = 'DELETE FROM code_%d WHERE id=?'%YEAR
    cur.execute(cmd, (id,))
    cmd = 'UPDATE galleries SET size = size - 1 WHERE name = ? AND year = ?'
    cur.execute(cmd, (gallery, YEAR))
    db.commit()
    return img_format

def get_visible_galleries(year=YEAR):
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()

    #cmd = 'SELECT name FROM galleries WHERE (year = %d) AND (perm = %d or perm = %d)'%(YEAR, VISIBLE, EDITABLE)
    cmd = 'SELECT name FROM galleries WHERE (year = ?) AND (perm = ? or perm = ?)'
    cur.execute(cmd, (year, VISIBLE, EDITABLE))
    galleries = cur.fetchall()
    galleries = [x[0] for x in galleries]
    return galleries

def get_editable_galleries():
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()

    #cmd = 'SELECT * FROM galleries WHERE year = %d AND perm = %d'%(YEAR, EDITABLE)
    cmd = 'SELECT * FROM galleries WHERE year = ? AND perm = ?'
    cur.execute(cmd, (YEAR, EDITABLE))
    galleries = cur.fetchall()
    return galleries

def lookup_user(stuyd):
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()
    cmd = 'SELECT * FROM users WHERE stuyd = ?'
    cur.execute(cmd, (stuyd,))
    user = cur.fetchone()
    if not user:
        return False
    return {'stuyd':user[1], 'name':user[2], 'rights':user[3]}

def get_user_name(stuyd):
    #return lookup_user(stuyd)['name']
    name = lookup_user(stuyd)
    #print '================'
    #print name
    if name:
        return name['name']
    else:
        return 'Clyde Sinclair'
    
def get_image_list(gallery, year=YEAR):
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()
    #cmd = 'SELECT * FROM images_%d WHERE gallery = "%s"'%(YEAR, gallery)
    cmd = 'SELECT * FROM images_%d WHERE gallery = ?'%year
    cur.execute(cmd, (gallery,))
    images = cur.fetchall()
    image_list = []
    for image in images:
        author = get_user_name(image[1])
        image_list.append( {'image':'%d.%s'%(image[0], image[3]),'author':author, 'title':image[4]})
    return image_list

def code_exists(image_id):
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()
    #cmd = 'SELECT * FROM images_%d WHERE gallery = "%s"'%(YEAR, gallery)
    cmd = 'SELECT * FROM code_%d WHERE id = ?'%YEAR
    cur.execute(cmd, (image_id,))
    result = cur.fetchone()
    return result;

def get_random_image(gallery, year=YEAR):
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()
    cmd = 'SELECT * FROM images_%d WHERE gallery = ? ORDER BY RANDOM() LIMIT 1'%year
    cur.execute(cmd, (gallery,))
    return cur.fetchone()

def get_past_years():
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()
    cmd = 'SELECT year FROM galleries'
    cur.execute(cmd)
    ys = cur.fetchall()
    years = {y[0] for y in ys}
    return [y for y in years if y != YEAR]


def get_user_images(stuyd):
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()
    cmd = 'SELECT id, gallery FROM images_%d WHERE author=?'%YEAR
    cur.execute(cmd, (stuyd, ))
    images = cur.fetchall()
    return images

if __name__ == '__main__':
    #setup()
    if len(argv) < 2:
        print('Usage: db.py -c|v|s [username]')
    elif (argv[1] == '-v'):
        if len(argv) != 3:
            print('[view images] Usage: db.py -v [username]')
        else:
            print(get_user_images(argv[2]))
    elif argv[1] == '-c':
        user = raw_input("enter suyid: ")
        name = raw_input("enter full name: ")
        print('making regular user account: %s %s'%(user, name))
        add_user(user, name, USER)
    elif argv[1] == '-p':
        ans = raw_input('add users from %s y/N? '%USER_FILE)
        if ans == 'y':
            print('adding users')
            populate_users()
    elif argv[1] == '-s':
        #run setup_year to clear old users and make new tables
        #run filer.setup_year to create new folders for images
        ans = raw_input("YEAR is set to: %d\nproceed with new year setup? (y/N)"%YEAR)
        if (ans == 'y'):
            print('Setting up database...')
            setup_year()
            print('Settting up file structure...')
            filer.setup_year()
