import pathlib
import re

import scrappybara.config as cfg
from scrappybara.utils.files import path_exists, txt_file_reader, txt_file_writer, load_dict_from_txt_file
from scrappybara.utils.mutables import append_to_dict_list
from scrappybara.utils.timer import Timer


def extract_classes(resources_dir):
    """Extracts entity's classes from knowledge base"""
    # Reports
    reports_dir = cfg.REPORTS_DIR / 'extract_classes'
    report_uri_eid = 'uri_eid.txt'  # Map Yago URI to Wikidata ID
    report_uri_cid = 'uri_cid.txt'  # Map Schema URI to internal class ID
    report_eid_cids = 'eid_cids.txt'  # Map entity id and their relation "instance_of"
    # Patterns
    re_wikidata_uri = re.compile(r'<http://www.wikidata.org/entity/Q(\d+)>')
    # Process
    timer = Timer()
    print()
    # Extract URIs and their entity ID
    if path_exists(reports_dir / report_uri_eid):
        print('Reading entity IDs from "%s"...' % report_uri_eid)
        yago_eid = load_dict_from_txt_file(reports_dir / report_uri_eid)
    else:
        print('Extracting entity IDs...')
        with txt_file_reader(pathlib.Path(resources_dir) / 'yago-wd-sameAs.nt') as data:
            yago_eid = {}  # yago_uri => entity id (numerical string)
            for line in data:
                yago_uri, _, same_as, _ = line.strip().split('\t')
                match = re.fullmatch(re_wikidata_uri, same_as)
                if match:
                    yago_eid[yago_uri] = match.group(1)
        with txt_file_writer(reports_dir / report_uri_eid) as report:
            for yago_uri, eid in yago_eid.items():
                report.write('%s\t%s\n' % (yago_uri, eid))
            print('Wrote "%s" in full' % report_uri_eid)
    print('{:,} URIs extracted in {}'.format(len(yago_eid), timer.lap_time))
    print()
    # Extract class IDs
    if path_exists(reports_dir / report_uri_cid):
        print('Reading class IDs from "%s"' % report_uri_cid)
        uri_cid = load_dict_from_txt_file(reports_dir / report_uri_cid, int)
    else:
        print('Extracting class IDs...')
        with txt_file_reader(pathlib.Path(resources_dir) / 'yago-wd-schema.nt') as data:
            uri_cid = {}  # Schema URI => class ID
            class_id = 1
            for line in data:
                class_uri, _, _, _ = line.strip().split('\t')
                uri = class_uri[1:-1]
                if uri not in uri_cid and uri.startswith('http'):
                    uri_cid[uri] = class_id
                    class_id += 1
        with txt_file_writer(reports_dir / report_uri_cid) as report:
            for uri, cid in uri_cid.items():
                report.write('%s\t%d\n' % (uri, cid))
        print('Wrote "%s" in full' % report_uri_cid)
    print('Extracted {:,} classes in {}'.format(len(uri_cid), timer.lap_time))
    print()
    # Extract "instance_of" relations
    if path_exists(reports_dir / report_eid_cids):
        print('Reading types from "%s"' % report_eid_cids)
        eid_cids = load_dict_from_txt_file(reports_dir / report_eid_cids, eval)
    else:
        print('Extracting types...')
        with txt_file_reader(pathlib.Path(resources_dir) / 'yago-wd-simple-types.nt') as data:
            eid_cids = {}  # entity id => list of class ids
            for line in data:
                yago_uri, _, instance_of, _ = line.strip().split('\t')
                eid = yago_eid.get(yago_uri, None)
                if eid is not None:
                    append_to_dict_list(eid_cids, int(eid), uri_cid[instance_of[1:-1]])
        with txt_file_writer(reports_dir / report_eid_cids) as report:
            for eid, types in eid_cids.items():
                report.write('%d\t%s\n' % (eid, str(types)))
            print('Wrote "%s" in full' % report_eid_cids)
    print('{:,} entities assigned in {}'.format(len(eid_cids), timer.lap_time))
    print()
    # All done
    print('All done in {}'.format(timer.total_time))
