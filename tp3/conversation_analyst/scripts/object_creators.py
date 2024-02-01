from ..models import File, Message, Analysis, Person, Location, RiskWord, RiskWordResult, VisFile, DateFormat, ChatGPTConvo, ChatGPTMessage

def add_message(file, timestamp, sender, message, display_message, risk_rating=0):
    m = Message.objects.get_or_create(file=file, timestamp=timestamp, sender=sender, content=message, display_content=display_message, risk_rating=risk_rating)[0]
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


def add_risk_word_result(analysis, keyword, amount, risk_factor=0):
    keyword = keyword.lower()
    k = RiskWord.objects.filter(keyword=keyword).first()
    r = RiskWordResult.objects.get_or_create(analysis=analysis, riskword=k, amount=amount)[0]
    r.save()
    return r

def add_vis(analysis, file_path):
    v = VisFile.objects.get_or_create(analysis=analysis, file_path=file_path)[0]
    v.save()
    return v

def add_date(name, example,format):
    d = DateFormat.objects.get_or_create(name=name, example=example,format=format)[0]
    d.save()
    return d

def add_chat_message(type_of_message, content, convo):
    return ChatGPTMessage.objects.create(typeOfMessage=type_of_message, content=content, convo=convo)

def add_chat_convo(slug, title, analysis, start=None, end=None):
    return ChatGPTConvo.objects.create(slug=slug, title=title, analysis=analysis, start=start, end=end)

