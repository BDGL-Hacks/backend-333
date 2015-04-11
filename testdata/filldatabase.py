'''
Read through the users.txt, events.txt, and groups.txt files and use the
partup api to fill up the database with test data.

The script takes a url as an optional command line argument. If the
argument is included, the script will direct its api calls to that.
Otherwise, the script will direct its api calls to the dev server.

Consider modifying to take another command line argument that will
let you only do users, events, or groups.
'''
from __future__ import print_function
from datetime import datetime, timedelta
from random import random
import requests
import sys

server = "http://52.4.3.6"
cookies = {}


# TODO: document the format of the input file
def add_users():
    f = open('users.txt', 'r')
    for l in f.readlines():
        line = l.strip('\n').split()
        if line[0] == '#':
            # Ignore commented lines
            continue

        data = {
            'first_name': line[0],
            'last_name': line[1],
            'email': line[2],
            'password': line[3]
        }

        r = requests.post(server + '/users/register/', data=data)
        response = r.json()

        global cookies
        if response['accepted'] is True:
            # Store the users login cookie
            cookies[data['email']] = r.cookies
        elif (response['accepted'] is False and
              'email is being used' in response['error']):
            # Log in because the cookie may be needed later
            r = requests.post(server + '/users/login/', data=data)
            response = r.json()
            if response['accepted'] is True:
                cookies[data['email']] = r.cookies
            else:
                print(l, response, file=sys.stderr)
        else:
            # Not clear what the error was so print to log file
            print(l, response, file=sys.stderr)

    f.close()


def _parse_time(displacement=0):
    '''
    Given an integer, displacement, return a string representing the
    date and time displacement days from now. The string returned will
    be of the "YYYYMMDDhhmm".
    '''
    time = datetime.now() + timedelta(days=displacement)
    info = (time.year, time.month, time.day, time.hour, time.minute)
    return '%4d%02d%02d%02d%02d' % info


def _random_name():
    '''
    Returns a random username from users.txt uniformly at random.
    '''
    name = ''
    counter = 0
    for l in open('users.txt', 'r').readlines():
        line = l.strip('\n').split()
        if line[0] == '#':
            # ignore comments
            continue

        counter += 1
        if random() < (1.0 / float(counter)):
            name = line[2]
    return name


def _parse_invite_list(num_guests=0):
    '''
    Given an integer, num_guests, randomly select num_guests users from
    users.txt to invite to the event.
    '''
    return [_random_name() for i in range(num_guests)]


# TODO: document the format of the input file
def add_events():
    f = open('events.txt', 'r')
    for l in f.readlines():
        line = l.strip('\n').split()
        if line[0] == '#':
            # Ignore commented lines
            continue

        # line[0] is the username
        cookie = cookies[line[0]]

        # Parse the rest of the line
        data = {
            'title': line[1],
            'time': _parse_time(int(line[2])),
            'location_name': line[3],
            'public': line[4],
            'age_restrictions': line[5],
            'price': line[6],
            'invite_list': ','.join(_parse_invite_list(int(line[7])))
        }

        r = requests.post(server + '/events/create/', data=data,
                          cookies=cookie)
        response = r.json()
        if response['accepted'] is False:
            print(l, response, file=sys.stderr)


# TODO: this
def add_groups():
    pass


def main(args):
    global server
    if len(args) > 1:
        server = args[1]

    add_users()
    add_events()
    # add_groups()


if __name__ == '__main__':
    main(sys.argv)
