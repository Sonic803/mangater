from tokenize import group
import mangadex
import json
from libra import *
import os
import requests
from time import sleep
api = mangadex.Api()


class Manga:
    def __init__(self, idManga,language='en'):
        self.language=language
        self.quant=3
        self.idManga=idManga
        self.manga=api.view_manga_by_id(manga_id=self.idManga)
        self.volumes=api.get_manga_volumes_and_chapters(
            manga_id=idManga, limit=1000,translatedLanguage=self.language)
        self.coverId=self.manga.coverId
        self.title=list(self.manga.title.values())[0]
        self.description=self.manga.description
        self.authorId=self.manga.authorId
        self.artistId=self.manga.artistId
        self.genres=self.manga.publicationDemographic
        self.status=self.manga.status
        self.year=self.manga.year
        self.chapters=[]
        for i in range (10):
            self.chapters.extend(api.manga_feed(manga_id=idManga,limit=100,offset=100*i,translatedLanguage=self.language))
        
        # self.chapters=api.chapter_list(manga=idManga,limit=3)

        self.volumi=list(self.volumes.values())
        self.capitoli=[list(a.values())[0] for a in list(self.volumi)]
        capitoli=[a['chapters'] for a in self.volumi]


        self.groups=[a.scanlation_group_id for a in self.chapters]

        self.groupsNum={}
        for a in self.groups:
            if (a in self.groupsNum):
                self.groupsNum[a] += 1
            else:
                self.groupsNum[a] = 1
        print(self.groupsNum)
        #get the largest element from groupsNum


        # self.volumes=self.manga.volumes
        # self.last_chapter=self.manga.last_chapter
        # self.last_volume=self.manga.last_volume
        # self.views=self.manga.views
        # self.favorites=self.manga.favorites
        # self.date_uploaded=self.manga.date_uploaded
        # self.date_last_updated=self.manga.date_last_updated
        # self.date_last_chapter_updated=self.manga.date_last_chapter_updated
        # self.is_manga=self.manga.is_manga
        # self.is_licenced=self.manga.is_licenced
        # self.is_adult=self.manga.is_adult
        # self.is_completed=self.manga.is_completed
        # self.is_ongoing=self.manga.is_ongoing
        # self.is_licensed=self.manga.is_licensed
        # self.is_hentai=self.manga.is_hentai
        # self.is_mature=self.manga.is_mature
        # self.is_partial=self.manga.is_partial
        # self.is_nsfw=self.manga.is_nsfw
        # self.is_liked=self.manga.is_liked
        # self.is_disliked=self

    def __str__(self):
        # return f"{self.manga}"
        return f"{self.volumes}"

    def download(self):
        chapt=[]
        for i in range (10):
            chapt.extend(api.chapter_list(manga=self.idManga,translatedLanguage=self.language,limit=100,offset=100*i))
        for a in chapt:
            print(a.volume,a.chapter)
        print(self.groupsNum)
        vett={}
        for a in chapt:
            indice=a.chapter
            if a.chapter in vett:
                vecchio=vett[indice].scanlation_group_id
                nuovo=a.scanlation_group_id
                if self.groupsNum[vecchio]<self.groupsNum[nuovo]:
                    vett[indice]=a
            else:
                vett[indice]=a
            print(vett)

        e=sorted(list(vett))
        f=[]
        for a in e:
            f.append(vett[a])
        print([(a,a.chapter) for a in f])

        coverss=api.get_coverart_list(manga=self.idManga,limit=100)
        print(coverss)
        covers={}
        for a in coverss:
            if   a.fileName.find('.jpg')!=-1:
                covers[a.volume]=a
        print(f"Coversss:::: {covers}")

        for a in f:

            volume=a.volume
            path = f'./{self.title}/{volume}'
            if not os.path.exists(path):
                os.makedirs(path)


            if not os.path.exists(f"{path}/0cover"):
                os.makedirs(f"{path}/0cover")
                print(covers[volume].fetch_cover_image())
                img_data = requests.get(covers[volume].fetch_cover_image()).content
                with open(f'{path}/0cover/{volume}.jpg', 'wb') as handler:
                    handler.write(img_data)

            path=path+f"/{a.chapter}"
            if not os.path.exists(path):
                os.makedirs(path)
            links=a.fetch_chapter_images()
            #print(links)
            print(a.chapter)
            
            for i,b in enumerate(links):
                if not os.path.exists(f'{path}/{i}.jpg'):
                    img_data = requests.get(b).content
                    with open(f'{path}/{i}.jpg', 'wb') as handler:
                        handler.write(img_data)
                else:
                    print(f"Esiste: {a.chapter}.{i}")
            #fetch_cover_image
            sleep(0.5)


        return 42
    

if __name__ == "__main__":
    idManga='d86cf65b-5f6c-437d-a0af-19a31f94ec55'
    manga=Manga(idManga)
    # print(manga)
    #print(manga.capitoli)
    print(manga.volumes)
    manga.download()
