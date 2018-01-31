import sqlite3, csv
from os import remove, stat, path

DIR = path.dirname(__file__) or '.'
DIR += '/'
DBFILE = DIR + 'ggallery.db'

#create the database
def setup():
    pass

#LEFT IN CURRENTLY AS EXAMPLES
def build_students():
    f = open( STUDENT_FILE )
    students = csv.DictReader( f )

    db = sqlite3.connect( DBFILE )
    cur = db.cursor()

    try:
        cmd = "DROP TABLE students"
        cur.execute( cmd )
        db.commit()
    except:
        print "students table does not exist"

    cmd = 'CREATE TABLE students (' + '"%s" TEXT, '*(len(STUDENT_FIELDS)-1) + '"%s" TEXT)'
    cmd = cmd%tuple(STUDENT_FIELDS)
    cur.execute( cmd )
    db.commit()

    
    for student in students:
        
        cmd = 'INSERT INTO students VALUES(' + '"%s", '*(len(STUDENT_FIELDS)-1) + '"%s")'
        cmd = cmd% tuple( [student[k] for k in STUDENT_FIELDS] )
        print cmd
        cur.execute( cmd )

    db.commit()
    db.close()
    f.close()

def build_faculty():
    f = open( FACULTY_FILE )
    hrs = csv.DictReader( f )
    
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()

    try:
        cmd = "DROP TABLE faculty"
        cur.execute( cmd )
        db.commit()
    except:
        print "faculty table does not exist"
        
    cmd = 'CREATE TABLE faculty (id TEXT, hr TEXT)'
    cur.execute( cmd )
    db.commit()

    for h in hrs:
        cmd = 'INSERT INTO faculty VALUES("{id}", "{hr}")'.format(id = h['id'], hr = h['hr'])
        print cmd
        cur.execute(cmd)

    db.commit()
    db.close()
    f.close()


def valid_user( fid ):
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()
    cmd = 'SELECT * FROM faculty where id = "{fid}"'.format(fid = fid)
    cur.execute(cmd)
    return cur.fetchone()
    
def get_student( osis ):
    db = sqlite3.connect( DBFILE )
    cur = db.cursor()
    student = {}
    student ['osis'] = osis

    #Get personal info first
    cmd = 'SELECT %s, %s, %s, %s, %s  FROM students where StudentID = '%tuple(STUDENT_FIELDS[1:6]) + osis 
    s = cur.execute( cmd ).fetchone()

    student['first'] = s[1]
    student['last'] = s[0]
    student['grade'] = s[2]
    student['hr'] = s[3]

    #Get class info
    cmd = 'SELECT %s, %s, %s, "%s", %s FROM students WHERE StudentID = '%tuple(STUDENT_FIELDS[6:]) + osis
    s = cur.execute( cmd )

    courses = {}
    for key in SUBJECTS:
        courses[key] = []
    for c in s:
        course = {}
        course['year'] = c[0]
        course['term'] = c[1]
        course['course'] = c[2]
        course['course title'] = c[3]
        course['mark'] = c[4]        
        course['requirements'] = get_requirements( c[2] )
        subject = get_subject( c[2] )
        courses[subject].append( course )
            
    for key in courses:
        courses[key].sort( course_compare )
        
    student['courses'] = courses
    
    return student
