from tokenize import group
import mangadex
import json
from libra import *
import os
import requests
from time import sleep
api = mangadex.Api()

#Download url to path if not exists
def download(url,path,force=False):
    if not os.path.exists(path) or force:
        img_data = requests.get(url).content
        with open(path, 'wb') as handler:
            handler.write(img_data)
        return 1
    return 0

def downloadCover(covers,volume,path):
    if volume in covers:
        url = covers[volume].fetch_cover_image()
        createDir(path)
        download(url,f"{path}/cover.jpg",force=True)
        return 1
    return 0

def createDir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        return 1
    return 0

class Manga:
    def __init__(self, idManga,language='en'):
        self.language=language
        self.idManga=idManga
        self.manga=api.view_manga_by_id(manga_id=self.idManga)

        self.volumes=api.get_manga_volumes_and_chapters(
            manga_id=idManga, limit=300,translatedLanguage=self.language) #API limita a 300 volumi
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

    def __str__(self):
        return f"{self.manga}"
        #return f"{self.volumes}"

    def save(self):
        chapt=[]
        for i in range (10):
            chapt.extend(api.chapter_list(manga=self.idManga,translatedLanguage=self.language,limit=100,offset=100*i))

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
            createDir(path)
            coverPath=f"{path}/\"0cover"
            downloadCover(covers,volume,coverPath)


            path=path+f"/{a.chapter}"
            createDir(path)

            links=a.fetch_chapter_images()

            #for i,link in enumerate(links):
            #    print(link)
            #    download(link,f"{path}/{i}.jpg")
            
            
            sleep(0.5)
    

if __name__ == "__main__":
    idManga='a1422bad-4598-4018-95ae-888435bafe67'
    manga=Manga(idManga)
    # print(manga)
    #print(manga.capitoli)
    print(manga.volumes)
    manga.save()
