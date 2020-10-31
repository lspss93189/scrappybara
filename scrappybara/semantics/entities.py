class Entity(object):
    __uri_start = 'https://www.wikidata.org/wiki/Q'

    def __init__(self, entity_ids, form):
        self.eids = entity_ids
        self.form = form
        self.start_idx = None
        self.end_idx = None
        self.uri = None

    def __repr__(self):
        return self.form

    def __str__(self):
        return self.form

    @property
    def boundaries(self):
        return self.start_idx, self.end_idx
