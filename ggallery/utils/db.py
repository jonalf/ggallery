import sqlite3, csv
from os import remove, stat, path

DIR = path.dirname(__file__) or '.'
DIR += '/'
DBFILE = DIR + 'ggallery.db'
USER_FILE = DIR + '../data/users.csv'

USER = 0
ADMIN = 1

VISIBLE = 0
EDITABLE = 1

YEAR = 2017

#create the database
def setup():
    build_galleries()
    build_users()
    build_images(YEAR)
    
def build_galleries():
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()

    try:
        cmd = "DROP TABLE galleries"
        cur.execute( cmd )
        db.commit()
    except:
        print "galleries table does not exist"

    cmd = 'CREATE TABLE galleries (id INTEGER PRIMARY KEY, name TEXT, year INTEGER, perm INTEGER, size INTEGER)'
    cur.execute(cmd)
    db.commit()

def add_gallery(name, year, permission):
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()

    cmd = 'INSERT INTO galleries VALUES(null, "%s", "%d", %d, 0)'%(name, year, permission)
    cur.execute(cmd)
    db.commit()

def build_users():
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()

    try:
        cmd = "DROP TABLE users"
        cur.execute( cmd )
        db.commit()
    except:
        print "users table does not exist"

    cmd = 'CREATE TABLE users (id INTEGER PRIMARY KEY, stuyd TEXT, name TEXT, priv INTEGER)'
    cur.execute(cmd)
    db.commit()
    populate_users()

def add_user(stuyd, name, priv):
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()
    cmd = 'INSERT INTO users VALUES(null, "%s", "%s", "%d")'%(stuyd, name, priv)
    cur.execute(cmd)
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
    cmd = 'CREATE TABLE images_%d (id INTEGER PRIMARY KEY, author TEXT, gallery TEXT)'%year
    cur.execute(cmd)
    db.commit()

def add_image(author, year, gallery):
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()
    cmd = 'INSERT INTO images_%d VALUES(null, "%s", "%s")'%(year, author, gallery)
    cur.execute(cmd)
    image_id = cur.lastrowid
    db.commit()
    cmd = 'UPDATE galleries SET size = size + 1 WHERE name = "%s" AND year = %d'%(gallery, year)
    return image_id

def valid_user( fid ):
    return True


if __name__ == '__main__':
    setup()
