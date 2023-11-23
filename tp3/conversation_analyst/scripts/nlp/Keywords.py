class Keywords:
    def __init__(self, dictionary=None):
        if dictionary is None:
            self.keywords = {}
        else:
            self.keywords = dictionary

    def add_keyword(self, key, topics, risk):
        key, topics =key.lower(), [s.lower() for s in topics]
        self.keywords[key] = {"risk":risk,"topics":topics}

    def remove_keyword(self, key):
        key =key.lower()
        if key.lower() in self.keywords:
            del self.keywords[key]
        else:
            print(f"The keyword '{key}' does not exist.")   
    def set_keywords_risk(self, key, risk):
        key, topic =key.lower(), topic.lower()
        if key in self.keywords:
            self.keywords[key]["risk"] = risk
        else:
            print(f"The keyword '{key}' does not exist.")
    def add_keywords_topic(self, key, topic):
        key, topic =key.lower(), topic.lower()
        if key in self.keywords:
            if topic not in self.keywords[key]["topic"]:
                self.keywords[key]["topic"].append(topic)
        else:
            print(f"The keyword '{key}' does not exist.")          
    def add_remove_topic(self, key, topic):
        key, topic =key.lower(), topic.lower()
        if key in self.keywords:
            if topic in self.keywords[key]["topic"]:
                self.keywords[key]["topic"].remove(topic)
            else:
                print(f"The topic '{topic}' does not exist.")
        else:
            print(f"The keyword '{key}' does not exist.")
    def get_keywords(self):
        return self.keywords
    def get_keyword(self, key):
        key =key.lower()
        if key in self.keywords:
            return self.keywords[key]
        else:
            print(f"The keyword '{key}' does not exist.")
    def get_keyword_risk(self, key):
        key =key.lower()
        if key in self.keywords:
            return self.keywords[key]["risk"]
        else:
            print(f"The keyword '{key}' does not exist.")     
    def get_keyword_topics(self, key):
        key =key.lower()
        if key in self.keywords:
            return self.keywords[key]["topics"]
        else:
            print(f"The keyword '{key}' does not exist.")