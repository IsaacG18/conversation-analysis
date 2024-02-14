from ..models import File, Message, Analysis, Person, Location, RiskWord

def add_message(file, timestamp, sender, message, display_message):
    m = Message.objects.get_or_create(file=file, timestamp=timestamp, sender=sender, content=message, display_content=display_message)[0]
    m.save()
    return m


def add_file(file):
    f = File.objects.get_or_create(file=file)[0]
    f.save()
    return f

def add_file(file):
    f = File.objects.get_or_create(file=file)[0]
    f.save()
    return f

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

def add_vis(analysis, file_path):
    v = VisFile.objects.get_or_create(analysis=analysis, file_path=file_path)[0]
    v.save()
    return v

def add_date(name, example, format, default):
    d = DateFormat.objects.get_or_create(name=name, example=example,format=format, is_default=default)[0]
    d.save()
    return d

def add_delim(name, order, value, is_default):
    delim = Delimiter.objects.get_or_create(name=name, order=order, value = value, is_default=is_default)[0]
    delim.save()
    return delim

def add_chat_message(type_of_message, content, convo):
    m = ChatGPTMessage.objects.create(typeOfMessage=type_of_message, content=content, convo=convo)
    m.save()
    return m

def add_chat_convo(slug, title, file, start=None, end=None):
    c = ChatGPTConvo.objects.create(slug=slug, title=title, file=file, start=start, end=end)
    c.save()
    return c

def add_chat_filter(content, typeOfFilter, convo):
    f = ChatGPTFilter.objects.create(typeOfFilter=typeOfFilter,content=content)
    f.save()
    fc = ChatGPTConvoFilter.objects.create(convo=convo, filter=f)
    fc.save()
    return f, fc
