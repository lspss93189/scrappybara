import collections
import math
import re

import scrappybara.config as cfg
from scrappybara.exceptions import DestinationFolderNotEmtpyError
from scrappybara.utils.files import load_dict_from_txt_file, txt_file_writer, save_pkl_file, txt_file_reader, \
    files_in_dir
from scrappybara.utils.mutables import reverse_dict
from scrappybara.utils.timer import Timer


class FeatureSelector(object):
    __min_tc = 2  # minimum term's total count
    __min_idf = 2.  # minimum term's inverse document frequency

    __re_rejects = [
        re.compile(r'https?://'),
    ]

    def __init__(self):
        self.__feature_idx = -1  # feature idx

    def __call__(self, lexeme, tc, idf):
        """Returns feature & its idx if lexeme is selected, None otherwise"""
        if tc < self.__min_tc:
            return None
        if idf < self.__min_idf:
            return None
        if any([re.findall(pattern, lexeme) for pattern in self.__re_rejects]):
            return None
        self.__feature_idx += 1
        return self.__feature_idx


def push_data():
    """Creates entitys' document sparse vectors"""
    reports_dir = cfg.REPORTS_DIR / 'push_data'
    data_dir = cfg.DATA_DIR / 'entities'
    if len(files_in_dir(data_dir)):
        raise DestinationFolderNotEmtpyError(data_dir)
    timer = Timer()
    prd_vars = {'total_docs': 0}  # constants needed to calculate vectors on production
    # Read lexemes
    print('Reading bags of lexemes...')
    bags_path = cfg.REPORTS_DIR / 'extract_lexeme_bags'
    lexeme_tc = collections.Counter()  # lexeme => term total count
    lexeme_dc = collections.Counter()  # lexeme => term document count (int)
    total_docs = 0
    for file in files_in_dir(bags_path):
        for eid, lexbag in load_dict_from_txt_file(bags_path / file, key_type=int, value_type=eval).items():
            total_docs += 1
            for lexeme, count in lexbag:
                lexeme_tc[lexeme] += count
                lexeme_dc[lexeme] += 1
    prd_vars['total_docs'] = total_docs
    print('{:,} lexemes extracted in {}'.format(len(lexeme_dc), timer.lap_time))
    print()
    # Select features
    print('Selecting features...')
    select = FeatureSelector()
    feature_idx_dc = {}  # feature => (idx, idf)
    lexeme_idf = {}  # lexeme => inverse document frequency
    for lexeme, dc in lexeme_dc.items():
        lexeme_idf[lexeme] = math.log(total_docs / dc)
        idx = select(lexeme, lexeme_tc[lexeme], lexeme_idf[lexeme])
        if idx is not None:
            feature_idx_dc[lexeme] = (idx, dc)
    selected_lexemes_report = txt_file_writer(reports_dir / 'accepted_lexemes.txt')
    rejected_lexemes_report = txt_file_writer(reports_dir / 'rejected_lexemes.txt')
    for lexeme, dc in [(lex, df) for lex, df in sorted(lexeme_dc.items(), key=lambda x: x[1], reverse=True)]:
        line = '%s\t%d\t%.7f\n' % (lexeme, lexeme_tc[lexeme], lexeme_idf[lexeme])
        if lexeme in feature_idx_dc:
            selected_lexemes_report.write(line)
        else:
            rejected_lexemes_report.write(line)
    save_pkl_file([(feature, idx_dc[1]) for feature, idx_dc in sorted(feature_idx_dc.items(), key=lambda x: x[1][0])],
                  data_dir / 'features.pkl')
    del lexeme_tc
    del lexeme_dc
    del lexeme_idf
    print('{:,} features selected in {}'.format(len(feature_idx_dc), timer.lap_time))
    print()
    # Create bags of features
    print('Creating bags of features...')
    eid_featbag = {}  # entity id => (total count of document, bag of features)
    for file in files_in_dir(bags_path):
        for eid, lexbag in load_dict_from_txt_file(bags_path / file, key_type=int, value_type=eval).items():
            featbag = {feature_idx_dc[lexeme][0]: count for lexeme, count in lexbag if lexeme in feature_idx_dc}
            if len(featbag):
                eid_featbag[eid] = featbag
    save_pkl_file(eid_featbag, data_dir / 'bags.pkl')
    save_pkl_file(prd_vars, data_dir / 'vars.pkl')
    del feature_idx_dc
    print('{:,} initial number of entities'.format(total_docs))
    print('{:,} entities with features pushed to data in {}'.format(len(eid_featbag), timer.lap_time))
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
            eids = {title_eid[title] for title in titles if title_eid[title] in eid_featbag}
            if len(eids):
                form_eids[form] = eids
    save_pkl_file(form_eids, data_dir / 'forms.pkl')
    print('{:,} initial forms'.format(initial_nb_forms))
    print('{:,} forms pushed to data in {}'.format(len(form_eids), timer.lap_time))
    # All done
    print('All done in {}'.format(timer.total_time))
