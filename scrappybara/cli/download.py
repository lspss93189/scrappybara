import os
import shutil
import sys
import urllib.request
import zipfile

import requests
import tqdm

import scrappybara.config as cfg


class DownloadProgressBar(tqdm.tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download(bundle):
    """Downloads & unzips data files according to current version of Scrappybara"""
    filename = cfg.HOME_DIR / 'data.zip'
    if bundle == 'core':
        url = 'https://github.com/ericperriard/scrappybara/releases/download/v%s/data-%s-core.zip' % (
            cfg.APP_VERSION, cfg.DATA_VERSION)
    elif bundle == 'full':
        url = 'https://github.com/ericperriard/scrappybara/releases/download/v%s/data-%s-full.zip' % (
            cfg.APP_VERSION, cfg.DATA_VERSION)
    else:
        sys.exit('Argument not recognized: can only download "core" or "full" data.')
    # Check if file exists
    if requests.head(url).status_code != requests.codes.ok:
        sys.exit('The data corresponding to this version of Scrappybara is not available anymore. ' +
                 'Please upgrade Scrappybara first: "pip3 install --upgrade scrappybara".')
    # Dowload
    print('Downloading zip file...')
    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=url.split('/')[-1]) as progress:
        urllib.request.urlretrieve(url, filename, reporthook=progress.update_to)
    # Delete current data
    print('Deleting old data if any...')
    try:
        shutil.rmtree(cfg.HOME_DIR / 'data')
    except FileNotFoundError:
        pass
    # Unzip
    print('Unzipping files...')
    with zipfile.ZipFile(filename) as zip_file:
        zip_file.extractall(cfg.HOME_DIR)
    # Clean
    print('Deleting zip file...')
    os.remove(filename)
    print('All done.')
