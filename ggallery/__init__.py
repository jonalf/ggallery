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

#authentication wrapper
def require_login(f):
    @wraps(f)
    def inner(*args, **kwargs):
        print 'inner'
        if 'user' not in session:
            print 'not logged in'
            return render_template("base.html", message = 'Please sign in above with your stuy.edu account', user = 'Sign In')
        else:
            return f(*args, **kwargs)
    return inner


@app.route('/', methods=['POST', 'GET'])
@require_login
def root():
    galleries = db.get_visible_galleries()
    gallery_names = []
    for gallery in galleries:
        gallery_names.append(gallery[1])
    return render_template("homepage.html", user = session['user'], galleries = gallery_names)

@app.route('/upload', methods=['POST', 'GET'])
@require_login
def upload():
    return render_template("upload.html")

@app.route('/send_file', methods=['POST'])
def save_file():
    gallery = 'intro'
    img_file = request.files['img_file']
    img_code = Markup.escape(request.form['img_code'])
    if img_file.filename == '':
        flash('No File Selected')
        return redirect(url_for('upload'))

    img = Image(file=img_file)
    if img.format not in ALLOWED_TYPES:
        flash('Your image must be a .png, .gif or .jpg file')
        return redirect(url_for('upload'))
    img_id = db.add_image( session['user'], YEAR, gallery, img.format, img_code)
    if img_id < 1:
        flash('There was an error uploading your image, please try again')
    save_check = filer.add_file(img, img_id, img_code)
    if not save_check:
        flash('There was an error uploading your image, please try again. Make sure your image is a .png, .gif or .jpg file')
        return redirect(url_for('upload'))
    return redirect(url_for('root'))

@app.route('/gallery/<gallery_name>', methods=['GET'])
def gallery_view(gallery_name):
    return render_template('gallery.html', user=session['user'], gallery_name=gallery_name)





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
        print user
        print domain
        if domain == 'stuy.edu' and db.valid_user( user ):
            session['user'] = user
            return redirect(url_for('root'))
        else:
            return render_template("base.html", message = (user + ' is not an approved user for this serive.'), user = 'Sign in')

@app.route('/logout', methods=["POST", 'GET'])
@require_login
def logout():
    credentials = OAuth2Credentials.from_json(session['credentials'])
    if credentials.access_token_expired:
        return redirect(url_for('root'))

    session.pop('credentials')
    session.pop('user')
    return redirect( url_for('root') )


if __name__ == '__main__':
    #context = ('devcerts/ontrkr-dev.crt', 'devcerts/ontrkr-dev.key')
    app.debug = True
    #app.run(ssl_context=context, threaded=True)
    app.run()
