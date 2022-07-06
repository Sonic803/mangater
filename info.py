import mangadex
from libra import *
import os
import zipfile
import pathlib
import time
from functions import *

api = mangadex.Api()


class Manga:
    def __init__(self, idManga, language='en', cover_locale=None,path='./'):
        self.language=language
        self.idManga=idManga
        self.manga=api.view_manga_by_id(manga_id=self.idManga)

        self.cover_locale=cover_locale

        self.volumes=api.get_manga_volumes_and_chapters(
            manga_id=idManga, limit=300, translatedLanguage=self.language)  # API limita a 300 volumi
        self.coverId=self.manga.manga_id
        self.title=list(self.manga.title.values())[0]
        self.basePath=f'{path}/{self.title}'

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
<Title>{self.title} {numero(volume,' Extra')}</Title>
<Series>{self.title}</Series>
<Number>{numero(volume)}</Number>
<Writer>{api.get_author_by_id(author_id=self.authorId).name}</Writer>
<LanguageISO>{self.language}</LanguageISO>
<Manga>Yes</Manga>
</ComicInfo>"""

    def cbz(self):
        folder=self.basePath
        subfolders = [f.name for f in os.scandir(
            f"{folder}/images") if f.is_dir()]
        for i in subfolders:
            pathIm=f"{folder}/images"
            pathMetadata=f"{pathIm}/ComicInfo.xml"
            pathImages=f"{pathIm}/{i}"
            pathOutput=f"{folder}/out"
            createDir(pathOutput)
            printo(f"Creating {pathOutput}/{self.title} {numero(i,' Extra')}.cbz")

            writeFile(pathMetadata, self.metadata(i))
            directory = pathlib.Path(pathImages)
            with zipfile.ZipFile(f"{pathOutput}/{self.title} {numero(i,' Extra')}.cbz", mode="w") as archive:
                for file_path in directory.rglob("*"):
                    archive.write(
                        file_path,
                        arcname=file_path.relative_to(pathIm)

                    )
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
        sizo=0
        start = 0
        end = 0
        for i, mangach in enumerate(f):

            volume=mangach.volume
            path = f'{self.basePath}/images/{volume}'
            createDir(path)

            coverPath=f"{path}"
            downloadCover(covers, volume, coverPath, )

            chapter=mangach.chapter
            path=path +f"/{chapter:05}"
            createDir(path)

            loading(
                i /len(f), f'Downloading {volume}-{chapter} {"{:.0f}".format(sizo/(1024*max(end - start,1)))}Kb/s    ')

            links=mangach.fetch_chapter_images()
            # print(links)
            start = time.time()
            URLS_PATHS=[[link, f"{path}/{i:05}.{getFormat(link)}"]
                        for i, link in enumerate(links)]
            end = time.time()
            sizo=download_multiple(URLS_PATHS)
            # sleep(0.5)


if __name__ == "__main__":
    idManga='d86cf65b-5f6c-437d-a0af-19a31f94ec55'
    # idManga='c0ad8919-4646-4a61-adf9-0fd6d8612efa'
    manga=Manga(idManga, 'en', 'ja','./Libri')
    print(manga.title)


    manga.cbz()
    manga.save()

