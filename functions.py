
from libra import *
import os
import requests
import concurrent.futures
from functions import *

from concurrent.futures import as_completed


def download(url, path, force=False):
    if not os.path.exists(path) or force:
        img_data = requests.get(url).content
        with open(path, 'wb') as handler:
            handler.write(img_data)
        return len(img_data)
    return 0


def getcovers(coverss, cover_locale=None):
    covers={}
    id=''
    for a in coverss:
        if cover_locale==None:
            cover_locale=a.locale
        if a.volume in covers:
            if a.locale==cover_locale:
                covers[a.volume]=a
        else:
            covers[a.volume]=a
    return covers


def numero(volume, title=None):
    if volume=='None':
        if title==None:
            return 0
        else:
            return title
    else:
        return volume


def download_for_multiple(url, path, force=False):
    return (download(url, path, force), path)


def download_multiple(urls_paths, force=False):
    conta=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(
            download_for_multiple, url_path[0], url_path[1]) for url_path in urls_paths]
        for future in as_completed(futures):
            # retrieve result
            res, path = future.result()
            # check for a link that was skipped
            conta=conta +res
            """if res :
                print(f'Downloaded')
            else:
                print(f'>skipped {path}')"""
    return conta


def downloadCover(covers, volume, path):
    if volume in covers:
        url = covers[volume].fetch_cover_image()
        createDir(path)
        download(url, f"{path}/0.{getFormat(url)}", force=True)
        return 1
    return 0


def createDir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        return 1
    return 0


def getFormat(link):
    return link.split(".")[-1]


def writeFile(path, stringa):
    with open(path, "w") as text_file:
        text_file.write(stringa)
