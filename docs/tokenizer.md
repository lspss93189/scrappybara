# Tokenizer

> Method that tokenizes text.

## Example

```python
import scrappybara as sb

tokenize = sb.Tokenizer()
tokens = tokenize("I cannot sing Mr. Smith's song. It is jargon!")
print(tokens)
```

Output:

```terminal
['I', 'can', 'not', 'sing', 'Mr.', 'Smith', "'s", 'song', '.', 'It', 'is', 'jargon', '!']
```

This method does not split sentences. You can compare the difference with the [Sentencizer's output](sentencizer.md#example) with the same example.

## Constructor

`Tokenizer()`

## Magic methods

### \_\_call\_\_

`Tokenizer(text)`

Returns a list of strings: the tokens.

## Call arguments

Call argument | Type | Description
-- | -- | --
**text** | string | Text to tokenize.
