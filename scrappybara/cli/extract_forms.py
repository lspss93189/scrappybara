import json
import multiprocessing
import pathlib
import re

from lxml import etree

import scrappybara.config as cfg
from scrappybara.preprocessing.tokenizer import Tokenizer
from scrappybara.utils.files import bz2_file_bytes_reader, files_in_dir, load_set_from_txt_file, \
    load_dict_from_txt_file, txt_file_writer, txt_file_reader, path_exists
from scrappybara.utils.mutables import add_in_dict_set, reverse_dict
from scrappybara.utils.timer import Timer


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
    # Patterns
    re_disamb = re.compile(r'{{[^()]*?Disambiguation[^()]*?}}', re.I)  # Wikipedia disambiguation template
    categories = ['Wikipedia:', 'Portal:', 'Category:', 'Template:', 'File:', 'Module:', 'MediaWiki:', 'Book:',
                  'Draft:', 'List of']
    # Read file
    titles = []
    with bz2_file_bytes_reader(filepath) as data:
        for _, elem in etree.iterparse(data):
            title, redirect, text = _extract_article(elem)
            # Guards
            if redirect:
                continue
            if title:
                if title.endswith('(disambiguation)'):
                    continue
                if any([title.startswith(start_bl) for start_bl in categories]):
                    continue
            if text and re.findall(re_disamb, text):
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
    reports_dir = cfg.REPORTS_DIR / 'extract_forms'
    filepaths = [pathlib.Path(resources_dir) / filename for filename in files_in_dir(resources_dir)]
    timer = Timer()
    print()

    # LOAD CLASSES
    # -------------------------------------------------------------------------->

    reports_dir = cfg.REPORTS_DIR / 'extract_classes'
    # Read classes
    print("Extracting classes...")
    uri_cid = load_dict_from_txt_file(reports_dir / 'uri_cid.txt', value_type=int)
    print('Extracted {:,} classes in {}'.format(len(uri_cid), timer.lap_time))
    print()
    # Read entity's classes
    print("Extracting entity's class IDs...")
    eid_cids = load_dict_from_txt_file(reports_dir / 'eid_cids.txt', key_type=int, value_type=eval)
    print('{:,} entities assigned in {}'.format(len(eid_cids), timer.lap_time))
    print()

    # EXTRACT WIKIPEDIA TITLES
    # -------------------------------------------------------------------------->

    report_file = 'wikipedia_titles.txt'
    if path_exists(reports_dir / report_file):
        print('Reading Wikipedia titles from "%s"...' % report_file)
        titles = load_set_from_txt_file(reports_dir / report_file)
    else:
        print('Extracting Wikipedia titles...')
        with multiprocessing.Pool(cfg.NB_PROCESSES) as pool:
            title_lists = pool.map(_extract_titles, filepaths)
        titles = sorted([title for title_list in title_lists for title in title_list])
        with txt_file_writer(reports_dir / report_file) as report:
            for title in titles:
                report.write('%s\n' % title)
    titles = set(titles)
    print('{:,} titles extracted in {}'.format(len(titles), timer.lap_time))
    print()

    # LINKING TITLES TO IDs
    # -------------------------------------------------------------------------->

    report_file = 'form_eids.txt.txt'
    if path_exists(reports_dir / report_file):
        print('Reading title from "%s"...' % report_file)
        eid_title = load_dict_from_txt_file(reports_dir / report_file, key_type=int)
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
    title_eid = reverse_dict(eid_title)
    del titles
    print('{:,} titles have been mapped to an entity ID'.format(len(eid_title), timer.lap_time))
    print()

    # PREPARING FORM EXTRACTION
    # -------------------------------------------------------------------------->

    form_eids = {}  # form => set of entity IDs

    def _update_form_eids(_report_file):
        print('Reading forms from "%s"' % _report_file)
        _form_titles = load_dict_from_txt_file(reports_dir / _report_file, value_type=eval).items()
        for _form, _titles in _form_titles:
            for _title in _titles:
                add_in_dict_set(form_eids, _form, title_eid[_title])
        return _form_titles

    # EXTRACT FORMS FROM WIKIDATA ITEMS
    # -------------------------------------------------------------------------->

    report_file = 'form_titles_from_items.txt'
    if path_exists(reports_dir / report_file):
        form_titles = _update_form_eids(report_file)
    else:
        print('Extracting forms from Wikidata items...')
        with txt_file_reader(cfg.REPORTS_DIR / 'extract_items' / 'items.txt') as data:
            form_titles = {}  # form => set of titles
            for line in data:
                item = json.loads(line.strip())
                if item['title'] in title_eid:
                    for form in [_convert_to_form(label) for label in [item['label']] + item['aliases']]:
                        if form:
                            add_in_dict_set(form_titles, form, item['title'])
                            add_in_dict_set(form_eids, form, item['id'])
        with txt_file_writer(reports_dir / report_file) as report:
            for form, titles in form_titles.items():
                report.write('%s\t%s\n' % (form, str(titles)))
    print('{:,} forms extracted in {}'.format(len(form_titles), timer.lap_time))
    print()

    # EXTRACT FORMS FROM TITLES
    # -------------------------------------------------------------------------->

    report_file = 'form_titles_from_titles.txt'
    if path_exists(reports_dir / report_file):
        form_titles = _update_form_eids(report_file)
    else:
        print('Extracting forms from titles...')
        re_parenthesis = re.compile(r'([^()]+?) \(.+?\)')  # e.g. "Harbach (surname)", 1 capturing group
        re_comma = re.compile(r'([^,"(]+?), ([^,")\'?!.&]+?)')  # e.g. "Paris, France", 2 capturing groups
        creative_work_cid = uri_cid['http://schema.org/CreativeWork']
        form_titles = {}  # form => set of titles
        for eid, title in eid_title.items():
            match = re.fullmatch(re_parenthesis, title)
            form = None
            if match:
                form = _convert_to_form(match.group(1))
            else:
                match = re.fullmatch(re_comma, title)
                if match:
                    # Avoid any title for which we don't have classes
                    if eid not in eid_cids:
                        continue
                    # Avoid end of enumeration
                    if any([' and ' in match.group(2), ' or ' in match.group(2)]):
                        continue
                    # Don't split titles of creative works
                    if creative_work_cid in eid_cids[eid]:
                        continue
                    form = _convert_to_form(match.group(1))
            if form:
                add_in_dict_set(form_titles, form, title)
                add_in_dict_set(form_eids, form, title_eid[title])
        with txt_file_writer(reports_dir / 'form_titles_from_titles.txt') as report:
            for form, titles in form_titles.items():
                report.write('%s\t%s\n' % (form, str(titles)))
    print('{:,} forms extracted from titles in {}'.format(len(form_titles), timer.lap_time))
    print()

    # EXTRACT FORMS FROM LINKS
    # -------------------------------------------------------------------------->

    report_file = 'form_titles_from_links.txt'
    if path_exists(reports_dir / report_file):
        form_titles = _update_form_eids(report_file)
    else:
        print('Extracting forms from links...')
        re_link = re.compile(r'\[\[([^\n]+?)\|([^\n]+?)]]')
        form_titles = {}  # form => set of titles
        form_eid_titles = {}  # (form, eid) => set of titles
        for filepath in filepaths:
            with bz2_file_bytes_reader(filepath) as data:
                for _, elem in etree.iterparse(data):
                    page, _, text = _extract_article(elem)
                    if page and text:
                        for match in re.finditer(re_link, text):
                            target = match.group(1)
                            display = match.group(2)
                            if target in title_eid:
                                add_in_dict_set(form_eid_titles, (_convert_to_form(display), title_eid[target]), page)
        for form_eid, pages in form_eid_titles.items():
            # Just use links that have been used in at least 2 different pages
            if len(pages) > 1:
                form, eid = form_eid
                add_in_dict_set(form_titles, form, eid_title[eid])
                add_in_dict_set(form_eids, form, eid)
        with txt_file_writer(reports_dir / 'form_titles_from_links.txt') as report:
            for form, titles in form_titles.items():
                report.write('%s\t%s\n' % (form, str(titles)))
    print('{:,} forms extracted from links in {}'.format(len(form_titles), timer.lap_time))
    print()
    # All done
    print('All done in {}'.format(timer.total_time))


extract_forms('/media/data/wikipedia')
