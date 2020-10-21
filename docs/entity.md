# Entity

> Class that represents a named-entity.

## Example

```python
import scrappybara as sb

pipe = sb.Pipeline()
docs = pipe(['I went to Seoul, South Korea.'])
for entity in docs[0].entities:
    print([entity.id, entity.uri, entity.form, entity.start_idx, entity.end_idx])
```

Output:

```terminal
[884, 'https://www.wikidata.org/wiki/Q884', 'South Korea', 17, 28]
[8684, 'https://www.wikidata.org/wiki/Q8684', 'Seoul', 10, 15]
```

## Properties

### end_idx

`Entity.end_idx`

Returns an integer: the exclusive end-index of the entity's form in the original text.

### form

`Entity.form`

Returns a string: the surface form found in the original text.

### id

`Entity.id` returns an integer: the wikidata ID.

### start_idx

`Entity.start_idx`

Returns an integer: the inclusive start-index of the entity's form in the original text.

### uri

`Entity.uri`

Returns a string: the Wikidata URI.
