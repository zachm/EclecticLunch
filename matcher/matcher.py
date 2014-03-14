# -*- coding: utf-8 -*-
import random

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

    def distance_to_luncher(self, luncher):
        return sum([luncher_distance(l, luncher) for l in self._lunchers])


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
    return random.random(1000)
    return get_number_of_shared_lunches(l1, l2) * 10000 + \
        get_desk_distance(l1, l2)


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
    lunch_groups = [LunchGroup(size) for size in lunch_group_sizes]

    # let's do a simple greedy matching
    remaining_groups = lunch_groups.copy()
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


def deliver_lunch(lunch_group):
    """Takes a group of lunchers and emails them that lunch is ready!"""
    pass
