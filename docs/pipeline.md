# Pipeline

> Class: factory that processes texts into Documents.

## Example

```python
import scrappybara as sb

pipe = sb.Pipeline()
docs = pipe(['They visited the Louvre Museum in Paris.'])
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
`batch_size` | int | 128 | Size of batch that goes into deep-learning models.

To greatly increase speed, try to find the highest `batch_size` possible while using a GPU: it's limited by the GPU's memory. 

You will need to follow these instructions in order to install your GPU for Tensorflow:
* [TensorFlow GPU support](https://www.tensorflow.org/install/gpu)

If no GPU is available, you can just use the default `batch_size`.

## Magic methods

### \_\_call\_\_

`Pipeline(texts)`

Returns a list of [Documents](document.md) corresponding to the `texts`.

#### Call Arguments

Call argument | Type | Description
-- | -- | --
`texts` | list of strings | Texts to be processed.
