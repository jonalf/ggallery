from flask import Flask, url_for, redirect, render_template, request, flash, session
from oauth2client.client import flow_from_clientsecrets, OAuth2Credentials # OAuth library, import the function and class that this use
from httplib2 import Http # The http library to issue REST calls to the oauth api
#from OpenSSL import SSL
from functools import wraps
from utils import db
import json
import os

app = Flask(__name__)
app.secret_key = 'NOT SO SECRET'

DIR = os.path.dirname(__file__) or '.'
CLIENT_SECRETS = DIR + '/client_secrets.json'

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
    return render_template("homepage.html", user = session['user'])

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
