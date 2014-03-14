#!/usr/bin/env python
import argparse
import datetime
import json
import urllib2

from flask import Flask
from flask import render_template
from flask import request, redirect, session
from flask.ext.script import Manager, Server
import staticconf

import auth
import models
from lukas import get_person_info

db_conf = staticconf.YamlConfiguration('database.yaml')

app = Flask(__name__)

app.secret_key = """
Need to see the doctor
but I don't got the cash
Got a pain in my chest
and I hope it would come to pass
but it lingers on and on
"""

app.config['SQLALCHEMY_DATABASE_URI'] = db_conf['database_uri']

manager = Manager(app)
manager.add_command("runserver", Server(
    host='localhost',
    port=8008,
))

auth.wire_up(app)

models.wire_up(app)


def logged_in_user():
    assert 'user_id' in session, 'Not logged in.'

    return models.User.query.get(session['user_id'])

@app.route("/")
def ohai():
    session['after_auth'] = "/start"
    return redirect('/login')


def make_block_user(uinfo):
    return """<div class='user'>
        <div style='float:left'><img src='%s' alt='%s' /></div>
        <div>%s %s (%s)</div>
        </div>""" % (uinfo['photo_url'], uinfo['yelp_id'],
                   uinfo['first'], uinfo['last'], uinfo['yelp_id'])

@app.route("/submit/<user>")
def submit(user):
    if len(request.args.getlist("time")) != 1:
        return "Please specify time!"
    time = int(request.args.getlist("time")[0])
    if time not in [11,12,13,14]:
        return "Valid times are 11,12,13,14!"
    
    uinfo = get_person_info(user)
    # TODO add user, etc. here
    message = "You've been booked for a lunch with new friends!<br/>"
    message += "Please meet at "
    
    companions = "Your companions will be selected and revealed fifteen minutes before lunch!"
    return user + "\n" + str(time)



@app.route("/start/<user>")
def start(user):
    info = get_person_info(user)
    me_html = make_block_user(info)
    return render_template('start.html', me_html=me_html, username=info['yelp_id'])



def get_luncheon_group(username):
    # TODO
    return [get_person_info('jschultz'), get_person_info('pkoch'), get_person_info('ztm'), get_person_info('plucas')]

def get_user_reservation(username):
    return datetime.datetime.now()


@app.route("/status/<user>")
def status(user):
    info = get_person_info(user)
    #title = "%s is  Down to Lunch!" % info['first']

    name_str="%s %s (%s)" % (info['first'], info['last'], user),
    approved = True
    matched = True
    message = ""
    if approved:
        dt = get_user_reservation(user)
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
                           us_html=" ".join([make_block_user(x) for x in get_luncheon_group(user)])
                            )


if __name__ == "__main__":
    manager.run()
