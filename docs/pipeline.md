# Pipeline

> Class that processes texts into Documents.

## Example

```python
import scrappybara as sb

pipe = sb.Pipeline()
docs = pipe(['They visit the Louvre Museum in Paris, France.'])
print(docs[0].entities)
```

Output:

```terminal
[
    ('Louvre Museum', 'https://www.wikidata.org/wiki/Q19675'),
    ('Paris', 'https://www.wikidata.org/wiki/Q90'),
    ('France', 'https://www.wikidata.org/wiki/Q142')
]
```

## Constructor

`Pipeline(gpu_batch_size=-1)`

### Named arguments

Named argument | Type | Default | Description |
-- | -- | -- | --
`gpu_batch_size` | int | -1 | Size of batch that goes into deep-learning models when using the GPU. `-1` Means no GPU will be used.

To greatly increase speed, `gpu_batch_size` is the most important parameter. When processing a lot of texts, it's important to use the highest value possible. The value is limited by the GPU's available memory. 

Since Scrappybara is using TensorFlow for machine learning, you will need to follow these instructions in order to use your GPU:
* [TensorFlow GPU support](https://www.tensorflow.org/install/gpu)

## Magic methods

### \_\_call\_\_

`Pipeline(texts)`

Returns a list of [Documents](document.md) corresponding to the `texts` passed as an argument.

#### Call Arguments

Call argument | Type | Description
-- | -- | --
`texts` | list of strings | Texts to be processed.
