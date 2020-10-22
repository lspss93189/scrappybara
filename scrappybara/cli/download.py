import os
import urllib.request
import zipfile

import tqdm

import scrappybara.config as cfg


class DownloadProgressBar(tqdm.tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download():
    """Downloads & unzips data files according to current version of Scrappybara"""
    filename = cfg.HOME_DIR / 'data.zip'
    # Dowload
    print('Downloading zip file...')
    url = 'https://scrappybara.s3.ap-northeast-2.amazonaws.com/data-%s.zip' % cfg.DATA_VERSION
    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=url.split('/')[-1]) as progress:
        urllib.request.urlretrieve(url, filename, reporthook=progress.update_to)
    # Unzip
    print('Unzipping files...')
    with zipfile.ZipFile(filename) as zip_file:
        zip_file.extractall(cfg.HOME_DIR)
    # Clean
    print('Deleting zip file...')
    os.remove(filename)
    print('All done.')
