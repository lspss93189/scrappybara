import json
import multiprocessing
import pathlib
import re

from lxml import etree

import scrappybara.config as cfg
from scrappybara.preprocessing.tokenizer import Tokenizer
from scrappybara.utils.files import bz2_file_bytes_reader, files_in_dir, load_set_from_txt_file, \
    load_dict_from_txt_file, txt_file_writer, txt_file_reader, path_exists
from scrappybara.utils.logger import Logger
from scrappybara.utils.mutables import add_in_dict_set, reverse_dict
from scrappybara.utils.timer import Timer


def _valid_page(title):
    avoid_pages = ['Wikipedia:', 'Portal:', 'Category:', 'Template:', 'File:', 'Module:', 'MediaWiki:', 'Book:',
                   'Draft:', 'List of']
    if not title:
        return False
    if any([title.startswith(avoid_page) for avoid_page in avoid_pages]):
        return False
    return True


def _page_is_disamb(title, text):
    if not text:
        return False
    re_disamb = re.compile(r'{{[^()]*?Disambiguation[^()]*?}}', re.I)
    return title.endswith('(disambiguation)') or re.findall(re_disamb, text)


def _valid_token(token):
    return token not in {"'", '"', ',', ';', ':', '(', ')', '-', '_', '[', ']', '{', '}', '.', '..', '...'}


def _convert_to_form(cand):
    tokenize = Tokenizer()
    return ' '.join([token.lower() for token in tokenize(cand) if _valid_token(token)])


def _extract_article(elem):
    """Extract article data from an Wikipedia XML tree Element"""
    title = None
    redirect = None
    text = None
    if elem.tag.endswith('}page'):
        for child in elem:
            if child.tag.endswith('}title'):
                if child.text:
                    title = child.text.strip()
            elif child.tag.endswith('}redirect'):
                if child.get('title'):
                    redirect = child.get('title').strip()
            elif child.tag.endswith('}revision'):
                for gchild in child:
                    if gchild.tag.endswith('}text'):
                        if gchild.text:
                            text = gchild.text.strip()
    return title, redirect, text


# ###############################################################################
# MULTIPROCESSING
# ###############################################################################


def _extract_titles(filepath):
    """Extract valid titles from wikipedia articles"""
    titles = []
    with bz2_file_bytes_reader(filepath) as data:
        for _, elem in etree.iterparse(data):
            title, redirect, text = _extract_article(elem)
            # Guards
            if redirect:
                continue
            if not _valid_page(title):
                continue
            if _page_is_disamb(title, text):
                continue
            # Add title
            if title:
                titles.append(title)
    return titles


# ###############################################################################
# MAIN
# ###############################################################################


def extract_forms(resources_dir):
    """Extracts forms from Wikipedia & Wikidata by applying constraints.
    A report is saved at each step, so we don't have to run the whole process again when one step fails.
    To make sure a step is rerun, the corresponding report must be manually deleted beforehand.
    """
    Logger.info('EXTRACT FORMS')
    timer = Timer()

    # LOAD CLASSES
    # -------------------------------------------------------------------------->

    reports_dir = cfg.REPORTS_DIR / 'extract_classes'

    # Read classes
    uri_cid = load_dict_from_txt_file(reports_dir / 'uri_cid.txt', value_type=int)
    Logger.info('Extracted {:,} classes in {}'.format(len(uri_cid), timer.lap_time))
    # Read entity's classes
    eid_cids = load_dict_from_txt_file(reports_dir / 'eid_cids.txt', key_type=int, value_type=eval)
    Logger.info('{:,} entities assigned in {}'.format(len(eid_cids), timer.lap_time))

    # EXTRACT WIKIPEDIA TITLES
    # -------------------------------------------------------------------------->

    reports_dir = cfg.REPORTS_DIR / 'extract_forms'
    filepaths = [pathlib.Path(resources_dir) / file for file in files_in_dir(resources_dir) if file.endswith('.bz2')]

    report_file = 'titles.txt'
    if path_exists(reports_dir / report_file):
        titles = load_set_from_txt_file(reports_dir / report_file)
        Logger.info('{:,} titles loaded from "{}" in {}'.format(len(titles), report_file, timer.lap_time))
    else:
        with multiprocessing.Pool(cfg.NB_PROCESSES) as pool:
            title_lists = pool.map(_extract_titles, filepaths)
        titles = sorted([title for title_list in title_lists for title in title_list])
        with txt_file_writer(reports_dir / report_file) as report:
            for title in titles:
                report.write('%s\n' % title)
        titles = set(titles)
        Logger.info('{:,} titles extracted in {}'.format(len(titles), timer.lap_time))

    # LINK TITLES TO IDs
    # -------------------------------------------------------------------------->

    report_file = 'eid_title.txt'
    if path_exists(reports_dir / report_file):
        eid_title = load_dict_from_txt_file(reports_dir / report_file, key_type=int)
        Logger.info(
            '{:,} entity IDs loaded from "{}" in {}'.format(len(eid_title), report_file, timer.lap_time))
    else:
        with txt_file_reader(cfg.REPORTS_DIR / 'extract_items' / 'items.txt') as data:
            eid_title = {}  # entity ID => wikipedia title
            for line in data:
                item = json.loads(line.strip())
                if item['title'] in titles:
                    eid_title[item['id']] = item['title']
        with txt_file_writer(reports_dir / report_file) as report:
            for eid, title in eid_title.items():
                report.write('%d\t%s\n' % (eid, title))
        Logger.info('{:,} titles mapped to an entity ID'.format(len(eid_title), timer.lap_time))
    title_eid = reverse_dict(eid_title)
    del titles

    # PREPARE FORM EXTRACTION
    # -------------------------------------------------------------------------->

    def _write_form_titles(_form_titles, _report_file):
        with txt_file_writer(reports_dir / _report_file) as _report:
            for _form, _titles in _form_titles.items():
                _report.write('%s\t%s\n' % (_form, str(_titles)))

    # EXTRACT FORMS FROM WIKIDATA ITEMS
    # -------------------------------------------------------------------------->

    report_file = 'form_titles_from_items.txt'
    if path_exists(reports_dir / report_file):
        form_titles_from_items = load_dict_from_txt_file(reports_dir / report_file, value_type=eval)
        Logger.info(
            '{:,} forms loaded from "{}" in {}'.format(len(form_titles_from_items), report_file, timer.lap_time))
    else:
        with txt_file_reader(cfg.REPORTS_DIR / 'extract_items' / 'items.txt') as data:
            form_titles_from_items = {}  # form => set of titles
            for line in data:
                item = json.loads(line.strip())
                if item['title'] in title_eid:
                    for form in [_convert_to_form(label) for label in [item['label']] + item['aliases']]:
                        if form:
                            add_in_dict_set(form_titles_from_items, form, item['title'])
        _write_form_titles(form_titles_from_items, report_file)
        Logger.info('{:,} forms extracted in {}'.format(len(form_titles_from_items), timer.lap_time))

    # EXTRACT FORMS FROM TITLES
    # -------------------------------------------------------------------------->

    report_file = 'form_titles_from_titles.txt'
    if path_exists(reports_dir / report_file):
        form_titles_from_titles = load_dict_from_txt_file(reports_dir / report_file, value_type=eval)
        Logger.info(
            '{:,} forms loaded from "{}" in {}'.format(len(form_titles_from_titles), report_file, timer.lap_time))
    else:
        re_parenthesis = re.compile(r'([^()]+?) \(.+?\)')  # e.g. "Harbach (surname)", 1 capturing group
        re_comma = re.compile(r'([^,"(]+?), ([^,")\'?!.&]+?)')  # e.g. "Paris, France", 2 capturing groups
        creative_work_cid = uri_cid['http://schema.org/CreativeWork']
        form_titles_from_titles = {}  # form => set of titles
        for eid, title in eid_title.items():
            match = re.fullmatch(re_parenthesis, title)
            form = None
            if match:
                form = _convert_to_form(match.group(1))
            else:
                match = re.fullmatch(re_comma, title)
                if match:
                    # Guards
                    if eid not in eid_cids:
                        continue
                    if any([' and ' in match.group(2), ' or ' in match.group(2)]):
                        continue
                    if creative_work_cid in eid_cids[eid]:
                        continue
                    # Create form
                    form = _convert_to_form(match.group(1))
            if form:
                add_in_dict_set(form_titles_from_titles, form, title)
        _write_form_titles(form_titles_from_titles, report_file)
        Logger.info('{:,} forms extracted from titles in {}'.format(len(form_titles_from_titles), timer.lap_time))

    # EXTRACT FORMS FROM ALL TYPE OF LINKS
    # -------------------------------------------------------------------------->

    report_redirects = 'form_titles_from_redirects.txt'
    report_disambs = 'form_titles_from_disambiguations.txt'

    def _write_source_target_tuples(_tuples, _report_file):
        _form_titles = {}  # form => set of titles
        for _source, _target in _tuples:
            _form = _convert_to_form(_source)
            if _form:
                add_in_dict_set(_form_titles, _form, _target)
        _write_form_titles(_form_titles, _report_file)
        return _form_titles

    if all([path_exists(reports_dir / report_redirects), path_exists(reports_dir / report_disambs)]):
        form_titles_from_redirects = load_dict_from_txt_file(reports_dir / report_redirects, value_type=eval)
        form_titles_from_disambs = load_dict_from_txt_file(reports_dir / report_disambs, value_type=eval)
        Logger.info('{:,} forms loaded from "{}"'.format(len(form_titles_from_redirects), report_redirects))
        Logger.info('{:,} forms loaded from "{}"'.format(len(form_titles_from_disambs), report_disambs))
    else:
        re_simple_link = re.compile(r'\[\[([^\n]+?)(\|.+?)?]]')
        # List of tuples (source, target)
        redirects = []
        disambs = []
        # Extraction: not using multiprocessing due to memory overflow (each file has a lot of links)
        for filepath in filepaths:
            with bz2_file_bytes_reader(filepath) as data:
                for _, elem in etree.iterparse(data):
                    title, redirect, text = _extract_article(elem)
                    # Guards
                    if not _valid_page(title):
                        continue
                    # Redirect
                    if redirect in title_eid:
                        redirects.append((title, redirect))
                    # Disambiguation
                    elif _page_is_disamb(title, text):
                        for match in re.finditer(re_simple_link, text):
                            target = match.group(1)
                            if target in title_eid and title.lower() in target.lower():
                                disambs.append((title, target))
        # Write reports
        form_titles_from_redirects = _write_source_target_tuples(redirects, report_redirects)
        form_titles_from_disambs = _write_source_target_tuples(disambs, report_disambs)
        Logger.info('{:,} forms extracted from redirects'.format(len(form_titles_from_redirects)))
        Logger.info('{:,} forms extracted from disambiguations'.format(len(form_titles_from_disambs)))
    Logger.info('Extracted forms from all types of link in {}'.format(timer.lap_time))

    # CONSOLIDATE
    # -------------------------------------------------------------------------->

    form_eids = {}  # form => set of entity IDs

    def _update_form_eids(_form_titles):
        for _form, _titles in _form_titles.items():
            for _title in _titles:
                add_in_dict_set(form_eids, _form, title_eid[_title])

    # Consolidate forms
    _update_form_eids(form_titles_from_items)
    _update_form_eids(form_titles_from_titles)
    _update_form_eids(form_titles_from_redirects)
    _update_form_eids(form_titles_from_disambs)
    # Write global report
    with txt_file_writer(reports_dir / 'form_titles.txt') as report:
        for form, eids in sorted(form_eids.items(), key=lambda x: len(x[1]), reverse=True):
            report.write('%s\t%d\t%s\n' % (form, len(eids), str({eid_title[eid] for eid in eids})))
    Logger.info('Extracted {:,} forms in total'.format(len(form_eids)))
    Logger.info('Total time: {}'.format(timer.total_time))
