import json
import pathlib

import scrappybara.config as cfg
from scrappybara.pipeline.pipeline import Pipeline
from scrappybara.utils.files import txt_file_reader


def test_entity_linking(data_dir):
    """Run benchmarks for Entity Linking using T-REx dataset"""
    reports_dir = cfg.REPORTS_DIR / 'test_entity_linking'
    pipe = Pipeline()

    with txt_file_reader(pathlib.Path(data_dir) / 're-nlg_0-10000.json') as data:
        batch = json.load(data)
        for sample in batch:
            # text = sample['text']
            text = 'The Austroasiatic languages, in recent classifications synonymous with Mon-Khmer, are a large language family of continental Southeast Asia, also scattered throughout India, Bangladesh, Nepal and the southern border of China.'
            # uri: "http://www.wikidata.org/entity/Q33199"
            entities = sample['entities']  # list of dict {boundaries: [int, int], surfaceform: str, uri: str}
            doc = pipe([text])[0]
            print(text)
            print()
            # print(sorted([entity['surfaceform'] for entity in sorted(entities, key=lambda x: x['boundaries'][0])]))
            # print()
            print(doc.entities)
            break


test_entity_linking('/media/data/trex')
