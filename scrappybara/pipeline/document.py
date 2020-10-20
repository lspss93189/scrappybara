class Document(object):
    """Output of pipeline"""

    def __init__(self, texts_entities):
        self.__texts_entities = texts_entities  # list of tuples (text, Entity)

    @property
    def entities(self):
        """Returns a list of tuple (original string from text, resource URI)"""
        return [(text, str(entity)) for text, entity in self.__texts_entities]
