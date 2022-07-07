import mangadex
from libra import *
import os
import zipfile
import pathlib
import time
from functions import *
from inspect import cleandoc


api = mangadex.Api()


class Manga:

    def __str__(self):
        return f"{self.manga}"

    
    def setGroups(self):
        tuttiCapitoli=getAllChapters(api,self.idManga,self.language)

        # Lista di id di gruppi con ripetizioni se hanno fatto più capitoli
        gruppi=[a.group_id for a in tuttiCapitoli]

        # Dizionario con frequenze dei gruppi
        self.groupsNum={}
        for a in gruppi:
            if (a in self.groupsNum):
                self.groupsNum[a] += 1
            else:
                self.groupsNum[a] = 1

    def getAllChapters(api,manga_id,translatedLanguage=None):
        tuttiCapitoli=[]
        alcuniCapitoli=api.manga_feed(
                manga_id=manga_id, limit=100, offset=100 *i, translatedLanguage=translatedLanguage)
        while len(alcuniCapitoli)> 0:
            alcuniCapitoli.extend(alcuniCapitoli)
            alcuniCapitoli=api.manga_feed(
                manga_id=manga_id, limit=100, offset=100 *i, translatedLanguage=translatedLanguage)
        return tuttiCapitoli


    def __init__(self, idManga=None, language='en', cover_locale=None, path='./Libri'):
        if idManga is None:
            return
        self.language=language
        self.idManga=idManga
        self.cover_locale=cover_locale

        self.manga=api.view_manga_by_id(manga_id=self.idManga)

        # Dizionario con {1 : {'volume': 1 , 'count' : 6 , chapters : {...} }, ...}
        self.volumes=api.get_manga_volumes_and_chapters(
            manga_id=idManga, limit=300, translatedLanguage=self.language)  # API limita a 300 volumi

        self.title=list(self.manga.title.values())[0]
        self.basePath=f'{path}'
        self.path=f'{path}/{self.title}'

        self.coverId=self.manga.manga_id

        self.authorId=self.manga.author_id[0]
        self.author=api.get_author_by_id(author_id=self.authorId).name

        self.setGroups()
    
    def setup(self,idManga=None):
        if idManga is None:
            idManga=input("ID Manga: ")
        self.idManga=idManga
        self.manga=api.view_manga_by_id(manga_id=idManga)
        self.title=list(self.manga.title.values())[0]
        print(self.title)
        #print(self.manga)
        tuttiCapitoli=getAllChapters(api,idManga)
        langagues=possibleLanguages(tuttiCapitoli)
        print(langagues)
        language=input("Language: ")
        if language not in langagues:
            raise Exception("Language not found")
        print()
        self.language=language
        covers=getCovers(api,idManga)
        locales=getLocales(api,covers)
        print(locales)
        locale=input("Cover locale: ")
        if locale not in locales:
            raise Exception("Cover locale not found")
        
        self.setGroups()
        tuttiCapitoliLingua=getChapters(api,idManga,language,self.groupsNum)

        groupsNamesById=getGroupsNamesById(api,tuttiCapitoliLingua)
        # Lista di capitoli
        capitoli=[(a.chapter,a.group_id) for a in tuttiCapitoliLingua]

        capitoli=sorted(capitoli,key=lambda x: x[0])

        #Give a color to every element of groupsNamesById
        groupsColor={group_id: randomColor() for group_id in list(groupsNamesById)}

        groupsCount=[(group_id,[a[1] for a in capitoli].count(group_id)) for group_id in list(groupsNamesById)]

        groupsCount=sorted(groupsCount,key=lambda x: x[1],reverse=True)
        for a in groupsCount:
            print(color(groupsNamesById[a[0]]+" "+str(a[1]),groupsColor[a[0]]),end=', ')
        print()
        for a in capitoli:
            print(color(a[0],groupsColor[a[1]]),end=' ')
        
        self.__init__(idManga,language,locale)




    def metadata(self, volume, a=None):
        if a is None:
            a=self.volume

        return cleandoc(f"""
            <?xml version='1.0' encoding='utf-8'?>
            <ComicInfo>
            <Title>{self.title} {numero(volume,' Extra')}</Title>
            <Series>{self.title}</Series>
            <Number>{numero(a)}</Number>
            <Writer>{self.author}</Writer>
            <LanguageISO>{self.language}</LanguageISO>
            <Manga>Yes</Manga>
            </ComicInfo>"""
                        )

    def cbz(self):
        folder=self.path
        subfolders = [f.name for f in os.scandir(
            f"{folder}/images") if f.is_dir()]

        cartelle=[int(a) for a in subfolders if a.isdigit()]

        # Number of the volume made from chapters not in any volume
        if len(cartelle)>0:
            extraVolume=max(cartelle) +1
        else:
            extraVolume=1

        for i in subfolders:
            pathImages=f"{folder}/images"
            pathMetadata=f"{pathImages}/ComicInfo.xml"
            pathCurrentVolume=f"{pathImages}/{i}"
            pathOutput=f"{folder}/out"

            createDir(pathOutput)

            printo(
                f"Creating {pathOutput}/{self.title} {numero(i,' Extra')}.cbz")

            metadata=self.metadata(i, realVolume(i, extraVolume))

            writeFile(pathMetadata, metadata)

            directory = pathlib.Path(pathCurrentVolume)

            pathCbz=f"{pathOutput}/{self.title} {numero(i,' Extra')}.cbz"

            with zipfile.ZipFile(pathCbz, mode="w") as archive:
                for file_path in directory.rglob("*"):
                    archive.write(
                        file_path,
                        arcname=file_path.relative_to(pathImages)
                    )

                archive.write(
                    pathMetadata,
                    arcname="ComicInfo.xml"
                )

    def save(self,whichVolumes=None):


        chapters=getChapters(api,self.idManga,self.language,self.groupsNum)

        covers=api.get_coverart_list(manga=self.idManga, limit=100)

        cover=getCorrectCovers(covers, self.cover_locale)

        sizeDownloaded=0
        start = 0
        end = 0
        incremento=0
        for i, chapter in enumerate(chapters):

            volume=chapter.volume
            whichVolumes=[str(a) for a in whichVolumes]
            if whichVolumes is not None:
                if volume not in whichVolumes:
                    continue

            path = f'{self.path}/images/{volume}'            
            createDir(path)

            coverPath=f"{path}"
            downloadCover(cover, volume, coverPath, )

            chapterNumber=chapter.chapter
            path=path +f"/{chapterNumber:05}"
            createDir(path)

            loading(
                i /len(chapters), f'Downloading {volume}-{chapterNumber} {bites(sizeDownloaded/(max(end - start,1)))}/s')

            links=chapter.fetch_chapter_images()
            # print(links)
            start = time.time()
            URLS_PATHS=[[link, f"{path}/{(incremento+i):05}.{getFormat(link)}"]
                        for i, link in enumerate(links)]
            incremento=incremento+len(links)
            end = time.time()
            sizeDownloaded=download_multiple(URLS_PATHS)
            # sleep(0.5)


if __name__ == "__main__":
    #idManga='d86cf65b-5f6c-437d-a0af-19a31f94ec55'
    idManga='0951feea-ba41-4ad0-9cb0-edadc77eae73'
    # idManga='c0ad8919-4646-4a61-adf9-0fd6d8612efa'
    #manga=Manga(idManga, 'en', 'ja', './///Libri')
    manga=Manga()
    manga.setup()
    print(manga.title)

    manga.save([1])
    manga.cbz()
