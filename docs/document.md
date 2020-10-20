# Document

> Class that represents an output of the Pipeline.

## Example

```python
import scrappybara as sb

pipe = sb.Pipeline()
docs = pipe(['I went to Seoul, South Korea.'])
print(docs[0].entities)
```

Output:

```terminal
[
    ('South Korea', 'https://www.wikidata.org/wiki/Q884'),
    ('Seoul', 'https://www.wikidata.org/wiki/Q8684')
]
```

## Properties

### entities

`Document.entities`

Returns a list of tuples (named-entity as found in the original text, URI).

The list is the consolidation of all named-entities found in the document, in the same order.
