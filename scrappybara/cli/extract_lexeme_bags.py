import json
import pathlib
import re

import scrappybara.config as cfg
from scrappybara.pipeline.toolkit_pipeline import LexemePipeline
from scrappybara.utils.files import files_in_dir, bz2_file_reader, load_dict_from_txt_file, txt_file_writer, path_exists
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

    def __init__(self, resources_dir, batch_size):
        self.__pipe = LexemePipeline(batch_size)
        self.__data_path = pathlib.Path(resources_dir) / 'json'
        self.__processed_eids = set()

    def __call__(self, filename, title_eid):
        """Extracts bag of lexemes & writes it in a report.
        If the process crashed, don't forget to delete incomplete reports prior to run this.
        Incomplete reports are the last edited (one per tower).
        """
        total_txts = 0
        report_path = cfg.REPORTS_DIR / 'extract_lexeme_bags' / (filename[:-4] + '.txt')
        if not path_exists(report_path):
            with txt_file_writer(report_path) as report:
                for batch in files_in_dir(self.__data_path / filename):
                    for file in files_in_dir(self.__data_path / filename / batch):
                        texts = []
                        eids = []
                        with bz2_file_reader(self.__data_path / filename / batch / file) as data:
                            for line in data:
                                obj = json.loads(line)
                                title = obj['title']
                                # Only process texts that maps to an entity ID
                                if title in title_eid and title_eid[title]:
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
        return total_txts


def extract_lexeme_bags(resources_dir, tower_id, nb_towers, batch_size):
    """This process can be towered (one tower per GPU).
    Just indicate the total number of GPUs participating in the overall operation & the gpu_id for this tower.
    Towers (threads) are then run manually from CLI, one per GPU.
    Hint: don't forget to specify the visible GPU for one tower with "CUDA_VISIBLE_DEVICES=" in the environment.
    """
    # Parse args
    tower_id = int(tower_id)
    nb_towers = int(nb_towers)
    batch_size = int(batch_size)
    # Prep
    timer = Timer()
    re_filename = re.compile(r'enwiki-latest-pages-articles(\d+)\.xml-[p\d]+\.bz2')
    eid_title = load_dict_from_txt_file(cfg.REPORTS_DIR / 'extract_forms' / 'eid_title.txt', key_type=int)
    title_eid = reverse_dict(eid_title)
    process = Tower(resources_dir, batch_size)
    # Running tower
    print('Running tower %d...' % tower_id)
    print()
    nb_texts_processed = 0
    for filename in [fn for fn in files_in_dir(resources_dir + '/dump') if fn.endswith('.bz2')]:
        file_match = re.fullmatch(re_filename, filename)
        file_nb = int(file_match.group(1))
        if file_nb % nb_towers != tower_id:
            continue
        print('Processing "%s"...' % filename)
        nb_texts_processed_in_file = process(filename, title_eid)
        if nb_texts_processed_in_file:
            nb_texts_processed += nb_texts_processed_in_file
            print()
            print('Batch processed in {}'.format(timer.lap_time))
        else:
            print('File found: skiping')
        print()
    print('Total: {:,} articles processed in {}'.format(nb_texts_processed, timer.total_time))
