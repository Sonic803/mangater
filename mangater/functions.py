
import os
import requests
import concurrent.futures
from concurrent.futures import as_completed
from print_libra import hsv_to_rgb, randomVividColor


def download(url, path, force=False):
    if not os.path.exists(path) or force:
        img_data = requests.get(url).content
        with open(path, 'wb') as handler:
            handler.write(img_data)
        return len(img_data)
    return 0


def getCovers(api, idManga):
    return api.get_coverart_list(manga=idManga, limit=100)


def getLocales(api, covers):
    locales=[]
    for a in covers:
        if a.locale not in locales:
            locales.append(a.locale)
    return locales


def getCorrectCovers(coverss, cover_locale=None):
    covers={}
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


def realVolume(i, extraVolume):
    if i=='None':
        return extraVolume
    else:
        return i


def getChapters(api, idManga, language, groupsNum):
    offset=0
    capitoli=[]
    pochiCapitoli=api.chapter_list(
        manga=idManga, translatedLanguage=language, limit=100, offset=100 *offset)
    while len(pochiCapitoli)>0:
        capitoli.extend(pochiCapitoli)
        offset=offset +1
        pochiCapitoli=api.chapter_list(
            manga=idManga, translatedLanguage=language, limit=100, offset=100 *offset)

    indice_Capitolo={}
    for a in capitoli:
        indice=a.chapter
        if a.chapter in indice_Capitolo:
            vecchio=indice_Capitolo[indice].group_id
            nuovo=a.group_id
            if groupsNum[vecchio]<groupsNum[nuovo]:
                indice_Capitolo[indice]=a
        else:
            indice_Capitolo[indice]=a

    indiciCapitoli=sorted(list(indice_Capitolo))

    capitoliMigliori=[]
    for a in indiciCapitoli:
        capitoliMigliori.append(indice_Capitolo[a])
    return capitoliMigliori


def getAllChapters(api, manga_id, translatedLanguage=None):
    offset=0
    capitoli=[]
    pochiCapitoli=[]
    while len(pochiCapitoli)>0 or offset==0:
        if translatedLanguage==None:
            pochiCapitoli=api.chapter_list(
                manga=manga_id, limit=100, offset=100 *offset)
        else:
            pochiCapitoli=api.chapter_list(
                manga=manga_id, translatedLanguage=translatedLanguage, limit=100, offset=100 *offset)
        capitoli.extend(pochiCapitoli)
        offset=offset +1

    return capitoli


def possibleLanguages(capitoli):
    languages=[]
    for a in capitoli:
        if a.translatedLanguage not in languages:
            languages.append(a.translatedLanguage)
    return languages


def getGroupName(api, group_id):
    return api.scanlation_group_list(group_ids=group_id)[0].name


def getGroupsNamesById(api, chapters):
    groups=[]
    for a in chapters:
        if a.group_id not in groups:
            groups.append(a.group_id)
    return {group_id: getGroupName(api, group_id) for group_id in groups}


def randomColor():
    # array of 3 random numbers between 0 and 255
    return randomVividColor()


def getRainbowColor(i, n):
    # array of 3 random numbers between 0 and 255
    return hsv_to_rgb(i /n, 1., 1.)
