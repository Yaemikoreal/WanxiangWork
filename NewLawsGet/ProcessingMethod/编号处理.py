import re

from .预处理 import selectsqls


def fbbmbhcl(bh):
    if len(bh) == 9:
        bh1 = bh[0:1]
        bh2 = bh[0:3]
        bh3 = bh[0:5]
        bh4 = bh[0:7]
        # print(bh1+";"+bh2+";"+bh)
        return bh1 + ";" + bh2 + ";" + bh3 + ";" + bh4 + ";" + bh
    if len(bh) == 7:
        bh1 = bh[0:1]
        bh2 = bh[0:3]
        bh3 = bh[0:5]
        # print(bh1+";"+bh2+";"+bh)
        return str(bh1) + ";" + str(bh2) + ";" + str(bh3) + ";" + str(bh)
    if len(bh) == 5:
        bh1 = bh[0:1]
        bh2 = bh[0:3]
        return str(bh1) + ";" + str(bh2) + ";" + str(bh)
    if len(bh) == 3:
        bh1 = bh[0:1]
        return str(bh1) + ";" + str(bh)
    if len(bh) == 1:
        return bh


def pzbmbhcl(bh):
    if len(bh) == 9:
        bh1 = bh[0:1]
        bh2 = bh[0:3]
        bh3 = bh[0:5]
        # print(bh1+";"+bh2+";"+bh)
        return bh1 + ";" + bh2 + ";" + bh3 + ";" + bh
    if len(bh) == 6:
        bh1 = bh[0:1]
        bh2 = bh[0:3]
        bh3 = bh[0:5]
        # print(bh1+";"+bh2+";"+bh)
        return bh1 + ";" + bh2 + ";" + bh3 + ";" + bh
    if len(bh) == 5:
        bh1 = bh[0:1]
        bh2 = bh[0:3]
        return bh1 + ";" + bh2 + ";" + bh
    if len(bh) == 3:
        bh1 = bh[0:1]
        return bh1 + ";" + bh
    if len(bh) == 1:
        return bh


def xljbbhcl(bh):
    if len(bh) == 6:
        bh1 = bh[0:4]
        return bh1 + ";" + bh
    if len(bh) == 4:
        return bh


def fglbbhcl(bh):
    if len(bh) == 9:
        bh0=bh[0]
        bh1 = bh[0:3]
        bh2 = bh[0:5]
        return bh0+ ";"+bh1 + ";" + bh2 + ";" + bh
    if len(bh) == 8:
        bh1 = bh[0:3]
        bh2 = bh[0:5]
        return bh1 + ";" + bh2 + ";" + bh
    if len(bh) == 7:
        bh1 = bh[0:3]
        bh2 = bh[0:5]
        return bh1 + ";" + bh2 + ";" + bh
    if len(bh) == 5:
        bh1 = bh[0:3]
        return bh1 + ";" + bh
    if len(bh) == 3:
        return bh
    if len(bh) == 2:
        return bh


def wsflbhcl(bh):
    if len(bh) == 15:
        bh1 = bh[0:3]
        bh2 = bh[0:6]
        bh3=bh[0:9]
        bh4 = bh[0:12]
        return bh1 + ";" + bh2 + ";"+ bh3 + ";" + bh4 + ";"+ bh
    if len(bh) == 12:
        bh1 = bh[0:3]
        bh2 = bh[0:6]
        bh3=bh[0:9]
        return bh1 + ";" + bh2 + ";"+ bh3 + ";" + bh
    if len(bh) == 9:
        bh1 = bh[0:3]
        bh2 = bh[0:6]
        return bh1 + ";" + bh2 + ";" + bh
    if len(bh) == 6:
        bh1 = bh[0:3]
        return bh1 + ";" + bh
    if len(bh) == 3:
        return bh


def htflbhcl(bh):
    if len(bh) == 9:
        bh1 = bh[0:3]
        bh2 = bh[0:6]
        return bh1 + ";" + bh2 + ";" + bh
    if len(bh) == 6:
        bh1 = bh[0:3]
        return bh1 + ";" + bh
    if len(bh) == 3:
        return bh


def gfhtbhcl(bh):
    if len(bh) == 10:
        bh1 = bh[0:1]
        bh2 = bh[0:4]
        bh3 = bh[0:7]
        # print(bh1+";"+bh2+";"+bh)
        return bh1 + ";" + bh2 + ";" + bh3 + ";" + bh
    if len(bh) == 9:
        bh1 = bh[0:1]
        bh2 = bh[0:3]
        bh3 = bh[0:5]
        # print(bh1+";"+bh2+";"+bh)
        return bh1 + ";" + bh2 + ";" + bh3 + ";" + bh
    if len(bh) == 7:
        if bh[0:1] == "b":
            bh1 = bh[0:1]
            bh2 = bh[0:4]
            return bh1 + ";" + bh2 + ";" + bh
        else:
            bh1 = bh[0:1]
            bh2 = bh[0:3]
            bh3 = bh[0:5]
            # print(bh1+";"+bh2+";"+bh)
            return bh1 + ";" + bh2 + ";" + bh3 + ";" + bh
    if len(bh) == 5:
        bh1 = bh[0:1]
        bh2 = bh[0:3]
        return bh1 + ";" + bh2 + ";" + bh
    if len(bh) == 4:
        bh1 = bh[0:1]
        return bh1 + ";" + bh
    if len(bh) == 3:
        bh1 = bh[0:1]
        return bh1 + ";" + bh
    if len(bh) == 1:
        return bh


def hylbbhcl(bh):
    if len(bh) == 3:
        return bh


def lbbhcl(bh):
    if len(bh) == 6:
        bh1 = bh[0:3]
        return bh1 + ";" + bh
    if len(bh) == 3:
        return bh


def aybhcl(bh):
    if len(bh) == 11:
        bh1 = bh[0:3]
        bh2 = bh[0:5]
        bh3 = bh[0:7]
        bh4 = bh[0:9]
        # print(bh1+";"+bh2+";"+bh)
        return bh1 + ";" + bh2 + ";" + bh3 + ";" + bh4 + ";" + bh
    if len(bh) == 9:
        bh1 = bh[0:3]
        bh2 = bh[0:5]
        bh3 = bh[0:7]
        # print(bh1+";"+bh2+";"+bh)
        return bh1 + ";" + bh2 + ";" + bh3 + ";" + bh
    if len(bh) == 7:
        bh1 = bh[0:3]
        bh2 = bh[0:5]
        # print(bh1+";"+bh2+";"+bh)
        return bh1 + ";" + bh2 + ";" + bh
    if len(bh) == 5:
        bh1 = bh[0:3]
        return bh1 + ";" + bh
    if len(bh) == 3:
        return bh


def slfybhcl(bh):
    if len(bh) == 6:
        bh1 = bh[0:2]
        bh2 = bh[0:4]
        # print(bh1+";"+bh2+";"+bh)
        return bh1 + ";" + bh2 + ";" + bh
    if len(bh) == 4:
        bh1 = bh[0:2]
        return bh1 + ";" + bh
    if len(bh) == 2:
        return bh


def altzbhcl(bh):
    if len(bh) == 3:
        return bh


def cjjgbhcl(bh):
    if len(bh) == 5:
        return bh


def zcflbhcl(bh):
    if len(bh) == 4:
        bh1 = bh[0:2]
        return bh1 + ";" + bh
    if len(bh) == 2:
        return bh


def qzgjcbhcl(bh):
    if len(bh) == 10:
        bh1 = bh[0:2]
        bh2 = bh[0:4]
        bh3 = bh[0:6]
        bh4 = bh[0:8]
        return bh1 + ";" + bh2 + ";" + bh3 + ";" + bh4 + ";" + bh
    if len(bh) == 8:
        bh1 = bh[0:2]
        bh2 = bh[0:4]
        bh3 = bh[0:6]
        return bh1 + ";" + bh2 + ";" + bh3 + ";" + bh
    if len(bh) == 6:
        bh1 = bh[0:2]
        bh2 = bh[0:4]
        return bh1 + ";" + bh2 + ";" + bh
    if len(bh) == 4:
        bh1 = bh[0:2]
        return bh1 + ";" + bh
    if len(bh) == 2:
        return bh


def slcxbhcl(bh):

    if len(bh) == 3:
        return bh


def ajlxbhcl(bh):
    if len(bh) == 9:
        bh1 = bh[0:3]
        bh2 = bh[0:6]
        return bh1 + ";" + bh2 + ";" + bh
    if len(bh) == 6:
        bh1 = bh[0:3]
        return bh1 + ";" + bh
    if len(bh) == 3:
        return bh


def wslxbhcl(bh):
    if len(bh) == 3:
        return bh


def zkzmbhcl(bh):
    if len(bh) == 9:
        bh1 = bh[0:3]
        bh2 = bh[0:5]
        bh3 = bh[0:7]
        # print(bh1+";"+bh2+";"+bh)
        return bh1 + ";" + bh2 + ";" + bh3 + ";" + bh
    if len(bh) == 7:
        bh1 = bh[0:3]
        bh2 = bh[0:5]
        return bh1 + ";" + bh2 + ";" + bh
    if len(bh) == 5:
        bh1 = bh[0:3]
        return bh1 + ";" + bh
    if len(bh) == 3:
        return bh


def pdzmbhcl(bh):
    if len(bh) == 9:
        bh1 = bh[0:3]
        bh2 = bh[0:5]
        bh3 = bh[0:7]
        # print(bh1+";"+bh2+";"+bh)
        return bh1 + ";" + bh2 + ";" + bh3 + ";" + bh
    if len(bh) == 7:
        bh1 = bh[0:3]
        bh2 = bh[0:5]
        return bh1 + ";" + bh2 + ";" + bh
    if len(bh) == 5:
        bh1 = bh[0:3]
        return bh1 + ";" + bh
    if len(bh) == 3:
        return bh




def bhqc(bhs):
    bhs2 = ""
    for fbbmid1 in bhs.split(';'):
        pd = True
        for fbbmid2 in bhs2.split(';'):
            if fbbmid1 == fbbmid2:
                pd = False
        if pd:
            bhs2 += fbbmid1 + ";"
    bhs = bhs2[0:len(bhs2) - 1]
    return bhs


def fbbmbhwzcl(fbbm):
    fbbmbhs2 = ""
    for fbbma in fbbm.find_all('a'):
        fbbmbh = fbbma.get('href')
        pipe = re.compile('ClassCodeKey')
        pipe2 = re.compile('whitebook')
        pipe3 = re.compile('Category|TrialStep|DocumentAttr|CriminalPunish|Accusation|LastInstanceCourt|CaseClass|IssueDepartment')
        if pipe2.findall(fbbmbh.split('=')[0]):
            fbbmbh = fbbmbh.split('=')[1].split(',')[0]
            if '&' in fbbmbh:
                fbbmbh = fbbmbh.split('&')[0]
            fbbmbhs2 += fbbmbhcl(fbbmbh) + ";"
        elif pipe.findall(fbbmbh):
            fbbmbh = fbbmbh.split(',')[2]
            if '&' in fbbmbh:
                fbbmbh = fbbmbh.split('&')[0]
            fbbmbhs2 += fbbmbhcl(fbbmbh) + ";"
        if pipe3.findall(fbbmbh.split('=')[0]):
            fbbmbh = fbbmbh.split('=')[1]
            fbbmbh=fbbmbh
            if '&' in fbbmbh:
                fbbmbh = fbbmbh.split('&')[0]
            #fbbmbh = re.sub(r"[A-Za-z]", "", fbbmbh)
            try:
                fbbmbhs2 += fbbmbhcl(fbbmbh) + ";"
            except Exception as e:
                print(e)
                print()
        elif pipe3.findall(fbbmbh):
            fbbmbh = fbbmbh.split(',')[2]
            if '&' in fbbmbh:
                fbbmbh = fbbmbh.split('&')[0]
            fbbmbhs2 += fbbmbhcl(fbbmbh) + ";"
    fbbmbhs = fbbmbhs2[0:len(fbbmbhs2) - 1]
    fbbmbhs = bhqc(fbbmbhs)
    return fbbmbhs


def sxxbhwzcl(sxx):
    sxxbhs2 = ""
    for sxxa in sxx.find_all('a'):
        sxxbh = sxxa.get('href')
        pipe = re.compile('ClassCodeKey')
        pipe3 = re.compile('Category|TrialStep|DocumentAttr|CriminalPunish|Accusation|LastInstanceCourt|CaseClass|TimelinessDic')
        if pipe.findall(sxxbh):
            sxxbh = sxxbh.split(',')[3]
            if '&' in sxxbh:
                sxxbh = sxxbh.split('&')[0]
            sxxbhs2 += sxxbh + ";"
        if pipe3.findall(sxxbh):
            sxxbh = sxxbh.split('=')[1]
            if '&' in sxxbh:
                sxxbh = sxxbh.split('&')[0]
            sxxbhs2 += sxxbh + ";"
    sxxbhs = sxxbhs2[0:len(sxxbhs2) - 1]
    sxxbhs = bhqc(sxxbhs)
    return sxxbhs


def xljbbhwzcl(xljb):
    xljbbhs2 = ""
    for xljba in xljb.find_all('a'):
        xljbbh = xljba.get('href')
        pipe = re.compile('ClassCodeKey')
        pipe3 = re.compile('Category|TrialStep|DocumentAttr|CriminalPunish|Accusation|LastInstanceCourt|CaseClass|EffectivenessDic')
        if pipe.findall(xljbbh):
            xljbbh = xljbbh.split(',')[1]
            if '&' in xljbbh:
                xljbbh = xljbbh.split('&')[0]
            xljbbhs2 += xljbbhcl(xljbbh) + ";"

        if pipe3.findall(xljbbh):
            xljbbh = xljbbh.split('=')[1]
            if '&' in xljbbh:
                xljbbh = xljbbh.split('&')[0]
            xljbbhs2 += xljbbhcl(xljbbh) + ";"

    xljbbhs = xljbbhs2[0:len(xljbbhs2) - 1]
    xljbbhs = bhqc(xljbbhs)
    return xljbbhs


def fglbbhwzcl(fglb):
    fglbbhs2 = ""
    for fglba in fglb.find_all('a'):
        fglbbh = fglba.get('href')
        pipe = re.compile('ClassCodeKey')
        pipe3 = re.compile('Category|TrialStep|DocumentAttr|CriminalPunish|Accusation|LastInstanceCourt|CaseClass')
        if pipe.findall(fglbbh):
            fglbbh = fglbbh.split(',')[4]
            if '&' in fglbbh:
                fglbbh = fglbbh.split('&')[0]
            fglbbhs2 += fglbbhcl(fglbbh) + ";"
        if pipe3.findall(fglbbh):
            fglbbh = fglbbh.split('=')[1]
            if '&' in fglbbh:
                fglbbh = fglbbh.split('&')[0]
            fglbbhs2 += fglbbhcl(fglbbh) + ";"

    fglbbhs = fglbbhs2[0:len(fglbbhs2) - 1]
    fglbbhs = bhqc(fglbbhs)
    return fglbbhs


def pzbmbhwzcl(pzbm):
    pzbmbhs2 = ""
    for pzbma in pzbm.find_all('a'):
        pzbmbh = pzbma.get('href')
        pipe = re.compile('RatifyDepartment')
        pipe3 = re.compile('Category|TrialStep|DocumentAttr|CriminalPunish|Accusation|LastInstanceCourt|CaseClass')
        if pipe.findall(pzbmbh):
            pzbmbh = pzbmbh.split('=')[1]
            if '&' in pzbmbh:
                pzbmbh = pzbmbh.split('&')[0]
            pzbmbhs2 += pzbmbhcl(pzbmbh) + ";"

        if pipe3.findall(pzbmbh):
            pzbmbh = pzbmbh.split('=')[1]
            if '&' in pzbmbh:
                pzbmbh = pzbmbh.split('&')[0]
            pzbmbhs2 += pzbmbhcl(pzbmbh) + ";"

    pzbmbhs = pzbmbhs2[0:len(pzbmbhs2) - 1]
    pzbmbhs = bhqc(pzbmbhs)
    return pzbmbhs


def wsflbhwzcl(wsfl):
    wsflbhs2 = ""
    for wsfla in wsfl.find_all('a'):
        wsflbh = wsfla.get('href')
        pipe = re.compile('RatifyDepartment')
        pipe3 = re.compile('Category|TrialStep|DocumentAttr|CriminalPunish|Accusation|LastInstanceCourt|CaseClass')
        if pipe.findall(wsflbh):
            wsflbh = wsflbh.split('=')[1]
            wsflbhs2 += wsflbhcl(wsflbh) + ";"
        if pipe3.findall(wsflbh):
            try:
                wsflbh = wsflbh.split('=')[1]
                if '&' in wsflbh:
                    wsflbh = wsflbh.split('&')[0]
                wsflbhs2 += wsflbhcl(wsflbh) + ";"
            except Exception as e:
                print(e)
                print()

    wsflbhs = wsflbhs2[0:len(wsflbhs2) - 1]
    wsflbhs = bhqc(wsflbhs)
    return wsflbhs


def htflbhwzcl(htfl):
    htflbhs2 = ""
    for htfla in htfl.find_all('a'):
        htflbh = htfla.get('href')
        pipe = re.compile('ClassCodeKey')
        pipe3 = re.compile('Category|TrialStep|DocumentAttr|CriminalPunish|Accusation|LastInstanceCourt|CaseClass')
        if pipe.findall(htflbh):
            htflbh = htflbh.split('=')[1].split(',')[0]
            if '&' in htflbh:
                htflbh = htflbh.split('&')[0]
            htflbhs2 += htflbhcl(htflbh) + ";"
        if pipe3.findall(htflbh):
            htflbh = htflbh.split('=')[1]
            if '&' in htflbh:
                htflbh = htflbh.split('&')[0]
            htflbhs2 += htflbhcl(htflbh) + ";"

    htflbhs = htflbhs2[0:len(htflbhs2) - 1]
    htflbhs = bhqc(htflbhs)
    return htflbhs


def gfhtbhwzcl(gfht):
    gfhtbhs2 = ""
    for gfhta in gfht.find_all('a'):
        gfhtbh = gfhta.get('href')
        pipe = re.compile('ClassCodeKey')
        pipe3 = re.compile('Category|TrialStep|DocumentAttr|CriminalPunish|Accusation|LastInstanceCourt|CaseClass')
        if pipe.findall(gfhtbh):
            gfhtbh = gfhtbh.split('=')[1].split(',')[1]
            if '&' in gfhtbh:
                gfhtbh = gfhtbh.split('&')[0]
            gfhtbhs2 += gfhtbhcl(gfhtbh) + ";"
        if pipe3.findall(gfhtbh):
            gfhtbh = gfhtbh.split('=')[1]
            if '&' in gfhtbh:
                gfhtbh = gfhtbh.split('&')[0]
            gfhtbhs2 += gfhtbhcl(gfhtbh) + ";"

    gfhtbhs = gfhtbhs2[0:len(gfhtbhs2) - 1]
    gfhtbhs = bhqc(gfhtbhs)
    return gfhtbhs


def hylbbhwzcl(hylb):
    hylbbhs2 = ""
    for hylba in hylb.find_all('a'):
        hylbbh = hylba.get('href')
        pipe = re.compile('ClassCodeKey')
        pipe3 = re.compile('Category|TrialStep|DocumentAttr|CriminalPunish|Accusation|LastInstanceCourt|CaseClass')
        if pipe.findall(hylbbh):
            hylbbh = hylbbh.split('=')[1].split(',')[2]
            hylbbhs2 += hylbbhcl(hylbbh) + ";"

        if pipe3.findall(hylbbh):
            hylbbh = hylbbh.split('=')[1]
            if '&' in hylbbh:
                hylbbh = hylbbh.split('&')[0]
            hylbbhs2 += hylbbhcl(hylbbh) + ";"

    hylbbhs = hylbbhs2[0:len(hylbbhs2) - 1]
    hylbbhs = bhqc(hylbbhs)
    return hylbbhs


def lbbhwzcl(lb):
    lbbhs2 = ""
    for lba in lb.find_all('a'):
        lbbh = lba.get('href')
        pipe = re.compile('ClassCodeKey')
        pipe2 = re.compile('whitebook')
        pipe3 = re.compile('Category|TrialStep|DocumentAttr|CriminalPunish|Accusation|LastInstanceCourt|CaseClass')
        if pipe2.findall(lbbh.split('=')[0]):
            lbbh = lbbh.split('=')[1].split(',')[1]
            if '&' in lbbh:
                lbbh = lbbh.split('&')[0]
            lbbhs2 += lbbhcl(lbbh) + ";"
        if pipe.findall(lbbh):
            lbbh = lbbh.split('=')[1].split(',')[3].split('&')[0]
            if '&' in lbbh:
                lbbh = lbbh.split('&')[0]
            lbbhs2 += lbbhcl(lbbh) + ";"
        if pipe3.findall(lbbh):
            lbbh = lbbh.split('=')[1]
            if '&' in lbbh:
                lbbh = lbbh.split('&')[0]
            lbbhs2 += lbbhcl(lbbh) + ";"

    lbbhs = lbbhs2[0:len(lbbhs2) - 1]
    lbbhs = bhqc(lbbhs)
    return lbbhs


def aybhwzcl(ay):
    aybhs2 = ""
    aybhb=""
    # for aya in ay.find_all('a'):
    #     aybh = aya.get('href')
    #     pipe = re.compile('ClassCodeKey')
    #     pipe3 = re.compile('Category|TrialStep|DocumentAttr|CriminalPunish|Accusation|LastInstanceCourt|CaseClass|CategoryNew')
    #     pipe2=re.compile('CategoryNew')
    #     if pipe.findall(aybh):
    #         aybh = aybh.split('=')[1].split(',')[0]
    #         aybhs2 += aybhcl(aybh) + ";"
        # if pipe3.findall(aybh):
        #     aybh = aybh.split('=')[1]
        #     if '&' in aybh:
        #         aybh = aybh.split('&')[0]
        #     a=aybhcl(aybh)
        #     if a is None:
        #         aybhs2=";"
        #     else:
        #         aybhs2 += aybhcl(aybh) + ";"
        #
        # if pipe2.findall(aybh):
        #     aybh = aybh.split('=')[1]
        #     if '&' in aybh:
        #         aybh = aybh.split('&')[0]
    text=ay.text
    aybh=str(text).split('>')
    aybh1=aybh[-1]
    aybh1=aybh1.replace(' ','')
    sql="SELECT TOP 10 * FROM [FddLaw5.0].[dbo].[menus] WHERE [value] = "+"'"+aybh1+"'"+" AND [menuname] = N'pfnl_anyou_id'"
    info=selectsqls(sql)
    try:
        if len(info)==0 or info=='':
            aybh2 = aybh[-2]
            aybh2 = aybh2.replace(' ', '')
            sql = "SELECT TOP 10 * FROM [FddLaw5.0].[dbo].[menus] WHERE [value] = " + "'" + aybh2 + "'" + " AND [menuname] = N'pfnl_anyou_id'"
            info = selectsqls(sql)
        aybh=info[0][0]
        aybhs2 += aybhcl(aybh) + ";"
        aybhs = aybhs2[0:len(aybhs2) - 1]
        aybhs = bhqc(aybhs)
        aybhb=aybhb+aybhs+';'
    except Exception as e:
        print(e)
    return aybhb[:-1]


def slfybhwzcl(slfy):
    slfybhs2 = ""
    for slfya in slfy.find_all('a'):
        slfybh = slfya.get('href')
        pipe = re.compile('ClassCodeKey')
        pipe2 = re.compile('pfnl')
        pipe3 = re.compile('Category|TrialStep|DocumentAttr|CriminalPunish|Accusation|LastInstanceCourt|CaseClass')
        if pipe2.findall(slfybh):
            try:
                slfybh = slfybh.split('=')[1]
            except Exception as e:
                continue
            if '&' in slfybh:
                slfybh = slfybh.split('&')[0]
            slfybhs2 += slfybhcl(slfybh) + ";"
        elif pipe.findall(slfybh):
            slfybhf = slfybh.split('=')[1].split(',')[3]
            try:
                slfybhs2 += slfybhcl(slfybhf) + ";"
            except Exception as e:
                slfybhf = slfybh.split('=')[1].split(',')[5]
                slfybhs2 += slfybhcl(slfybhf) + ";"

        if pipe3.findall(slfybh):
            slfybh = slfybh.split('=')[1]
            if '&' in slfybh:
                slfybh = slfybh.split('&')[0]
            slfybhs2 += slfybhcl(slfybh) + ";"
        elif pipe.findall(slfybh):
            slfybhf = slfybh.split('=')[1]
            if '&' in slfybhf:
                slfybhf = slfybhf.split('&')[0]
            try:
                slfybhs2 += slfybhcl(slfybhf) + ";"
            except Exception as e:
                slfybhf = slfybh.split('=')[1]
                slfybhs2 += slfybhcl(slfybhf) + ";"

    slfybhs = slfybhs2[0:len(slfybhs2) - 1]
    slfybhs = bhqc(slfybhs)
    return slfybhs


def altzbhwzcl(altz):
    altzbhs2 = ""
    for altza in altz.find_all('a'):
        altzbh = altza.get('href')
        pipe = re.compile('ClassCodeKey')
        pipe3 = re.compile('Category|TrialStep|DocumentAttr|CriminalPunish|Accusation|LastInstanceCourt|CaseClass')
        if pipe.findall(altzbh):
            altzbh = altzbh.split('=')[1].split(',')[1]
            altzbhs2 += altzbhcl(altzbh) + ";"
        if pipe3.findall(altzbh):
            altzbh = altzbh.split('=')[1]
            if '&' in altzbh:
                altzbh = altzbh.split('&')[0]
            altzbhs2 += altzbhcl(altzbh) + ";"

    altzbhs = altzbhs2[0:len(altzbhs2) - 1]
    altzbhs = bhqc(altzbhs)
    return altzbhs


def cjjgbhwzcl(cjjg):
    cjjgbhs2 = ""
    for cjjga in cjjg.find_all('a'):
        cjjgbh = cjjga.get('href')
        pipe = re.compile('ClassCodeKey')
        pipe3 = re.compile('Category|TrialStep|DocumentAttr|CriminalPunish|Accusation|LastInstanceCourt|CaseClass')
        if pipe.findall(cjjgbh):
            cjjgbh = cjjgbh.split('=')[1].split(',')[1]
            cjjgbhs2 += cjjgbhcl(cjjgbh) + ";"
        if pipe3.findall(cjjgbh):
            cjjgbh = cjjgbh.split('=')[1]
            if '&' in cjjgbh:
                cjjgbh = cjjgbh.split('&')[0]
            cjjgbhs2 += cjjgbhcl(cjjgbh) + ";"

    cjjgbhs = cjjgbhs2[0:len(cjjgbhs2) - 1]
    cjjgbhs = bhqc(cjjgbhs)
    return cjjgbhs


def zcflbhwzcl(zcfl):
    zcflbhs2 = ""
    for zcfla in zcfl.find_all('a'):
        zcflbh = zcfla.get('href')
        pipe = re.compile('ClassCodeKey')
        pipe3 = re.compile('Category|TrialStep|DocumentAttr|CriminalPunish|Accusation|LastInstanceCourt|CaseClass')
        if pipe.findall(zcflbh):
            zcflbh = zcflbh.split('=')[1].split(',')[1]
            zcflbhs2 += zcflbhcl(zcflbh) + ";"
        if pipe3.findall(zcflbh):
            zcflbh = zcflbh.split('=')[1]
            if '&' in zcflbh:
                zcflbh = zcflbh.split('&')[0]
            zcflbhs2 += zcflbhcl(zcflbh) + ";"


    zcflbhs = zcflbhs2[0:len(zcflbhs2) - 1]
    zcflbhs = bhqc(zcflbhs)
    return zcflbhs


def qzgjcbhwzcl(qzgjc):
    qzgjcbhs2 = ""
    for qzgjca in qzgjc.find_all('a'):
        qzgjcbh = qzgjca.get('href')
        pipe = re.compile('CriminalPunish')
        pipe3 = re.compile('Category|TrialStep|DocumentAttr|CriminalPunish|Accusation|LastInstanceCourt|CaseClass')
        if pipe.findall(qzgjcbh):
            qzgjcbh = qzgjcbh.split('=')[1]
            if '&' in qzgjcbh:
                qzgjcbh = qzgjcbh.split('&')[0]
            qzgjcbhs2 += qzgjcbhcl(qzgjcbh) + ";"
        if pipe3.findall(qzgjcbh):
                    qzgjcbh = qzgjcbh.split('=')[1]
                    if '&' in qzgjcbh:
                        qzgjcbh = qzgjcbh.split('&')[0]
                    qzgjcbhs2 += qzgjcbhcl(qzgjcbh) + ";"

    qzgjcbhs = qzgjcbhs2[0:len(qzgjcbhs2) - 1]
    qzgjcbhs = bhqc(qzgjcbhs)
    return qzgjcbhs


def slcxbhwzcl(slcx):
    slcxbhs2 = ""
    for slcxa in slcx.find_all('a'):
        slcxbh = slcxa.get('href')
        pipe = re.compile('ClassCodeKey')
        pipe3 = re.compile('Category|TrialStep|DocumentAttr|CriminalPunish|Accusation|LastInstanceCourt|CaseClass')
        if pipe.findall(slcxbh):
            slcxbhf = slcxbh.split('=')[1].split(',')[5]
            try:
                slcxbhs2 += slcxbhcl(slcxbhf) + ";"
            except Exception as e:
                slcxbhf = slcxbh.split('=')[1].split(',')[6]
                if '&' in slcxbhf:
                    slcxbhf = slcxbhf.split('&')[0]
                slcxbhs2 += slcxbhcl(slcxbhf) + ";"
        if pipe3.findall(slcxbh):
            slcxbhf = slcxbh.split('=')[1]
            try:
                slcxbhs2 += slcxbhcl(slcxbhf) + ";"
            except Exception as e:
                slcxbhf = slcxbh.split('=')[1]
                if '&' in slcxbhf:
                    slcxbhf = slcxbhf.split('&')[0]
                slcxbhs2 += slcxbhcl(slcxbhf) + ";"
    slcxbhs = slcxbhs2[0:len(slcxbhs2) - 1]
    slcxbhs = bhqc(slcxbhs)
    return slcxbhs


def ajlxbhwzcl(ajlx):
    ajlxbhs2 = ""
    for ajlxa in ajlx.find_all('a'):
        ajlxbh = ajlxa.get('href')
        pipe = re.compile('ClassCodeKey')
        pipe3 = re.compile('Category|TrialStep|DocumentAttr|CriminalPunish|Accusation|LastInstanceCourt|CaseClass')
        if pipe.findall(ajlxbh):
            ajlxbhf = ajlxbh.split('=')[1].split(',')[2]
            try:
                ajlxbhs2 += ajlxbhcl(ajlxbhf) + ";"
            except Exception as e:
                ajlxbhf = ajlxbh.split('=')[1].split(',')[3]
                ajlxbhs2 += ajlxbhcl(ajlxbhf) + ";"
        if pipe3.findall(ajlxbh):
            ajlxbhf = ajlxbh.split('=')[1]
            try:
                ajlxbhs2 += ajlxbhcl(ajlxbhf) + ";"
            except Exception as e:
                ajlxbhf = ajlxbh.split('=')[1]
                if '&' in ajlxbhf:
                    ajlxbhf = ajlxbhf.split('&')[0]
                ajlxbhs2 += ajlxbhcl(ajlxbhf) + ";"
    ajlxbhs = ajlxbhs2[0:len(ajlxbhs2) - 1]
    ajlxbhs = bhqc(ajlxbhs)
    return ajlxbhs


def wslxbhwzcl(wslx):
    wslxbhs2 = ""
    for wslxa in wslx.find_all('a'):
        wslxbh = wslxa.get('href')
        pipe = re.compile('ClassCodeKey')
        pipe3 = re.compile('Category|TrialStep|DocumentAttr|CriminalPunish|Accusation|LastInstanceCourt|CaseClass')
        if pipe.findall(wslxbh):
            wslxbhf = wslxbh.split('=')[1].split(',')[6]
            try:
                wslxbhs2 += wslxbhcl(wslxbhf) + ";"
            except Exception as e:
                wslxbhf = wslxbh.split('=')[1].split(',')[7]
                wslxbhs2 += wslxbhcl(wslxbhf) + ";"
        if pipe3.findall(wslxbh):
            wslxbhf = wslxbh.split('=')[1]
            try:
                wslxbhs2 += wslxbhcl(wslxbhf) + ";"
            except Exception as e:
                wslxbhf = wslxbh.split('=')[1]
                if '&' in wslxbhf:
                    wslxbhf = wslxbhf.split('&')[0]
                if wslxbhcl(wslxbhf) is None:
                    wslxbhs2=";"
                else:
                 wslxbhs2 += wslxbhcl(wslxbhf) + ";"
    wslxbhs = wslxbhs2[0:len(wslxbhs2) - 1]
    wslxbhs = bhqc(wslxbhs)
    return wslxbhs


def zkzmbhwzcl(zkzm):
    zkzmbhs2 = ""
    for zkzma in zkzm.find_all('a'):
        zkzmbh = zkzma.get('href')
        pipe = re.compile('ClassCodeKey')
        pipe3 = re.compile('Category|TrialStep|DocumentAttr|CriminalPunish|Accusation|LastInstanceCourt|CaseClass')
        if pipe.findall(zkzmbh):
            zkzmbh = zkzmbh.split('=')[1].split(',')[0]
            zkzmbhs2 += zkzmbhcl(zkzmbh) + ";"
        if pipe3.findall(zkzmbh):
            zkzmbh = zkzmbh.split('=')[1]
            if '&' in zkzmbh:
                zkzmbh = zkzmbh.split('&')[0]
            if zkzmbhcl(zkzmbh) is None:
                zkzmbhs2= ";"
            else:
                zkzmbhs2 += zkzmbhcl(zkzmbh) + ";"

    zkzmbhs = zkzmbhs2[0:len(zkzmbhs2) - 1]
    zkzmbhs = bhqc(zkzmbhs)
    return zkzmbhs


def pdzmbhwzcl(pdzm):
    pdzmbhs2 = ""
    for pdzma in pdzm.find_all('a'):
        pdzmbh = pdzma.get('href')
        pipe = re.compile('Accusation')
        pipe3 = re.compile('Category|TrialStep|DocumentAttr|CriminalPunish|Accusation|LastInstanceCourt|CaseClass')
        if pipe.findall(pdzmbh):
            pdzmbh = pdzmbh.split('=')[1]
            pdzmbhs2 += pdzmbhcl(pdzmbh) + ";"
        if pipe3.findall(pdzmbh):
            pdzmbh = pdzmbh.split('=')[1]
            if '&' in pdzmbh:
                pdzmbh = pdzmbh.split('&')[0]
            pdzmbhs2 += pdzmbhcl(pdzmbh) + ";"
    pdzmbhs = pdzmbhs2[0:len(pdzmbhs2) - 1]
    pdzmbhs = bhqc(pdzmbhs)
    return pdzmbhs
