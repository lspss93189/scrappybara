import bottle

from scrappybara.pipeline.parsing_pipeline import ParsingPipeline
from scrappybara.syntax.dependencies import Dep

_PIPE = ParsingPipeline()


def _make_node(token, tag, dep, pidx):
    return {'token': token, 'tag': tag.name, 'dep': dep.name, 'parent': pidx}


@bottle.post('/parse')
def api_parse():
    """Parses raw sentence.
    Input: {"sentence": str or [str, ...]}
    Output: {"nodes": [{"token": str, "tag": str, "dep": str, "parent": int}, ...]}
    """
    body = bottle.request.json
    tokens, tags, tree, node_dict = _PIPE(body['sentence'])
    if tree is None:
        return {'nodes': []}
    nodes = []
    for idx, token in enumerate(tokens):
        tag = tags[idx]
        if idx == tree.root:
            nodes.append(_make_node(token, tag, Dep.ROOT, -1))
        else:
            dep_parent = tree.parent(idx)
            if dep_parent is None:
                nodes.append(_make_node(token, tag, Dep.NODEP, -1))
            else:
                dep, parent = dep_parent
                nodes.append(_make_node(token, tag, dep, parent))
    return {'nodes': nodes}


if __name__ == '__main__':
    bottle.run(port=8000)
