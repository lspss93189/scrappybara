import json
import pathlib

import scrappybara.config as cfg
from scrappybara.utils.files import bz2_file_reader, txt_file_writer
from scrappybara.utils.timer import Timer


def extract_items(resource_dir):
    """Extracts Wikidata items that have an English Wikipedia page"""
    print('Extracting items...')
    timer = Timer()
    items = []
    with bz2_file_reader(pathlib.Path(resource_dir) / 'latest-all.json.bz2') as bz2_file:
        properties = {'P31': 'instance_of', 'P279': 'subclass_of', 'P1709': 'equivalent_class'}
        for line in bz2_file:
            line = line.strip()
            if line.startswith('{') and line.endswith('},'):
                item = json.loads(line[:-1])
                # Guards
                if item['type'] != 'item':
                    continue
                if 'enwiki' not in item['sitelinks']:
                    continue
                # Optional fields
                if 'en' in item['descriptions']:
                    description = item['descriptions']['en']['value']
                else:
                    description = None
                if 'en' in item['labels']:
                    label = item['labels']['en']['value']
                else:
                    label = None
                aliases = []  # list of strings
                if 'en' in item['aliases']:
                    for alias in item['aliases']['en']:
                        aliases.append(alias['value'])
                # Build new dictionary
                small_item = {'id': int(item['id'][1:]), 'title': item['sitelinks']['enwiki']['title'],
                              'label': label, 'description': description, 'aliases': aliases}
                # Attach properties
                props = {code: {'preferred': [], 'normal': [], 'deprecated': []} for code in properties.keys()}
                for code in [p for p in properties.keys() if p in item['claims']]:
                    for claim in item['claims'][code]:
                        try:
                            props[code][claim['rank']].append(claim['mainsnak']['datavalue']['value']['numeric-id'])
                        except KeyError:
                            continue
                for code, prop in properties.items():
                    small_item[prop] = props[code]
                # Make json string
                items.append(json.dumps(small_item))
                if len(items) % 100 == 0:
                    print('\r{:,}'.format(len(items)), end='')
    with txt_file_writer(cfg.HOME_DIR / 'reports' / 'extract_items' / 'items.txt') as report:
        for item in items:
            report.write('%s\n' % item)
    print('\n')
    print('{:,} items extracted in {}'.format(len(items), timer.total_time))
