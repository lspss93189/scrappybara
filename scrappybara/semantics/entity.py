class Entity(object):

    def __init__(self, entity_id, form):
        self.eid = entity_id
        self.form = form
        self.uri = 'https://www.wikidata.org/wiki/Q%d' % entity_id

    def __repr__(self):
        return repr((self.form, self.uri))

    def __str__(self):
        return str((self.form, self.uri))
