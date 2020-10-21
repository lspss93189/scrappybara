class Resource(object):

    def __init__(self, uri):
        self.__uri = uri

    def __str__(self):
        return self.__uri

    def __repr__(self):
        return self.__uri


class Entity(Resource):

    def __init__(self, entity_id, form, start_idx, end_idx):
        self.uri = 'https://www.wikidata.org/wiki/Q%d' % entity_id
        super().__init__(self.uri)
        self.id = entity_id
        self.form = form
        self.start_idx = start_idx
        self.end_idx = end_idx

    def __repr__(self):
        return repr((self.boundaries, self.form, self.uri))

    @property
    def boundaries(self):
        return self.start_idx, self.end_idx
