from datetime import datetime, timedelta
import sys
import json
import time
import pytz
import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event

CATEGORIES = {
    '-1': 'All',
    '746': 'All Sports & Clubs',
    '747': 'All Recreation',
    '750': 'Boxing/Heavy Bag',
    '752': 'Disc Golf',
    '753': 'Field/Outdoor Sports',
    '749': 'Gym Sports',
    '751': 'Racquet Sports',
    '754': 'Skating & Hockey',
    '748': 'Swimming'
}

LOCATIONS = {
    "-1": 'All',
    "47": 'Red Pool',
    "48": 'Gold Pool',
    "49": 'UGAA Climbing Centre',
    "50": 'Combatives Rm',
    "51": 'Studio - 3213',
    "52": 'Studio - 3216',
    "53": 'Studio - 3214',
    "54": 'Studio - 3212',
    "55": 'Lobby',
    "56": 'Gryphon Fitness Centre',
    "57": 'AC 302',
    "58": 'AC 173',
    "59": 'North Field',
    "60": 'West Gym',
    "61": 'Range',
    "62": 'Combative Rm',
    "63": 'AC 210',
    "64": 'Red Arena',
    "65": 'Gold Arena',
    "66": 'Squash Courts',
    "67": '207',
    "68": 'Gryphon Lounge',
    "69": 'AC 300',
    "70": 'Gryphon Soccer Complex',
    "71": 'Main Gym',
    "72": 'AC 173',
    "73": 'North Court 1',
    "74": 'North Court 2',
    "75": 'North Court 3',
    "76": 'South Court 1',
    "77": 'South Court 2',
    "78": 'Arboretum',
    "79": 'Main Diamond',
    "80": 'Beach Courts',
    "81": 'Studio - 3206',
    "83": 'Gryphon Wrestling Rm - 3206',
    "84": 'Track',
    "86": 'Active Kids',
    "87": 'Aquatics',
    "88": 'Certifications - Aquatic & Safety',
    "89": 'Fitness',
    "90": 'Field',
    "91": 'Location',
    "92": 'Gold Pool - South Half',
    "93": 'Mitchell Cardio Room',
    "94": 'Field Hockey Pitch',
    "95": 'North Soccer Field',
    "96": 'North Soccer Field',
    "97": '3205',
    "98": 'Red Rink',
    "99": 'Gold Rink',
    "100": ' North 2',
    "101": ' North 3',
    "102": ' Half West Gym',
    "103": ' AC 173'
}


def create_ics(events):
    cal = Calendar()
    cal.add('prodid', '-//calendar//mxm.dk//')
    cal.add('version', '2.0')

    EST = pytz.timezone('US/Eastern')

    for event in events:
        ievent = Event()
        ievent.add('dtstart', event['start_time'].replace(tzinfo=EST))
        ievent.add('dtend', event['end_time'].replace(tzinfo=EST))
        ievent.add('dtstamp', datetime.now().replace(tzinfo=EST))
        ievent.add('summary', event['title'])
        ievent.add('location', event['location'])
        cal.add_component(ievent)

    with open('events.ics', 'wb') as f:
        f.write(cal.to_ical())


def get_events(num_days, categories, location, delay):
    payload = {
        'eventsDate': '',
        'resourceID': '5',
        'categoryID': '',
        'filterJson': json.dumps({'locationID': location})
    }

    for day in create_daterange(num_days):
        for categoryID in categories:
            payload['eventsDate'] = day.strftime('%Y-%m-%d')
            payload['categoryID'] = categoryID
            r = requests.post('https://fitandrec.gryphons.ca/REST/Event/getEventsDayView', data=payload)
            res_json = json.loads(r.text)
            soup = BeautifulSoup(res_json['html'], 'html.parser')

            for event in soup.find_all(class_='eventLink'):
                event_dict = {}
                event_dict['location'] = event.find(class_='location').text.strip().replace('\t', '').replace('\n', '')
                event_dict['title'] = event.h3.text.strip().replace('\t', '').replace('\n', '')
                start_time = datetime.strptime(event.find(class_='startTime').text.strip(), '%I:%M%p')
                event_dict['start_time'] = datetime.combine(day, start_time.time())
                end_time = datetime.strptime(event.find(class_='endTime').text.strip(), '%I:%M%p')
                event_dict['end_time'] = datetime.combine(day, end_time.time())

                yield event_dict

            time.sleep(delay)
            print('.', end='', flush=True)


def create_daterange(days):
    base = datetime.today()

    return [base + timedelta(days=x) for x in range(days)]

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print('Incorrect number of arguments. Use -h to show help.')
        sys.exit()

    if '-h' in sys.argv:
        print('-d\tRequired\tnumber of days in the future to get events for')
        print('-s\tRequired\tseconds between requests')
        sys.exit()

    for i in range(0, len(sys.argv)):
        if sys.argv[i] == '-d':
            days = int(sys.argv[i+1])
        if sys.argv[i] == '-s':
            seconds = int(sys.argv[i+1])

    events = get_events(days, categories=[748, 754], location=-1, delay=seconds)
    create_ics(events)
