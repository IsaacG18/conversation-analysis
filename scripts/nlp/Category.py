import spacy

nlp = spacy.load("en_core_web_sm")

def extract(text, label):
    found = []
    doc = nlp(text)
    for entity in doc.ents:
        if entity.label_ == label:
            found.append(entity.text)
    return found