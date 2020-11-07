import collections

import scrappybara.config as cfg
from scrappybara.utils.files import load_dict_from_txt_file, txt_file_writer, files_in_dir
from scrappybara.utils.timer import Timer


def extract_lexemes():
    """Reads bag of lexemes"""
    bags_path = cfg.REPORTS_DIR / 'extract_bags'
    reports_dir = cfg.REPORTS_DIR / 'extract_lexemes'
    timer = Timer()
    report_file = 'lexeme_tc_dc.txt'
    report_total = 'total_docs.txt'
    print('Reading bags of lexemes...')
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
    print('{:,} lexemes extracted in {}'.format(len(lexeme_dc), timer.lap_time))
    print()
    print('All done in {}'.format(timer.total_time))
