import json
import multiprocessing
import re

from lxml import etree

import scrappybara.config as cfg
from scrappybara.preprocessing.tokenizer import Tokenizer
from scrappybara.utils.files import bz2_file_bytes_reader, files_in_dir, txt_file_writer, path_exists, \
    txt_file_reader, load_set_from_txt_file, load_dict_from_txt_file
from scrappybara.utils.mutables import add_in_dict_set
from scrappybara.utils.timer import Timer


def _valid_token(token):
    return token not in {"'", '"', '.', ',', ';', ':', '(', ')', '-', '_', '[', ']', '{', '}', '...'}


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


def _update_form_eids(main_dic, dic):
    for form, titles in dic.items():
        try:
            main_dic[form] |= titles
        except KeyError:
            main_dic[form] = titles


# ###############################################################################
# PROCESS STEPS
# ###############################################################################


def _extract_titles(filename):
    """Extract valid titles from wikipedia articles"""
    # Patterns
    re_disamb = re.compile(r'{{[^()]*?Disambiguation[^()]*?}}', re.I)  # Wikipedia disambiguation template
    categories = ['Wikipedia:', 'Portal:', 'Category:', 'Template:', 'File:', 'Module:', 'MediaWiki:', 'Book:',
                  'Draft:', 'List of']
    # Read file
    titles = []
    with bz2_file_bytes_reader(cfg.HOME_DIR / 'resources' / 'wikipedia' / filename) as data:
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


def _extract_forms_from_titles(title_item):
    """Extract an additional form from a title (that is not the title)"""
    # Patterns
    re_parenthesis = re.compile(r'([^()]+?) \(.+?\)')  # e.g. "Harbach (surname)", 1 capturing group
    re_comma = re.compile(r'([^,"(]+?), ([^,")\'?!.&]+?)')  # e.g. "Paris, France", 2 capturing groups
    # Read titles
    form_titles = {}  # form => set of titles
    for title, item in title_item.items():
        match = re.fullmatch(re_parenthesis, title) or re.fullmatch(re_comma, title)
        if match:
            if len(match.groups()) > 1 and any([' and ' in match.group(2), ' or ' in match.group(2)]):
                continue  # Avoid end of enumeration
            form = _convert_to_form(match.group(1))
            if form in item['forms']:  # Make sure the derivated form was also in Wikidata aliases
                add_in_dict_set(form_titles, form, title)
    # Filter out forms that are not ambiguous
    return {form: titles for form, titles in form_titles.items() if len(titles) > 1}


def _extract_forms_from_links(filename_titles):
    filename, titles = filename_titles
    # Patterns
    re_link = re.compile(r'\[\[([^\n]+?)\|([^\n]+?)]]')
    # Read file
    form_titles = {}
    with bz2_file_bytes_reader(cfg.HOME_DIR / 'resources' / 'wikipedia' / filename) as data:
        for _, elem in etree.iterparse(data):
            _, _, text = _extract_article(elem)
            if text:
                for match in re.finditer(re_link, text):
                    if match.group(1) in titles:
                        add_in_dict_set(form_titles, _convert_to_form(match.group(2)), match.group(1))
    return form_titles


# ###############################################################################
# MAIN
# ###############################################################################


def extract_forms(resources_dir):
    # Reports
    reports_dir = cfg.REPORTS_DIR / 'extract_forms'
    report_form_eids_from_items = 'form_eids_from_items.txt'  # forms with their se of entity ids
    report_wikipedia_titles = 'wikipedia_titles.txt'  # valid Wikipedia titles sorted by alpha
    report_form_eids_from_titles = 'form_eids_from_titles.txt'  # forms with their set of entity ids
    report_form_eids_from_urls = 'form_eids_from_urls.txt'  # forms with their set of entity ids
    # Process
    timer = Timer()
    filenames = files_in_dir(resources_dir)
    print()
    # Extract titles from Wikipedia
    if path_exists(reports_dir / report_wikipedia_titles):
        print('Reading Wikipedia titles from "%s"...' % report_wikipedia_titles)
        titles = load_set_from_txt_file(reports_dir / report_wikipedia_titles)
    else:
        print('Extracting Wikipedia titles...')
        with multiprocessing.Pool(cfg.NB_PROCESSES) as pool:
            files_titles = pool.map(_extract_titles, filenames)
        titles = sorted([title for file_titles in files_titles for title in file_titles])
        with txt_file_writer(reports_dir / report_wikipedia_titles) as report:
            for title in titles:
                report.write('%s\n' % title)
            print('Wrote "%s" in full' % report_wikipedia_titles)
        titles = set(titles)
    print('{:,} titles extracted in {}'.format(len(titles), timer.lap_time))
    print()
    # Extract forms from Wikidata items
    if path_exists(reports_dir / report_form_eids_from_items):
        print('Reading forms from "%s"...' % report_form_eids_from_items)
        all_form_eids = load_dict_from_txt_file(reports_dir / report_form_eids_from_items, eval)
    else:
        print('Extracting forms from Wikidata items...')
        with txt_file_reader(cfg.REPORTS_DIR / 'extract_items' / 'items.txt') as data:
            all_form_eids = {}
            for line in data:
                item = json.loads(line.strip())
                for form in [_convert_to_form(label) for label in [item['label']] + item.aliases]:
                    add_in_dict_set(all_form_eids, form, item['id'])
        with txt_file_writer(reports_dir / report_form_eids_from_items) as report:
            for form, eids in all_form_eids.items():
                report.write('%s\t%s\n' % (form, str(eids)))
            print('Wrote "%s" in full' % report_form_eids_from_items)
    print('{:,} forms extracted in {}'.format(len(all_form_eids), timer.lap_time))
    print()

    # Extract forms from titles
    # if path_exists(reports_dir / report_form_eids_from_titles):
    #     print('Reading forms from "%s"...' % report_form_eids_from_titles)
    #     with txt_file_reader(reports_dir / report_form_eids_from_titles) as report:
    #         form_titles_1 = {form: eval(titles) for form, titles in [line.strip().split('\t') for line in report]}
    # else:
    #     print('Extracting forms from titles...')
    #     form_titles_1 = _extract_forms_from_titles(title_item)
    #     with txt_file_writer(reports_dir / report_form_eids_from_titles) as report:
    #         for form, titles in form_titles_1.items():
    #             report.write('%s\t%s\n' % (form, str(titles)))
    #         print('Wrote "%s" in full' % report_form_eids_from_titles)
    # _update_form_eids(form_titles, form_titles_1)
    # print('{:,} forms extracted from titles in {}'.format(len(form_titles_1), timer.lap_time))
    # print()

    # Extract forms from urls
    # with multiprocessing.Pool(cfg.NB_PROCESSES) as pool:
    #     packs = [(filename, titles) for filename in filenames]
    #     list_dics = pool.map(_extract_forms_from_links, packs)
    #     consolidated_dic = {}
    #     for dic in list_dics:
    #         for form, titles in dic.items():
    #             try:
    #                 consolidated_dic[form]
    # print('{:,} forms extracted from urls in {}'.format(len(form_titles_2), timer.lap_time))
    # All done
    print('All done in {}'.format(timer.total_time))
