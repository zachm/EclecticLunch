from flask import Flask
from flask import request
from flask import render_template
import argparse
import datetime
import json
import urllib2

import auth


app = Flask(__name__)

app.secret_key = """
Need to see the doctor
but I don't got the cash
Got a pain in my chest
and I hope it would come to pass
but it lingers on and on
"""

auth.wireer.wire_up(app)


@app.route("/")
def ohai():
    return "Hello, luser!"


def get_person_info(username):
    """ Given a username, get the URL, etc. for them. 
    
        Keys returned: team, photo_url, yelp_id, first, last
    """
    request_url = "http://lukas.dev.yelp.com:7777/yelployees?yelp_id="
    req = urllib2.urlopen(request_url + username)
    resp = json.loads(req.read())[0]
    resp['photo_url'] = resp['photo_urls'][0]
    del resp['photo_urls']
    return resp


@app.route("/status/<user>")
def status(user):
    info = get_person_info(user)
    title = "%s is  Down to Lunch!" % info['first']

    name_str="%s %s (%s)" % (info['first'], info['last'], user),
    approved = True
    matched = True
    message = ""
    if approved:
        dt = datetime.datetime.now()
        message += "%s has been booked for a lunch with new friends, %s at %s. " % (info['first'],
                    dt.strftime("%A"), dt.strftime("%I:%m %p"))
        message += "Please meet five minutes before this time in the Yelp lobby. "
    else:
        message += "We don't have any reservations scheduled for %s yet!" % info['first']

    if not matched:
        companions = "Your companions will be selected and revealed fifteen minutes before lunch!"
    else:
        companions = "Here are your friends!"

    return render_template("status.html",
                           message=message, companions=companions, name_str=name_str,
                           photo_url=info['photo_url']
                            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default='localhost')
    parser.add_argument("--port", "-p", type=int, default=8008)
    parser.add_argument("--no-debug", "-d", default=False, action='store_true')
    options = parser.parse_args()

    debug = not options.no_debug
    app.run(host=options.host, port=options.port, debug=debug)
