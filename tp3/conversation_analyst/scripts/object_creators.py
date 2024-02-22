from ..models import (
    Message,
    Analysis,
    Person,
    Location,
    RiskWord,
    RiskWordResult,
    VisFile,
    DateFormat,
    Delimiter,
    ChatGPTMessage,
    ChatGPTFilter,
    ChatGPTConvoFilter,
    CustomThresholds,
    GptSwitch,
)


def add_message(file, timestamp, sender, message, display_message=None, risk_rating=0):
    m = Message.objects.get_or_create(
        file=file, timestamp=timestamp, sender=sender, content=message
    )[0]
    m.save()
    return m


def update_message(id, display_message, entities, risk_rating=0):
    try:
        m = Message.objects.get(id=id)
        m.tags = ",".join(entities)
        m.display_content, m.risk_rating = display_message, risk_rating
        m.save()
        return m
    except Message.DoesNotExist:
        print(
            f"message object with id {id}, display_content: {display_message} does not exist"
        )


def add_analysis(file):
    a, created = Analysis.objects.get_or_create(file=file)
    if not created:
        a.delete()
        a = Analysis.objects.create(file=file)
    a.save()
    return a


def add_person(analysis, name):
    p = Person.objects.get_or_create(analysis=analysis, name=name)[0]
    p.save()
    return p


def add_location(analysis, name):
    loc = Location.objects.get_or_create(analysis=analysis, name=name)[0]
    loc.save()
    return loc


def add_risk_word(analysis, keyword, amount, risk_factor=0):
    k = RiskWord.objects.filter(keyword=keyword).first()
    r = RiskWordResult.objects.get_or_create(
        analysis=analysis, riskword=k, amount=amount, risk_factor=risk_factor
    )[0]
    r.save()
    return r


def add_risk_word_result(analysis, keyword, amount, risk_factor=0):
    k = RiskWord.objects.filter(keyword=keyword).first()
    r = RiskWordResult.objects.get_or_create(
        analysis=analysis, riskword=k, amount=amount
    )[0]
    r.save()
    return r


def add_vis(analysis, file_path):
    v = VisFile.objects.get_or_create(analysis=analysis, file_path=file_path)[0]
    v.save()
    return v


def add_date(name, example, format, default):
    d = DateFormat.objects.get_or_create(
        name=name, example=example, format=format, is_default=default
    )[0]
    d.save()
    return d


def add_delim(name, order, value, is_default):
    delim = Delimiter.objects.get_or_create(
        name=name, order=order, value=value, is_default=is_default
    )[0]
    delim.save()
    return delim


def add_chat_message(type_of_message, content, convo):
    m = ChatGPTMessage.objects.create(
        typeOfMessage=type_of_message, content=content, convo=convo
    )
    m.save()
    return m


def add_chat_filter(content, typeOfFilter, convo):
    f = ChatGPTFilter.objects.create(typeOfFilter=typeOfFilter, content=content)
    f.save()
    fc = ChatGPTConvoFilter.objects.create(convo=convo, filter=f)
    fc.save()
    return f, fc


def add_custom_threshold(
    average_risk,
    sentiment_multiplier,
    max_risk,
    word_risk,
    strictness_level=2,
    sentiment_level=2,
):
    ct = CustomThresholds.objects.create(
        strictness_level=strictness_level,
        sentiment_level=sentiment_level,
        average_risk=average_risk,
        sentiment_multiplier=sentiment_multiplier,
        max_risk=max_risk,
        word_risk=word_risk,
    )
    ct.save()
    return ct


def add_gpt_switch():
    s = GptSwitch.objects.create()
    s.save()
    return s
