from urllib2 import Request, urlopen, URLError
from urlparse import urlparse, urljoin

from flask import request, redirect, url_for, session
from flask_oauth import OAuth
import staticconf

from wireer import Wireer


# You must configure these 3 values from Google APIs console
# https://code.google.com/apis/console
oauth_conf = staticconf.YamlConfiguration('oauth.yaml')
GOOGLE_CLIENT_ID = oauth_conf['google.client.id']
GOOGLE_CLIENT_SECRET = oauth_conf['google.client.secret']

REDIRECT_URI = '/authorized'  # one of the Redirect URIs from Google APIs console

oauth = OAuth()
google = oauth.remote_app(
    'google',
    base_url='https://www.google.com/accounts/',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    request_token_url=None,
    request_token_params={
        'scope': 'https://www.googleapis.com/auth/userinfo.email',
        'hd': 'yelp.com',
        'response_type': 'code',
    },
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_method='POST',
    access_token_params={
        'grant_type': 'authorization_code',
    },
    consumer_key=GOOGLE_CLIENT_ID,
    consumer_secret=GOOGLE_CLIENT_SECRET,
)


wireer = Wireer()


@wireer.route('/debug/auth')
def index():
    access_token, __ = session.get('access_token', (None, None,))
    if access_token is None:
        return """
            You're logged out. <a href="{login_url}">Login</a>
        """.format(
            login_url=url_for('login'),
        )

    try:
        res = urlopen(
            Request(
                'https://www.googleapis.com/oauth2/v1/userinfo',
                None,
                {
                    'Authorization': 'OAuth ' + access_token,
                },
            ),
        )
    except URLError as e:
        if e.code == 401:
            # Unauthorized - bad token
            return """
                Your login seems borked. <a href="{login_url}">Login</a><br/>
                <br/>
                Result:'''<pre>{result}</pre>'''
            """.format(
                login_url=url_for('login'),
                result=res.read(),
            )

    return """
        You're logged in! <a href="{logout_url}">Logout</a><br/>
        <br/>
        Result:'''<pre>{result}</pre>'''
    """.format(
        logout_url=url_for('logout'),
        result=res.read(),
    )


def is_safe_url(target):
    test_url = urlparse(urljoin(request.host_url, target))

    return (
        test_url.scheme in ('http', 'https')
        and urlparse(request.host_url).netloc == test_url.netloc
    )


def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target

    return None


@wireer.route('/login')
def login():
    session['after_auth'] = get_redirect_target()

    return google.authorize(
        callback=url_for('authorized', _external=True),
    )


@wireer.route('/logout')
def logout():
    session.pop('access_token')

    return_url = get_redirect_target()
    if return_url:
        return redirect(return_url)

    return redirect(url_for('index'))


@wireer.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    session['access_token'] = resp['access_token'], ''

    return redirect(session.pop('after_auth') or url_for('index'))


@google.tokengetter
def get_access_token():
    return session.get('access_token')
