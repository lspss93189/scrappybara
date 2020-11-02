import json
import pathlib
import re

import scrappybara.config as cfg
from scrappybara.pipeline.toolkit_pipeline import LexemePipeline
from scrappybara.utils.files import files_in_dir, bz2_file_reader, load_dict_from_txt_file, txt_file_writer
from scrappybara.utils.mutables import reverse_dict
from scrappybara.utils.timer import Timer


class Tower(object):
    """Meant to use a single GPU"""

    __deletes = [
        re.compile(r'Section::::'),
        re.compile(r'BULLET::::'),
        re.compile(r'<onlyinclude></onlyinclude>'),
        re.compile(r'<br>'),
        re.compile(r'[a-z]+="[^"\s]+"'),
        re.compile(r'[a-z]+=[^"\s]+'),
    ]

    def __init__(self, resources_dir, gpu_id, batch_size):
        self.__data_path = pathlib.Path(resources_dir) / 'json'
        self.__report_path = cfg.REPORTS_DIR / 'extract_lexeme_bags' / ('ied_bag_%d.txt' % gpu_id)
        self.__pipe = LexemePipeline(batch_size)

    def __call__(self, filename, title_eid):
        """Extracts bag of lexemes & writes it in a report"""
        total_txts = 0
        with txt_file_writer(self.__report_path) as report:
            for batch in files_in_dir(self.__data_path / filename):
                for file in files_in_dir(self.__data_path / filename / batch):
                    texts = []
                    eids = []
                    with bz2_file_reader(self.__data_path / filename / batch / file) as data:
                        for line in data:
                            obj = json.loads(line)
                            title = obj['title']
                            # Only process texts that maps to an entity ID
                            if title in title_eid:
                                text = obj['text']
                                for d in self.__deletes:
                                    text = re.sub(d, '', text)
                                texts.append(text)
                                eids.append(title_eid[title])
                    bags = self.__pipe(texts)
                    for idx, bag in enumerate(bags):
                        report.write('%d\t%s\n' % (eids[idx], str(bag.most_common())))
                    total_txts += len(bags)
                    print('\r{:,}'.format(total_txts), end='')
        print('\n')
        return total_txts


def extract_lexeme_bags(resources_dir, nb_gpus, gpu_id, batch_size):
    """This process can be towered (one thread per GPU).
    Just indicate the total number of GPUs participating in the overall operation & the gpu_id for this tower.
    Towers (threads) are then run manually from CLI, one per GPU.
    Hint: don't forget to specify the visible GPU for one tower with "CUDA_VISIBLE_DEVICES=" in the environment.
    """
    # Parse args
    nb_gpus = int(nb_gpus)
    gpu_id = int(gpu_id)
    batch_size = int(batch_size)
    # Prep
    timer = Timer()
    re_filename = re.compile(r'enwiki-latest-pages-articles(\d+)\.xml-[p\d]+\.bz2')
    eid_title = load_dict_from_txt_file(cfg.REPORTS_DIR / 'extract_forms' / 'eid_title.txt', key_type=int)
    title_eid = reverse_dict(eid_title)
    process = Tower(resources_dir, gpu_id, batch_size)
    # Running tower
    print('Running tower %d...' % gpu_id)
    print()
    nb_texts_processed = 0
    for filename in [fn for fn in files_in_dir(resources_dir + '/dump') if fn.endswith('.bz2')]:
        file_match = re.fullmatch(re_filename, filename)
        file_nb = int(file_match.group(1))
        if file_nb % nb_gpus != gpu_id:
            continue
        print('Processing "%s"...' % filename)
        nb_texts_in_file = process(filename, title_eid)
        nb_texts_processed += nb_texts_in_file
        print('{:,} articles processed in {}'.format(nb_texts_in_file, timer.lap_time))
        print()
    print('Total: {:,} articles processed in {}'.format(nb_texts_processed, timer.total_time))
