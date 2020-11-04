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


def push_data():
    """Creates entitys' document sparse vectors"""
    timer = Timer()
    report_dir = cfg.REPORTS_DIR / 'create_vectors'
    data_dir = cfg.DATA_DIR / 'entities'
    prd_vars = {'total_docs': 0, 'total_counts': {}}  # to calculate vectors on production
    # Read lexemes
    print('Reading bags of lexemes...')
    bags_path = cfg.REPORTS_DIR / 'extract_lexeme_bags'
    lexeme_tf = collections.Counter()  # lexeme => term frequency (int)
    lexeme_df = collections.Counter()  # lexeme => document frequency (int)
    eid_lexbag = {}  # entity id => bag of lexemes
    total_docs = 0
    for file in files_in_dir(bags_path):
        for eid, lexbag in load_dict_from_txt_file(bags_path / file, key_type=int, value_type=eval).items():
            total_docs += 1
            eid_lexbag[eid] = lexbag
            for lexeme, count in lexbag:
                lexeme_tf[lexeme] += count
                lexeme_df[lexeme] += 1
    prd_vars['total_docs'] = total_docs
    print('{:,} lexemes extracted in {}'.format(len(lexeme_df), timer.lap_time))
    print()
    # Select features
    print('Selecting features...')
    select = FeatureSelector()
    feature_idx_df = {}  # feature => (idx, idf)
    for lexeme, df in lexeme_df.items():
        idx = select(lexeme, lexeme_tf[lexeme], df)
        if idx is not None:
            feature_idx_df[lexeme] = (idx, df)
    selected_lexemes_report = txt_file_writer(report_dir / 'accepted_lexemes.txt')
    rejected_lexemes_report = txt_file_writer(report_dir / 'rejected_lexemes.txt')
    for lexeme, df in [(lex, df) for lex, df in sorted(lexeme_df.items(), key=lambda x: x[1])]:
        line = '%s\t%d\t%.7f\n' % (lexeme, lexeme_tf[lexeme], math.log(total_docs / df))
        if lexeme in feature_idx_df:
            selected_lexemes_report.write(line)
        else:
            rejected_lexemes_report.write(line)
    save_pkl_file(feature_idx_df, data_dir / 'features.pkl')
    del lexeme_tf
    del lexeme_df
    print('{:,} features selected in {}'.format(len(feature_idx_df), timer.lap_time))
    print()
    # Create bags of features
    print('Creating bags of features...')
    eid_featbag = {}  # entity id => bag of features
    for eid, lexbag in eid_lexbag.items():
        featbag = {feature_idx_df[lexeme][0]: count for lexeme, count in lexbag if lexeme in feature_idx_df}
        if len(featbag):
            prd_vars['total_counts'][eid] = sum(featbag.values())
            eid_featbag[eid] = featbag
    save_pkl_file(eid_featbag, data_dir / 'bags.pkl')
    save_pkl_file(prd_vars, data_dir / 'vars.pkl')
    del feature_idx_df
    print('{:,} initial entities'.format(len(eid_lexbag)))
    del eid_lexbag
    print('{:,} vectors pushed to data in {}'.format(len(eid_featbag), timer.lap_time))
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
