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
    ((17, 28), 'South Korea', 'https://www.wikidata.org/wiki/Q884'),
    ((10, 15), 'Seoul', 'https://www.wikidata.org/wiki/Q8684')
]
```

## Properties

### entities

`Document.entities`

Returns a list of [Entities](entity.md): all named-entities found in the document.
