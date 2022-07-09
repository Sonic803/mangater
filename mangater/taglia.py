def diff(a, b):
    return abs(a -b)


def isSame(lista):
    coso=lista[0]
    treshold=20

    for a in lista[::10]:
        if diff(coso, a)> treshold:

            return False

    return True

def hihf(data):
    hi=0
    hf= len(data) -1

    while isSame(data[hi]):
        hi+=1
    while isSame(data[hf]):
        hf-=1

    hi=max(0, hi -3)

    hf=min(len(data) -1, hf +3)
    return (hi,hf)


def taglia(data):
    hi,hf=hihf(data)
    data=data[hi:hf]
    data=data.transpose(1, 0)
    hi,hf=hihf(data)
    data=data[hi:hf]
    data=data.transpose(1, 0)

    return data