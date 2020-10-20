class Resource(object):

    def __init__(self, uri):
        self.__uri = uri

    def __str__(self):
        return self.__uri

    def __repr__(self):
        return self.__uri


class Entity(Resource):

    def __init__(self, entity_id):
        super().__init__('https://www.wikidata.org/wiki/Q%d' % entity_id)
        self.id = entity_id
