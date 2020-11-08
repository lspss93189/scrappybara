import collections
import math
import re

import scrappybara.config as cfg
from scrappybara.exceptions import DestinationFolderNotEmtpyError
from scrappybara.utils.files import load_dict_from_txt_file, txt_file_writer, save_pkl_file, txt_file_reader, \
    files_in_dir, path_exists
from scrappybara.utils.logger import Logger
from scrappybara.utils.mutables import reverse_dict
from scrappybara.utils.timer import Timer


class FeatureSelector(object):
    __min_tc = 2  # minimum term's total count
    __min_idf = 1.  # minimum term's inverse document frequency

    # Accepted features
    __re_accepted = [
        re.compile(r'[a-z0-9\-_]+'),  # e.g. "house", "iphone9s", "covid-19", "formula_1"
        re.compile(r'[a-z]+&[a-z]+'),  # e.g. "r&b"
        re.compile(r'[a-z]\++'),  # e.g. "canal+"
        re.compile(r'[a-z\']+'),  # e.g. "o'brien"
        re.compile(r'([a-z]\.){2,}'),  # e.g. "u.s."
    ]

    # Rejected features (tests done after __re_accepted)
    __re_rejected = [
        re.compile(r'[\d&\'.\-_].+'),  # Anything starting with a specific character
        re.compile(r'[a-z]+\.'),  # e.g. "mr."
    ]

    __stopwords = set("""
    
        be become have do
        
        of the a
        
        external link
        
        i ii iii iv v vi vii viii ix x
        
        monday tuesday wednesday thursday friday saturday sunday
        january february march april may june july august september october november december
        
        e.g. i.e. a.m. p.m.

    """.split())

    def __init__(self):
        self.__feature_idx = -1  # feature idx

    def __call__(self, lexeme, tc, idf):
        """Returns feature & its idx if lexeme is selected, None otherwise"""
        if not lexeme:
            return None
        if tc < self.__min_tc:
            return None
        if idf < self.__min_idf:
            return None
        if lexeme in self.__stopwords:
            return None
        if not any([re.fullmatch(accepted, lexeme) for accepted in self.__re_accepted]):
            return None
        if any([re.fullmatch(rejected, lexeme) for rejected in self.__re_rejected]):
            return None
        self.__feature_idx += 1
        return self.__feature_idx


def push_el_data(min_features, max_features):
    """Pushes all resources necessary for entity-linking to data.
    First step "READ LEXEMES" saves its results: delete the report if you want to run it again.
    Entities with less features than "min_features" are discarded.
    Entities with more features than "max_features" retain their best features only.
    """
    Logger.info('PUSH ENTITY-LINKER DATA: min_features={}, max_features={}'.format(min_features, max_features))
    # Parse args
    min_features = int(min_features)
    max_features = int(max_features)
    # Prep
    bags_path = cfg.REPORTS_DIR / 'extract_bags'
    reports_dir = cfg.REPORTS_DIR / 'push_data'
    data_dir = cfg.DATA_DIR / 'entities'
    if len(files_in_dir(data_dir)):
        raise DestinationFolderNotEmtpyError(data_dir)
    timer = Timer()
    prd_vars = {'total_docs': 0}  # constants needed to calculate vectors on production

    # READ BAGS OF LEXEMES
    # -------------------------------------------------------------------------->

    report_file = 'lexeme_tc_dc.txt'
    report_total = 'total_docs.txt'

    if path_exists(reports_dir / report_file):
        # Load counts
        lexeme_tc = {}
        lexeme_dc = {}
        with txt_file_reader(reports_dir / report_total) as report:
            total_docs = int(report.read())
        with txt_file_reader(reports_dir / report_file) as report:
            for line in report:
                try:
                    lexeme, tc, dc = line.strip().split('\t')
                    lexeme_tc[lexeme] = int(tc)
                    lexeme_dc[lexeme] = int(dc)
                except ValueError:
                    continue
        Logger.info('{:,} lexemes loaded from "{}" in {}'.format(len(lexeme_dc), report_file, timer.lap_time))
    else:
        # Count lexemes
        lexeme_tc = collections.Counter()  # lexeme => term total count
        lexeme_dc = collections.Counter()  # lexeme => term document count (int)
        total_docs = 0
        for file in files_in_dir(bags_path):
            for eid, lexbag in load_dict_from_txt_file(bags_path / file, key_type=int, value_type=eval).items():
                total_docs += 1
                for lexeme, count in lexbag:
                    lexeme_tc[lexeme] += count
                    lexeme_dc[lexeme] += 1
        # Write reports
        with txt_file_writer(reports_dir / report_file) as report:
            for lexeme, tc in sorted(lexeme_tc.items(), key=lambda x: x[0]):
                report.write('%s\t%d\t%d\n' % (lexeme, tc, lexeme_dc[lexeme]))
        with txt_file_writer(reports_dir / report_total) as report:
            report.write('%d' % total_docs)
        Logger.info('{:,} lexemes extracted in {}'.format(len(lexeme_dc), timer.lap_time))
    prd_vars['total_docs'] = total_docs
    save_pkl_file(prd_vars, data_dir / 'vars.pkl')

    # SELECT FEATURES
    # -------------------------------------------------------------------------->

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
    Logger.info('{:,} features selected in {}'.format(len(feature_idx_dc), timer.lap_time))

    # CREATE BAG OF FEATURES
    # -------------------------------------------------------------------------->

    eid_featbag = {}  # entity id => bag of features
    for file in files_in_dir(bags_path):
        for eid, lexbag in load_dict_from_txt_file(bags_path / file, key_type=int, value_type=eval).items():
            featbag = [(lex, feature_idx_dc[lex][0], count) for lex, count in lexbag if lex in feature_idx_dc]
            if len(featbag) >= min_features:
                if len(featbag) > max_features:
                    # Prune features
                    total_count = sum([count for _, _, count in featbag])
                    idx_count_tfidf = [(idx, count, (count / total_count) * lexeme_idf[lex]) for lex, idx, count in
                                       featbag]
                    eid_featbag[eid] = [(idx, count) for idx, count, _ in
                                        sorted(idx_count_tfidf, key=lambda x: x[2], reverse=True)[:max_features]]
                else:
                    eid_featbag[eid] = [(idx, count) for _, idx, count in featbag]
    save_pkl_file(eid_featbag, data_dir / 'bags.pkl')
    del lexeme_idf
    del feature_idx_dc
    Logger.info('{:,} initial number of entities'.format(total_docs))
    Logger.info('{:,} entities pushed to data in {}'.format(len(eid_featbag), timer.lap_time))

    # CLEAN FORMS
    # -------------------------------------------------------------------------->

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
    Logger.info('{:,} initial forms'.format(initial_nb_forms))
    Logger.info('{:,} forms pushed to data in {}'.format(len(form_eids), timer.lap_time))

    # ALL DONE
    # -------------------------------------------------------------------------->

    Logger.info('Total time: {}'.format(timer.total_time))
