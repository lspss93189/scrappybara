# Quick start

> As easy as *1, 2, 3*

## Install Scrappybara

### Compatibility

Latest Scrappybara `v0.1.3` supports python 3.6-3.9.

### Pip install

Scrappybara is using Tensorflow v2 for machine learning.

Therefore you will need to install the current release of Tensorflow first:

```shell
pip install tensorflow
```

Then the current release of Scrappybara:

```shell
pip install scrappybara
```

### Download resources

The final step is to download data and deep-learning models:

```shell
python -m scrappybara download
```

### Optional step

To greatly increase performances when processing a large collection of texts, it is recommended to use a GPU.

Please refer to Tensorflow's documentation for installing a GPU:

* [TensorFlow GPU support](https://www.tensorflow.org/install/gpu)

### Try your first Scrappybara program 

```python
import scrappybara as sb

# Instantiate a pipeline (loads all necessary data in memory, might take few seconds)
pipe = sb.Pipeline()

# Process 2 texts
text_1 = "For the Chicago-based artist Nick Cave, trash is treasure. In his hands, the discarded detritus of everyday life becomes the foundational element of intricately layered artworks he calls Soundsuits."
text_2 = "The track is an aching piano ballad that finds Nick Cave grappling with loss, his lyrics visceral and blunt even as he keeps his piano playing and vocals soft and tender."

docs = pipe([text_1, text_2])

# Preview named-entities and their URI
print(docs[0].entities)
print(docs[1].entities)
```

And you should see 2 named-entities with their URI:
- `Nick Cave`: https://www.wikidata.org/wiki/Q24218
- `Nick Cave`: https://www.wikidata.org/wiki/Q192668  

As you can see, the first `Nick Cave` links to a performance artist, while the second `Nick Cave` links to a singer.

This example has illustrated the detection of named-entities and their disambiguation.
