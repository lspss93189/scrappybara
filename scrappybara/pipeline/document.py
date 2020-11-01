class Document(object):
    """Output of pipeline"""

    def __init__(self, sentences):
        self.sentences = sentences

    @property
    def entities(self):
        return [entity for sent in self.sentences for entity in sent.entities]
