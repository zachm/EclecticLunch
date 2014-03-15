#!/usr/bin/env python
from datetime import datetime, date

from flask import Flask
from flask import render_template
from flask import request, redirect, session, url_for
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
    return redirect('/login')

def make_block_user(uinfo):
    return """<div class='user'>
        <div style='float:left'><img src='%s' alt='%s' /></div>
        <div>%s (%s)</div>
        </div>""" % (uinfo.pic_url, uinfo.username,
                   uinfo.full_name, uinfo.username)


def get_or_create(klass, **kwargs):
    obj = klass.query.filter_by(**kwargs).first()
    if obj is not None:
        return obj

    obj = klass(**kwargs)
    models.db.session.add(obj)
    models.db.session.commit()

    return obj


@app.route("/submit/<user>")
def submit(user):
    if len(request.args.getlist("time")) != 1:
        return "Please specify time!"
    time = int(request.args.getlist("time")[0])
    if time not in [11,12,13,14]:
        return "Valid times are 11,12,13,14!"

    lunch_time = models.LunchTime.query.filter_by(starting_hour=time).first()

    uinfo = logged_in_user()
    if uinfo is None:
        return redirect('/login')

    # TODO add user, etc. here
    get_or_create(
        models.LuncherSignup,
        lunch=get_or_create(
            models.Lunch,
            lunch_time=lunch_time,
            happening_datetime=date.today(),
        ),
        user=uinfo,
    )
    return render_template(
        'submit.html',
        status_url=url_for('status', user=uinfo.username),
    )


@app.route("/start/<user>")
def start(user):
    info = logged_in_user()
    if info is None:
        return redirect('/login')
    me_html = make_block_user(info)
    return render_template('start.html', me_html=me_html, username=info.username)


@app.route("/match/<user>")
def match(user):
    info = logged_in_user()
    if info is None:
        return redirect('/login')
    from matcher import matcher
    for lunch in models.Lunch.query.all():
        groups = matcher.make_lunch(
            user.username
            for user in lunch.signed_up_users.all()
        )
        for group in groups:
            lg = get_or_create(
                models.LunchGroup,
            )
            for user in group.get_lunchers():
                get_or_create(
                    models.LunchGroupParticipation,
                    lunch_group=lg,
                    user=models.User.query.filter_by(username=user).first(),
                )
    return redirect("/status/"+user)

def get_luncheon_group(user):
    if user.username == 'pkoch':
        return [
            auth.get_or_create_user_by_nick('plucas'),
            auth.get_or_create_user_by_nick('bstack'),
            auth.get_or_create_user_by_nick('dmitriy'),
        ]

    lgp = models.LunchGroupParticipation.query.filter_by(user=user).first()
    if lgp is None:
        return None

    return lgp.lunch_group.participants.all()


def get_user_reservation(username):
    return datetime.now()


@app.route("/status/<user>")
def status(user):
    user = logged_in_user()
    if user is None:
        return redirect('/login')

    name_str="%s (%s)" % (user.full_name, user),


    signups = models.LuncherSignup.query.filter_by(
        user=user,
    )
    message = ""

    if signups:
        signup = signups[0]
        message += "%s has been booked for a lunch with new friends, %s at %s. " % (
            user.full_name,
            signup.lunch.happening_datetime.strftime("%A"),
            signup.lunch.happening_datetime.strftime("%I:%m %p"),
        )
        message += "Please meet five minutes before this time in the Yelp lobby. "
    else:
        message += "We don't have any reservations scheduled for %s yet!" % (user.full_name,)

    lgp = get_luncheon_group(user)
    if lgp is None:
        companions = "Your companions will be selected and revealed fifteen minutes before lunch!"
        us_html=""
    else:
        companions = "Here are your friends!"
        us_html=" ".join([make_block_user(x) for x in lgp])

    return render_template(
        "status.html",
        message=message,
        companions=companions,
        name_str=name_str,
        us_html=us_html
    )


if __name__ == "__main__":
    manager.run()
