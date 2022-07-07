import mangadex
from libra import *
import os
import zipfile
import pathlib
import time
from mangater.functions import *
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

        printo("Searching for chapters...")
        tuttiCapitoli=getAllChapters(api,idManga)

        deleteLastLine()
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
        
        printo("Searching for best chapters...")

        self.setGroups()
        tuttiCapitoliLingua=getChapters(api,idManga,language,self.groupsNum)

        groupsNamesById=getGroupsNamesById(api,tuttiCapitoliLingua)
        # Lista di capitoli
        capitoli=tuttiCapitoliLingua

        capitoli=sorted(capitoli,key=lambda x: x.chapter)

        #Give a color to every element of groupsNamesById
        groupsColor={group_id: getRainbowColor(i,len(list(groupsNamesById))) for i,group_id in enumerate(list(groupsNamesById))}

        groupsCount=[(group_id,[a.group_id for a in capitoli].count(group_id)) for group_id in list(groupsNamesById)]

        groupsCount=sorted(groupsCount,key=lambda x: x[1],reverse=True)

        deleteLastLine()
        for a in groupsCount:
            print(color(groupsNamesById[a[0]]+" "+str(a[1]),groupsColor[a[0]]),end=', ')
        print()
        volume=capitoli[0].volume
        print(f"Volume {volume}: " ,end='')
        for a in capitoli:
            chapter=a.chapter
            group_id=a.group_id
            if a.volume != volume:
                print()
                volume=a.volume
                print(f"Volume {volume}: " ,end='')
            print(color(chapter,groupsColor[group_id]),end=' ')
        print()

        input("Press Enter to continue...")

        volumesString=input("Which volumes do you want to download? ")
        #Remove spaces, tabs and end line from volumesString
        volumesString=volumesString.replace(' ','').replace('\t','').replace('\n','')

        #Parse volumesString into a list called volumes, volumesString is in the format "1,4-7,10"
        volumes=[]
        for a in volumesString.split(','):
            if len(a)==0:
                continue
            if '-' in a:
                start,end=a.split('-')
                volumes.extend(range(int(start),int(end)+1))
            else:
                volumes.append(int(a))
        if len(volumes) == 0:
            volumes=None
            printo(f"Volumes: all\n")
        else:
            printo(f"Volumes: {sorted(volumes)}\n")


        self.__init__(idManga,language,locale)
        self.save(volumes)
        self.cbz()



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
        if whichVolumes is not None:
            whichVolumes=[str(a) for a in whichVolumes]
            chapters=[a for a in chapters if a.volume in whichVolumes]
        
        lastvolume=chapters[0].volume
        incremento=0

        for i, chapter in enumerate(chapters):
            volume=chapter.volume

            if volume != lastvolume:
                incremento=0
                lastvolume=volume

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

    #manga.save()
    #manga.cbz()
