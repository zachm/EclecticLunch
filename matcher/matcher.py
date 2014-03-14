# -*- coding: utf-8 -*-
from copy import copy
import email
import email.mime.text
import random
import smtplib

from main import get_person_info


DESIRED_GROUP_SIZE = 4


num_lunchers_to_group_sizes = {
    0: [],
    1: [1],
    2: [2],
    3: [3],
    5: [3, 2],
    6: [3, 3],
    7: [4, 3],
    9: [3, 3, 3],
    10: [5, 5],
}


MESSAGE_BODY_FORM = """Hey luncher!

You've got an Electic Lunch group!

The members of your group are:
{lunchers}


Meet in the lobby @ {time}.

Enjoy!"""


EMAIL_MESSAGE_SUBJECT = "You've got an Eclectic Lunch Group!"


class TooManyLunchersInGroupException(Exception):
    pass


class LunchGroup(object):

    def __init__(self, desired_size):
        self.desired_size = desired_size
        self._lunchers = []

    def add_luncher(self, luncher):
        if self.current_num_lunchers < self.desired_size:
            self._lunchers.append(luncher)
        else:
            raise TooManyLunchersInGroupException()

    @property
    def current_num_lunchers(self):
        return len(self._lunchers)

    def distance_to_luncher(self, luncher):
        return sum([luncher_distance(l, luncher) for l in self._lunchers])

    def get_lunchers(self):
        return [luncher for luncher in self._lunchers]

    def __repr__(self):
        return '{0} {1}'.format(self.desired_size, self._lunchers)


def _calc_lunch_group_sizes(num_lunchers):
    """Calculates the number of different lunch groups based on the number of
    people looking for lunch and the `DESIRED_GROUP_SIZE`.
    """
    if num_lunchers in num_lunchers_to_group_sizes:
        return num_lunchers_to_group_sizes[num_lunchers]

    full_groups = num_lunchers / DESIRED_GROUP_SIZE
    remainder = num_lunchers % DESIRED_GROUP_SIZE

    groups  = [DESIRED_GROUP_SIZE] * full_groups

    if remainder == 0:
        return groups

    if remainder == 3:
        groups.append(3)
        return groups

    # if remainder is 1 or 2, sprinkle on the first two groups
    if remainder == 2:
        groups[1] += 1

    groups[0] += 1
    return groups


def luncher_distance(l1, l2):
    """Calculates the distance between two lunchers.

    The distance is determined by how many times the two lunchers have lunched
    in the past, and the distance between their desks.
    """
    return random.randint(0, 1000)
    return get_number_of_shared_lunches(l1, l2) * 10000 + \
        get_desk_distance(l1, l2)


def make_lunch(lunchers):
    """Takes a list of user objects and attempts to assign them to lunch groups
    of approximately `DESIRED_GROUP_SIZE`.

    The groups are created by minimizing the number of people in each group who
    have had lunch together before and maximizing the desk location distance.

    Returns a list of LunchGroups.
    """
    # determine number of groups
    lunch_groups = [LunchGroup(size)
        for size in _calc_lunch_group_sizes(len(lunchers))
    ]

    # let's do a simple greedy matching
    remaining_groups = copy(lunch_groups)
    for luncher in lunchers:
        # filter out full groups
        remaining_groups = [group for group in remaining_groups
            if group.current_num_lunchers < group.desired_size
        ]
        best_fit = min(
            remaining_groups,
            key=lambda x: x.distance_to_luncher(luncher)
        )
        best_fit.add_luncher(luncher)

    return lunch_groups


def deliver_lunch(lunch_group, time):
    """Takes a group of lunchers and emails them that lunch is ready!"""

    # get luncher usernames
    lunchers = [get_person_info(l) for l in lunch_group.get_lunchers()]


    message_body = MESSAGE_BODY_FORM.format(
            lunchers='\n'.join(
                ['\t* {first} {last} ({yelp_id})'.format(
                        first=l['first'],
                        last=l['last'],
                        yelp_id=l['yelp_id'],
                    )
                    for l in lunchers
                ]
            ),
            time=time,
    )

    message = email.mime.text.MIMEText(message_body)
    message['Subject'] = EMAIL_MESSAGE_SUBJECT
    message['To'] = ','.join([
        '{0}@yelp.com'.format(l['yelp_id']) for l in lunchers
    ])
    message['From'] = "who_knows@example.com"
    message['Reply-To'] = 'THIS_IS_MADNESS@leonidas.net'

    conn = smtplib.SMTP('localhost', 25)
    conn.sendmail(message['From'], message['To'], message.as_string())
    conn.quit()
