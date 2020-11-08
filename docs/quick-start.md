# Quick start

> As easy as *1, 2, 3*

## Install Scrappybara

### Compatibility

Latest Scrappybara `v0.2.0` supports python 3.6-3.9.

### Pip install

Scrappybara is using Tensorflow `v2.3+` for machine learning.

Therefore you will need to install the current release of Tensorflow first:

```shell
pip3 install tensorflow
```

Check the version of Tensorflow:
 
```shell
pip3 show tensorflow
```

The first 2 lines should give you enough details. For example:

```Shell
Name: tensorflow
Version: 2.3.1
```

You're now ready to install the current release of Scrappybara:

```shell
pip3 install scrappybara
```

### Download resources

The final step is to download the data:

```shell
python3 -m scrappybara download core
```

If you have a computer with at least 64Gb memory, you can instead download the full version:

```shell
python3 -m scrappybara download full
```

Differences between `core` and `full` datasets:

Bundle | Entity Linking
-- | -- |
`core` | **5,613,024** forms linked to **1,545,603** URIs
`full` | 1,545,603


### Optional step

To greatly increase performance when processing a large collection of texts, it is recommended to use a GPU.

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

And you should see 2 named-entities with their boundaries and URI:
- `Nick Cave`, https://www.wikidata.org/wiki/Q24218
- `Nick Cave`, https://www.wikidata.org/wiki/Q192668

As you can see, the first `Nick Cave` links to the performance artist, while the second `Nick Cave` links to the singer.

This example has illustrated the detection of named-entities and their disambiguation.
