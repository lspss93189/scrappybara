import pathlib
import re

import scrappybara.config as cfg
from scrappybara.utils.files import txt_file_reader, txt_file_writer
from scrappybara.utils.logger import Logger
from scrappybara.utils.mutables import append_to_dict_list
from scrappybara.utils.timer import Timer


def extract_classes(resources_dir):
    """Extracts entity's classes from knowledge base"""
    Logger.info('EXTRACT CLASSES')
    reports_dir = cfg.REPORTS_DIR / 'extract_classes'
    timer = Timer()

    # EXTRACT URIs & THEIR ENTITY ID
    # -------------------------------------------------------------------------->

    re_wikidata_uri = re.compile(r'<http://www.wikidata.org/entity/Q(\d+)>')
    with txt_file_reader(pathlib.Path(resources_dir) / 'yago-wd-sameAs.nt') as data:
        yago_eid = {}  # yago_uri => entity id (numerical string)
        for line in data:
            yago_uri, _, same_as, _ = line.strip().split('\t')
            match = re.fullmatch(re_wikidata_uri, same_as)
            if match:
                yago_eid[yago_uri] = match.group(1)
    with txt_file_writer(reports_dir / 'uri_eid.tx') as report:
        for yago_uri, eid in yago_eid.items():
            report.write('%s\t%s\n' % (yago_uri, eid))
    Logger.info('{:,} URIs extracted in {}'.format(len(yago_eid), timer.lap_time))

    # GENERATE CLASS IDs
    # -------------------------------------------------------------------------->

    with txt_file_reader(pathlib.Path(resources_dir) / 'yago-wd-schema.nt') as data:
        uri_cid = {}  # schema URI => class ID
        class_id = 1
        for line in data:
            class_uri, _, _, _ = line.strip().split('\t')
            uri = class_uri[1:-1]
            if uri not in uri_cid and uri.startswith('http'):
                uri_cid[uri] = class_id
                class_id += 1
    with txt_file_writer(reports_dir / 'uri_cid.txt') as report:
        for uri, cid in uri_cid.items():
            report.write('%s\t%d\n' % (uri, cid))
    Logger.info('Extracted {:,} classes in {}'.format(len(uri_cid), timer.lap_time))

    # EXTRACT INSTANCE_OF RELATIONS
    # -------------------------------------------------------------------------->

    with txt_file_reader(pathlib.Path(resources_dir) / 'yago-wd-simple-types.nt') as data:
        eid_cids = {}  # entity id => list of class ids
        for line in data:
            yago_uri, _, instance_of, _ = line.strip().split('\t')
            eid = yago_eid.get(yago_uri, None)
            if eid is not None:
                append_to_dict_list(eid_cids, int(eid), uri_cid[instance_of[1:-1]])
    with txt_file_writer(reports_dir / 'eid_cids.txt') as report:
        for eid, types in eid_cids.items():
            report.write('%d\t%s\n' % (eid, str(types)))
    Logger.info('{:,} entities assigned in {}'.format(len(eid_cids), timer.lap_time))

    # ALL DONE
    # -------------------------------------------------------------------------->

    Logger.info('Total time: {}'.format(timer.total_time))
