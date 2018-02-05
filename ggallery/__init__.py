#NOTE
#The imagemagick path in version 7 is incompatiable with wand
#do this on mac: export MAGICK_HOME="/usr/local/Cellar/imagemagick@6/6.9.9-31" (check version #)
#taken from https://stackoverflow.com/questions/37011291/python-wand-image-is-not-recognized

#SETUP INSTRUCTIONS (for now)
#NEW YEAR:
#    change db.YEAR
#    update data/users.csv if needed
#    db.setup_year()
#    filer.setup_year()
#NEW GALLERY
#    db.add_gallery(<name>, YEAR, EDITABLE)


from flask import Flask, url_for, redirect, render_template, request, flash, session, Markup
from oauth2client.client import flow_from_clientsecrets, OAuth2Credentials # OAuth library, import the function and class that this use
from httplib2 import Http # The http library to issue REST calls to the oauth api
#from OpenSSL import SSL
from functools import wraps
from utils import db, filer
import json
import os
from wand.image import Image

app = Flask(__name__)
app.secret_key = 'NOT SO SECRET'


ALLOWED_TYPES = filer.ALLOWED_TYPES
DIR = os.path.dirname(__file__) or '.'
CLIENT_SECRETS = DIR + '/client_secrets.json'
YEAR = db.YEAR
ADMIN_USERS = ['dw']

f = open(DIR+'/data/secret_key.txt')
app.secret_key = f.read()
f.close()

#authentication wrapper
def require_login(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if 'user' not in session:
            print 'not logged in'
            return render_template("base.html", message = 'Please sign in above with your stuy.edu account', user = 'Sign In')
        else:
            return f(*args, **kwargs)
    return inner


@app.route('/', methods=['POST', 'GET'])
def root():
    galleries = db.get_visible_galleries()
    uname = 'login'
    rights= db.USER
    if 'user' in session:
        uname = session['user']
        rights = session['rights']
    thumbnails = {}
    for gallery in galleries:
        display_img = db.get_random_image(gallery)
        if display_img:
            thumbnails[gallery] = '%d.%s'%(display_img[0], display_img[3])
    return render_template("homepage.html", user=uname, galleries = galleries, thumbnails=thumbnails, year=db.YEAR, rights=rights)

@app.route('/upload', methods=['POST', 'GET'])
@require_login
def upload():
    galleries = db.get_visible_galleries()
    return render_template("upload.html", user=session['user'], galleries = galleries, rights=session['rights'])

@app.route('/send_file', methods=['POST'])
@require_login
def save_file():
    if ('gallery' not in request.form or
        request.form['gallery'] == 'Pick one'):
        flash('Please select the correct assignment gallery.')
        return redirect(url_for('upload'))

    gallery = request.form['gallery']
    img_file = request.files['img_file']
    img_code = Markup.escape(request.form['img_code'])
    img_title = Markup.escape(request.form['title'])
    if img_file.filename == '':
        flash('No File Selected')
        return redirect(url_for('upload'))

    img = Image(file=img_file)
    if img.format not in ALLOWED_TYPES:
        flash('Your image must be a .png, .gif or .jpg file')
        return redirect(url_for('upload'))
    img_id = db.add_image( session['user'], YEAR, gallery, img.format, img_code, img_title)
    if img_id < 1:
        flash('There was an error uploading your image, please try again')
    save_check = filer.add_file(img, img_id, img_code)
    if not save_check:
        flash('There was an error uploading your image, please try again. Make sure your image is a .png, .gif or .jpg file')
        return redirect(url_for('upload'))
    return redirect(url_for('root'))

@app.route('/gallery/<gallery_name>', methods=['GET'])
@app.route('/gallery', methods=['GET'])
def gallery_view(gallery_name=None):
    if not gallery_name:
        return redirect(url_for('root'))
    images = db.get_image_list(gallery_name)
    galleries = db.get_visible_galleries()
    rights = db.USER
    uname = 'login'
    if 'user' in session:
        uname = session['user']
        rights = session['rights']
    return render_template('gallery.html', user=uname, gallery_name=gallery_name, images=images, year=YEAR, galleries=galleries, rights=rights)

@app.route('/get_image', methods=['POST'])
def get_image():
    if 'image_id' not in request.form:
        return ''
    image_id = request.form['image_id']
    image_info = {}
    image_info['scale'] = url_for('static', filename='images/%d/scale/%s'%(YEAR, image_id));
    image_info['code'] = filer.get_code(int(image_id.split('.')[0]))
    return json.dumps(image_info)

@app.route('/admin', methods=['POST', 'GET'])
@require_login
def admin():
    galleries = db.get_visible_galleries()
    return render_template('admin.html', user=session['user'], galleries=galleries, rights=session['rights'])

@app.route('/add_gallery', methods=['POST'])
@require_login
def add_gallery():
    gallery_name = request.form['new_gallery']
    db.add_gallery(gallery_name, db.EDITABLE)
    flash('%s gallery created'%gallery_name)
    return redirect( url_for('admin') )

#EVERYTHING BELOW HERE IS FOR AUTHENTICATION
@app.route('/authenticate', methods=['POST', 'GET'])
def authenticate():
    flow = flow_from_clientsecrets(CLIENT_SECRETS,
                                   scope = 'https://www.googleapis.com/auth/userinfo.email',
                                   redirect_uri = url_for('authenticate', _external = True))

    if 'code' not in request.args: #first step of authentication
        auth_uri = flow.step1_get_authorize_url() #google login page
        return redirect(auth_uri) # Redirects to that page
    else: #login will redirect here wiht 'code' in args
        auth_code = request.args.get('code')
        credentials = flow.step2_exchange(auth_code) #second step
        session['credentials'] = credentials.to_json() #convert cred to json
        c = json.loads(session['credentials'])
        (user, domain) = tuple(c['id_token']['email'].split('@'))
        user_details = db.lookup_user( user )
        if domain == 'stuy.edu' and user_details:
            session['user'] = user
            session['name'] = user_details['name']
            session['rights'] = user_details['rights']
            return redirect(url_for('root'))
        else:
            flash(user + ' is not an approved user for this serive.')
            return redirect(url_for('root'))

@app.route('/logout', methods=["POST", 'GET'])
@require_login
def logout():
    credentials = OAuth2Credentials.from_json(session['credentials'])
    if credentials.access_token_expired:
        return redirect(url_for('root'))

    session.pop('credentials')
    session.pop('user')
    session.pop('name')
    session.pop('rights')
    return redirect( url_for('root') )


if __name__ == '__main__':
    app.debug = True
    app.run()
