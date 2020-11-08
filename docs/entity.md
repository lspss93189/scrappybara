# Entity

> Class: a named-entity that has been linked to an URI.

## Example

```python
import scrappybara as sb

pipe = sb.Pipeline()
docs = pipe(['I went to Seoul, South Korea.'])
for entity in docs[0].entities:
    print([entity.id, entity.uri, entity.form])
```

Output:

```terminal
[884, 'https://www.wikidata.org/wiki/Q884', 'South Korea]
[8684, 'https://www.wikidata.org/wiki/Q8684', 'Seoul']
```

## Properties

### form

`Entity.form`

Returns a string: the surface form found in the original text.

### id

`Entity.id` returns an integer: the wikidata ID.

### uri

`Entity.uri`

Returns a string: the Wikidata URI.
