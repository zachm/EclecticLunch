from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class NiceRepr(object):
    def __repr__(self):
        info = dict(self.__dict__)
        info.pop('_sa_instance_state')
        id = info.pop('id', None)

        return "models.%s(id=%r, %s)" % (
            type(self).__name__,
            id,
            ', '.join([
                '%s=%r' % (key, info[key])
                for key in info
            ])
        )

class User(db.Model, NiceRepr):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    full_name = db.Column(db.Text)
    pic_url = db.Column(db.Text)


class LunchTime(db.Model, NiceRepr):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    starting_hour = db.Column(db.Integer, unique=True)


class Lunch(db.Model, NiceRepr):
    id = db.Column(db.Integer, primary_key=True)

    lunch_time_id = db.Column(db.Integer, db.ForeignKey('lunch_time.id'))
    lunch_time = db.relationship(
        'LunchTime',
        backref='lunches',
    )

    happening_datetime = db.Column(db.DateTime)

    signed_up_users = db.relationship(
        'User',
        secondary='luncher_signup',
        lazy='dynamic',
    )


class LuncherSignup(db.Model, NiceRepr):
    id = db.Column(db.Integer, primary_key=True)

    lunch_id = db.Column(db.Integer, db.ForeignKey('lunch.id'))
    lunch = db.relationship(
        'Lunch',
        backref='signups',
    )

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(
        'User',
        backref='signups',
    )


class LunchGroup(db.Model, NiceRepr):
    id = db.Column(db.Integer, primary_key=True)

    lunch_id = db.Column(db.Integer, db.ForeignKey('lunch.id'))
    lunch = db.relationship(
        'Lunch',
        backref='groups',
    )

    participants = db.relationship(
        'User',
        secondary='lunch_group_participation',
        lazy='dynamic',
    )


class LunchGroupParticipation(db.Model, NiceRepr):
    id = db.Column(db.Integer, primary_key=True)

    lunch_group_id = db.Column(db.Integer, db.ForeignKey('lunch_group.id'))
    lunch_group = db.relationship(
        'LunchGroup',
        backref='participations',
    )

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(
        'User',
        backref='lunch_group_participations',
    )


def initial_creation_and_seeding():
    for name, starting_hour in (
        ('Early lunch', 11,),
        ('Proper lunch', 12,),
        ('Late lunch', 13,),
        ('Super late lunch', 14,),
    ):
        db.create_all()

        db.session.add(
            LunchTime(name=name, starting_hour=starting_hour),
        )

        db.session.commit()

def wire_up(app):
    db.init_app(app)
