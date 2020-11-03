import collections
import math
import re

import scrappybara.config as cfg
from scrappybara.utils.files import load_dict_from_txt_file, txt_file_writer, save_pkl_file, txt_file_reader, \
    files_in_dir
from scrappybara.utils.mutables import reverse_dict
from scrappybara.utils.timer import Timer


class FeatureSelector(object):
    __min_count = 2
    __min_idf = 2.

    __re_rejects = [
        re.compile(r'https?://'),
    ]

    def __init__(self):
        self.__feature_idx = -1  # feature idx

    def __call__(self, lexeme, count, idf):
        """Returns feature & its idx if lexeme is selected, None otherwise"""
        if count < self.__min_count:
            return None
        if idf < self.__min_idf:
            return None
        if any([re.findall(pattern, lexeme) for pattern in self.__re_rejects]):
            return None
        self.__feature_idx += 1
        return self.__feature_idx


def create_vectors():
    """Creates entitys' document sparse vectors"""
    timer = Timer()
    report_dir = cfg.REPORTS_DIR / 'create_vectors'
    data_dir = cfg.DATA_DIR / 'entities'
    # Read lexemes
    print('Reading lexemes from bags...')
    bags_path = cfg.REPORTS_DIR / 'extract_lexeme_bags'
    lexeme_total_count = collections.Counter()  # lexeme => total count
    lexeme_nb_docs = collections.Counter()  # lexeme => nb docs
    eid_bag = {}  # entity id => bag of lexemes
    total_docs = 0
    for file in files_in_dir(bags_path):
        for eid, bag in load_dict_from_txt_file(bags_path / file, key_type=int, value_type=eval).items():
            total_docs += 1
            eid_bag[eid] = bag
            for lexeme, count in bag:
                lexeme_total_count[lexeme] += count
                lexeme_nb_docs[lexeme] += 1
    print('{:,} lexemes extracted in {}'.format(len(lexeme_nb_docs), timer.lap_time))
    print()
    # Calculate IDF scores
    print('Calculating IDF scores...')
    lexeme_idf = {lexeme: math.log(total_docs / nb_docs) for lexeme, nb_docs in lexeme_nb_docs.items()}
    print('All IDF scores calculated in {}'.format(timer.lap_time))
    print()
    # Select features
    print('Selecting features...')
    select = FeatureSelector()
    feature_idx_idf = {}  # feature => (idx, idf)
    for lexeme, idf in lexeme_idf.items():
        idx = select(lexeme, lexeme_total_count[lexeme], idf)
        if idx is not None:
            feature_idx_idf[lexeme] = (idx, idf)
    selected_lexemes_report = txt_file_writer(report_dir / 'accepted_lexemes.txt')
    rejected_lexemes_report = txt_file_writer(report_dir / 'rejected_lexemes.txt')
    for lexeme, idf in [(lex, idf) for lex, idf in sorted(lexeme_idf.items(), key=lambda x: x[1])]:
        line = '%s\t%d\t%.7f\n' % (lexeme, lexeme_total_count[lexeme], idf)
        if lexeme in feature_idx_idf:
            selected_lexemes_report.write(line)
        else:
            rejected_lexemes_report.write(line)
    save_pkl_file(feature_idx_idf, data_dir / 'feature_idx_idf.pkl')
    del lexeme_nb_docs
    del lexeme_total_count
    del lexeme_idf
    print('{:,} features selected in {}'.format(len(feature_idx_idf), timer.lap_time))
    print()
    # Create sparse vectors
    print('Calculating vectors...')
    eid_vector = {}  # entity id => sparse vector
    for eid, bag in eid_bag.items():
        new_bag = [(lexeme, count) for lexeme, count in bag if lexeme in feature_idx_idf]
        doc_total_count = sum([count for _, count in new_bag])
        vector = {}  # feature idx => tf.idf
        for lexeme, count in new_bag:
            idx, idf = feature_idx_idf[lexeme]
            vector[idx] = (count / doc_total_count) * idf
        if len(vector):
            eid_vector[eid] = vector
    save_pkl_file(eid_vector, data_dir / 'eid_vector.pkl')
    del feature_idx_idf
    print('{:,} initial entities'.format(len(eid_bag)))
    del eid_bag
    print('{:,} vectors pushed to data in {}'.format(len(eid_vector), timer.lap_time))
    print()
    # Clean forms
    print('Cleaning forms...')
    eid_title = load_dict_from_txt_file(cfg.REPORTS_DIR / 'extract_forms' / 'eid_title.txt', key_type=int)
    title_eid = reverse_dict(eid_title)
    form_eids = {}  # form => set of entity IDs
    initial_nb_forms = 0
    with txt_file_reader(cfg.REPORTS_DIR / 'extract_forms' / 'form_titles.txt') as report:
        for line in report:
            initial_nb_forms += 1
            form, _, titles = line.strip().split('\t')
            titles = eval(titles)
            eids = {title_eid[title] for title in titles if title_eid[title] in eid_vector}
            if len(eids):
                form_eids[form] = eids
    save_pkl_file(form_eids, data_dir / 'form_eids.pkl')
    print('{:,} initial forms'.format(initial_nb_forms))
    print('{:,} forms pushed to data in {}'.format(len(form_eids), timer.lap_time))
    # All done
    print('All done in {}'.format(timer.total_time))
