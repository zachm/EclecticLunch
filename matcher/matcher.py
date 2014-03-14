# -*- coding: utf-8 -*-


DESIRED_GROUP_SIZE = 4


num_lunchers_to_group_sizes = {
    2: (2),
    3: (3),
    5: (3, 2),
    6: (3, 3),
    7: (4, 3),
    9: (3, 3, 3),
    10: (5, 5),
}


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


def _calc_lunch_group_sizes(num_lunchers):
    """Calculates the number of different lunch groups based on the number of
    people looking for lunch and the `DESIRED_GROUP_SIZE`.
    """
    full_groups = num_lunchers / DESIRED_GROUP_SIZE
    remainder = num_lunchers % DESIRED_GROUP_SIZE

    if num_lunchers in num_lunchers_to_group_sizes:
        return num_lunchers_to_group_sizes[num_lunchers]

    groups  = [DESIRED_GROUP_SIZE] * full_groups

    if remainder == 0:
        return groups

    if remainder == 3:
        return groups.append(3)

    # if remainder is 1 or 2, sprinkle on the first two groups
    if remainder == 2:
        groups[1] += 1

    groups[0] += 1
    return groups


def make_lunch(lunchers):
    """Takes a list of user objects and attempts to assign them to lunch groups
    of approximately `DESIRED_GROUP_SIZE`.

    The groups are created by minimizing the number of people in each group who
    have had lunch together before and maximizing the desk location distance.

    Returns a list of lists, where each sublist is a group of people who should
    have lunch together.
    """
    # determine number of groups
    num_lunchers = len(lunchers)
    lunch_group_sizes = _calc_lunch_group_sizes(num_lunchers)


    # do matching


def deliver_lunch(lunch_group):
    """Takes a group of lunchers and emails them that lunch is ready!"""
    pass
