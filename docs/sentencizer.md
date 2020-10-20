# Sentencizer

> Method that tokenizes text and groups tokens by sentence.

## Example

```python
import scrappybara as sb

sentencize = sb.Sentencizer()
tokens = sentencize("I cannot sing Mr. Smith's song. It is jargon!")
print(tokens)
```

Output:

```terminal
[
    ['I', 'can', 'not', 'sing', 'Mr.', 'Smith', "'s", 'song', '.'],
    ['It', 'is', 'jargon', '!']
]
```

## Constructor

`Sentencizer()`

## Magic methods

### \_\_call\_\_

`Sentencizer(text)`

Returns a list of list of strings: tokens grouped by sentence.

## Call arguments

Call argument | Type | Description
-- | -- | --
**text** | string | Text to sentencize.
