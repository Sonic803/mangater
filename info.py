from tokenize import group
import mangadex
import json
from libra import *
import os
import requests
from time import sleep
import concurrent.futures
import urllib.request
import zipfile
import pathlib


from concurrent.futures import as_completed


api = mangadex.Api()

# Download url to path if not exists


def download(url, path, force=False):
    if not os.path.exists(path) or force:
        img_data = requests.get(url).content
        with open(path, 'wb') as handler:
            handler.write(img_data)
        return 1
    return 0


def getcovers(coverss, cover_locale='en'):
    covers={}
    id=''
    for a in coverss:
        if a.volume in covers:
            if a.locale==cover_locale:
                covers[a.volume]=a
        else:
            covers[a.volume]=a
    return covers


def download_for_multiple(url, path, force=False):
    return (download(url, path, force), path)


def download_multiple(urls_paths, force=False):
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(
            download_for_multiple, url_path[0], url_path[1]) for url_path in urls_paths]
        for future in as_completed(futures):
            # retrieve result
            res, path = future.result()
            # check for a link that was skipped
            """if res :
                print(f'Downloaded')
            else:
                print(f'>skipped {path}')"""


def downloadCover(covers, volume, path):
    if volume in covers:
        url = covers[volume].fetch_cover_image()
        createDir(path)
        download(url, f"{path}/cover.{getFormat(url)}", force=True)
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
        n = text_file.write(stringa)


class Manga:
    def __init__(self, idManga, language='en', cover_locale='en'):
        self.language=language
        self.idManga=idManga
        self.manga=api.view_manga_by_id(manga_id=self.idManga)

        self.cover_locale=cover_locale

        self.volumes=api.get_manga_volumes_and_chapters(
            manga_id=idManga, limit=300, translatedLanguage=self.language)  # API limita a 300 volumi
        self.coverId=self.manga.manga_id
        self.title=list(self.manga.title.values())[0]
        self.basePath=f'./{self.title}'

        self.description=self.manga.description
        self.authorId=self.manga.author_id[0]
        self.artistId=self.manga.author_id[0]
        self.genres=self.manga.publicationDemographic
        self.status=self.manga.status
        self.year=self.manga.year
        self.chapters=[]
        for i in range(10):
            self.chapters.extend(api.manga_feed(
                manga_id=idManga, limit=100, offset=100 *i, translatedLanguage=self.language))

        # self.chapters=api.chapter_list(manga=idManga,limit=3)

        self.volumi=list(self.volumes.values())
        self.capitoli=[list(a.values())[0] for a in list(self.volumi)]
        capitoli=[a['chapters'] for a in self.volumi]

        self.groups=[a.group_id for a in self.chapters]

        self.groupsNum={}
        for a in self.groups:
            if (a in self.groupsNum):
                self.groupsNum[a] += 1
            else:
                self.groupsNum[a] = 1

    def __str__(self):
        return f"{self.manga}"
        # return f"{self.volumes}"

    def metadata(self, volume):
        return f"""<?xml version='1.0' encoding='utf-8'?>
<ComicInfo>
<Title>{self.title} {volume}</Title>
<Series>{self.title}</Series>
<Number>{volume}</Number>
<Writer>{api.get_author_by_id(author_id=self.authorId).name}</Writer>
<LanguageISO>{self.language}</LanguageISO>
<Manga>Yes</Manga>
</ComicInfo>"""

    def cbz(self):
        folder=self.basePath
        subfolders = [f.name for f in os.scandir(f"{folder}/images") if f.is_dir()]
        for i in subfolders:
            pathIm=f"{folder}/images"
            pathMetadata=f"{pathIm}/ComicInfo.xml"
            pathImages=f"{pathIm}/{i}"
            pathOutput=f"{folder}/out"
            createDir(pathOutput)

            writeFile(pathMetadata, self.metadata(i))
            # print(self.metadata(i))
            print("ciao",pathImages)
            directory = pathlib.Path(pathImages)
            print(i)
            with zipfile.ZipFile(f"{pathOutput}/{self.title} {i}.cbz", mode="w") as archive:
                for file_path in directory.rglob("*"):
                    print(file_path)
                    archive.write(
                        file_path,
                        arcname=file_path.relative_to(pathIm)

                    )
                print(pathMetadata)
                archive.write(
                    pathMetadata,
                    arcname="ComicInfo.xml"

                )

    def save(self):
        k=0
        chapt=[]
        cha=api.chapter_list(
            manga=self.idManga, translatedLanguage=self.language, limit=100, offset=100 *k)
        while len(cha)>0:
            chapt.extend(cha)
            k=k +1
            cha=api.chapter_list(
                manga=self.idManga, translatedLanguage=self.language, limit=100, offset=100 *k)

        vett={}
        for a in chapt:
            indice=a.chapter
            if a.chapter in vett:
                vecchio=vett[indice].group_id
                nuovo=a.group_id
                if self.groupsNum[vecchio]<self.groupsNum[nuovo]:
                    vett[indice]=a
            else:
                vett[indice]=a

        e=sorted(list(vett))
        f=[]
        for a in e:
            f.append(vett[a])

        coverss=api.get_coverart_list(manga=self.idManga, limit=100)
        covers=getcovers(coverss, self.cover_locale)

        for i, mangach in enumerate(f):

            volume=mangach.volume
            path = f'./{self.title}/images/{volume}'
            createDir(path)

            coverPath=f"{path}/\"0cover"
            downloadCover(covers, volume, coverPath, )

            chapter=mangach.chapter
            path=path +f"/{chapter}"
            createDir(path)

            loading(i /len(f), f'Downloading {volume}-{chapter}')

            links=mangach.fetch_chapter_images()
            #print(links)
            URLS_PATHS=[[link, f"{path}/{i:05}.{getFormat(link)}"]
                        for i, link in enumerate(links)]
            download_multiple(URLS_PATHS)
            #sleep(0.5)


if __name__ == "__main__":
    #idManga='d86cf65b-5f6c-437d-a0af-19a31f94ec55'
    idManga='c0ad8919-4646-4a61-adf9-0fd6d8612efa'
    manga=Manga(idManga, 'en', 'ja')
    print(manga.title)

    manga.save()
    manga.cbz()

