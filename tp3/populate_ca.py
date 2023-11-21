import os
from os.path import isfile, join

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'tp3.settings')
import django

django.setup()
from conversation_analyst.models import File, Message, Analysis, Person, Location, RiskWord


def populate():
    sample_dir = os.path.abspath(os.path.join(os.getcwd(), 'static/sample'))
    sample_files = [f for f in os.listdir(sample_dir) if isfile(join(sample_dir, f))]
    sample_messages = [
        {'timestamp': '2022-10-08T10:38:02', 'sender': 'Chris Blonde',
         'message': 'Hey Martin! How you doing?? Long time '
                    'no speak! '},
        {'timestamp': '2022-10-08T10:42:58', 'sender': 'Martin Fisher',
         'message': 'Hey Chris! Its been a minute. How are things in Philly?'},
        {'timestamp': '2022-10-08T10:45:23', 'sender': 'Chris Blonde',
         'message': "Same old same old, you know what Ma is like... doesn't make living easy. Trying my best to fit in "
                    "here, but I am missing you folks from Chattanooga "},
        {'timestamp': '2022-10-08T10:49:40', 'sender': 'Martin Fisher',
         'message': "No place quite like Philly eh but that sucks you guys don't get on better, especially now you've so "
                    "far from everyone. Hope you get that sorted out "},
        {'timestamp': '2022-10-08T10:49:17', 'sender': 'Martin Fisher', 'message': 'Anyway what can I do ya for? '},
    ]
    person_and_locations = {
        'PERSON': ['Martin', 'Chris', 'Ma', 'Philly', 'Dune'], 'GPE': ['Philly']
    }
    sample_persons = person_and_locations['PERSON']
    sample_locations = person_and_locations['GPE']

    sample_risk_words = [('SpaCy', 8, 3), ('in', 5, 2)]

    for file in sample_files:
        f = add_file(file)
    f = File.objects.get(pk=1)  # temporarity assign to random file
    for message in sample_messages:
        m = add_message(f, message['timestamp'], message['sender'], message['message'])
        print("- {0} - {1}".format(str(m), str(f)))
    a = add_analysis(f)
    for person in sample_persons:
        p = add_person(a, person)
    for location in sample_locations:
        p = add_location(a, location)
    for risk_word in sample_risk_words:
        r = add_risk_word(a, risk_word[0], risk_word[1], risk_word[2])


def add_message(file, timestamp, sender, message):
    m = Message.objects.get_or_create(file=file, timestamp=timestamp, sender=sender, content=message)[0]
    m.save()
    return m


def add_file(file):
    f = File.objects.get_or_create(file=file)[0]
    f.save()
    return f


def add_analysis(file):
    a = Analysis.objects.get_or_create(file=file)[0]
    a.save()
    return a


def add_person(analysis, name):
    p = Person.objects.get_or_create(analysis=analysis, name=name)[0]
    p.save()
    return p


def add_location(analysis, name):
    l = Location.objects.get_or_create(analysis=analysis, name=name)[0]
    l.save()
    return l


def add_risk_word(analysis, keyword, risk_factor, amount):
    r = RiskWord.objects.get_or_create(analysis=analysis, keyword=keyword, risk_factor=risk_factor, amount=amount)[0]
    r.save()
    return r


# Start excution here
if __name__ == '__main__':
    print('Starting population script...')
    populate()
    print('Finished')
