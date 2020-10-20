import os
import urllib.request
import zipfile

import tqdm

from scrappybara.config import HOME_DIR, VERSION


class DownloadProgressBar(tqdm.tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download():
    """Downloads & unzips data files according to current version of Scrappybara"""
    filename = HOME_DIR / 'data.zip'
    # Dowload
    print('Downloading zip file...')
    url = 'https://scrappybara.s3.ap-northeast-2.amazonaws.com/data-%s.zip' % VERSION
    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=url.split('/')[-1]) as progress:
        urllib.request.urlretrieve(url, filename, reporthook=progress.update_to)
    # Unzip
    print('Unzipping files...')
    with zipfile.ZipFile(filename) as zip_file:
        zip_file.extractall(HOME_DIR)
    # Clean
    print('Deleting zip file...')
    os.remove(filename)
    print('All done.')
