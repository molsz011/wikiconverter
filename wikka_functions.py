from random import random
from _datetime import datetime
from hashlib import sha1
from jamwiki_functions import time_mw_to_jam as time_mw_to_wikka
from jamwiki_functions import mediawiki_time
import os
from shutil import copy2, rmtree
from hashlib import md5
from PIL import Image
from re import sub
from mediawiki_functions import capitalize_words

def wikka_get_max_page_id(session, Page):
    ids = []
    for page in session.query(Page).all():
        ids.append(page.id)
    return max(ids)

def wikka_pages_to_dict(session, Base):
    pages = []
    revs = []
    texts = []
    Page = Base.classes.wikka_pages
    next_page_id = 1
    next_rev_id = 1
    next_text_id = 1
    queried_pages = session.query(Page).all()
    pages_links = []
    for page in queried_pages:
        pages_links.append(page.title)

    for page in queried_pages:
        if page.user == 'WikkaInstaller' or page.latest is 'N':
            continue
        tag = page.tag
        tempdict = {}
        tempdict['page_id'] = next_page_id
        tempdict['page_namespace'] = 0
        tempdict['page_title'] = bytes(str.replace(page.title, ' ', '_').title(), 'utf-8')
        tempdict['page_restrictions'] = bytes('', 'utf-8')
        tempdict['page_is_redirect'] = 0
        tempdict['page_is_new'] = 0
        tempdict['page_random'] = random()
        tempdict['page_touched'] = bytes(mediawiki_time(page.time), 'utf-8')
        tempdict['page_links_updated'] = None
        tempdict['page_latest'] = next_rev_id
        tempdict['page_len'] = len(page.body)
        tempdict['page_content_model'] = b'wikitext'
        tempdict['page_lang'] = None
        pages.append(tempdict)
        temprev = {}
        temprev['rev_id'] = next_rev_id
        temprev['rev_page'] = next_page_id
        temprev['rev_text_id'] = next_text_id
        temprev['rev_comment'] = bytes(page.note, 'utf-8')
        temprev['rev_user'] = 0
        temprev['rev_user_text'] = bytes(page.user, 'utf-8')
        temprev['rev_timestamp'] = bytes(mediawiki_time(page.time), 'utf-8')
        temprev['rev_version'] = 0
        temprev['rev_previous'] = None
        temprev['rev_char_changed'] = 0
        temprev['rev_minor_edit'] = 0
        temprev['rev_deleted'] = 0
        temprev['rev_len'] = len(page.body)
        temprev['rev_parent_id'] = 0
        temprev['rev_sha1'] = bytes(sha1(bytes(page.title, 'utf-8')).hexdigest(), 'utf-8')
        temprev['rev_content_model'] = None
        temprev['rev_content_format'] = None
        revs.append(temprev)
        temptext = {}
        temptext['old_id'] = next_text_id
        temptext['old_text'] = bytes(wikka_text_to_mediawiki(page.body, pages_links), 'utf-8')
        temptext['old_flags'] = bytes('utf-8', 'utf-8')
        texts.append(temptext)
        next_rev_id += 1
        next_text_id += 1
        version = 1
        for page2 in queried_pages:
            if page2.latest is 'N' and page2.tag == tag:
                temprev = {}
                temprev['rev_id'] = next_rev_id
                temprev['rev_page'] = next_page_id
                temprev['rev_text_id'] = next_text_id
                temprev['rev_comment'] = bytes(page2.note, 'utf-8')
                temprev['rev_user'] = 0
                temprev['rev_user_text'] = bytes(page2.user, 'utf-8')
                temprev['rev_timestamp'] = bytes(mediawiki_time(page2.time), 'utf-8')
                temprev['rev_version'] = version
                temprev['rev_previous'] = None
                temprev['rev_char_changed'] = 0
                temprev['rev_minor_edit'] = 0
                temprev['rev_deleted'] = 0
                temprev['rev_len'] = len(page2.body)
                temprev['rev_parent_id'] = 0
                temprev['rev_sha1'] = bytes(sha1(bytes(page2.title, 'utf-8')).hexdigest(), 'utf-8')
                temprev['rev_content_model'] = None
                temprev['rev_content_format'] = None
                revs.append(temprev)
                temptext = {}
                temptext['old_id'] = next_text_id
                temptext['old_text'] = bytes(wikka_text_to_mediawiki(page2.body, pages_links), 'utf-8')
                temptext['old_flags'] = bytes('utf-8', 'utf-8')
                texts.append(temptext)
                next_text_id += 1
                next_rev_id += 1
                version += 1
        next_page_id += 1

    return {'pages': pages, 'revs': revs, 'texts': texts}

def wikka_dict_to_pages(session, Base, dicts):
    Page = Base.classes.wikka_pages
    max_page_id = wikka_get_max_page_id(session, Page)
    max_page2 = 0
    skip = []
    queried_pages = session.query(Page).all()
    for p in queried_pages:
        skip.append(p.tag)
    revs_done = []
    for page in dicts['pages']:
        title = str.replace(page['page_title'].decode(), '_', ' ')
        tag_ = str.replace(page['page_title'].decode(), '_', '')
        tag = str.replace(tag_, '-', '')
        while tag in skip:
            tag += 'Duplicate'
            title += 'Duplicate'
        skip.append(tag)

        for rev in dicts['revs']:
            if rev['rev_id'] == page['page_latest']:
                current_rev = rev
                revs_done.append(current_rev['rev_id'])
                break
        for text in dicts['texts']:
            if text['old_id'] == current_rev['rev_text_id']:
                text_data = text['old_text'].decode()
                break
        if text_data[:6] != '======':
            text_data = '====== ' + title + ' ======\n' + text_data
        new_page = Page(id=current_rev['rev_id']+max_page_id, tag=tag, title=title,
                        time=time_mw_to_wikka(page['page_touched'].decode()), body=mediawiki_text_to_wikka(text_data),
                        owner=current_rev['rev_user_text'].decode(), user=current_rev['rev_user_text'].decode(),
                        latest='Y', note=current_rev['rev_comment'].decode())
        session.add(new_page)
        if new_page.id > max_page2:
            max_page2 = new_page.id

    for rev in dicts['revs']:
        if rev['rev_id'] in revs_done:
            continue

        for page in dicts['pages']:
            if page['page_id'] == rev['rev_page']:
                current_page = page
                break

        for text in dicts['texts']:
            if text['old_id'] == rev['rev_text_id']:
                text_data = text['old_text'].decode()
                break

        title = str.replace(current_page['page_title'].decode(), '_', ' ')
        tag_ = str.replace(current_page['page_title'].decode(), '_', '')
        tag = str.replace(tag_, '-', '')
        while tag in skip:
            tag += 'Duplicate'
            title += '-Duplicate'

        if text_data[:6] != '======':
            text_data = '====== ' + title + ' ======\n' + text_data

        new_page = Page(id=rev['rev_id']+max_page_id, tag=tag, title=title,
                        time=time_mw_to_wikka(current_page['page_touched'].decode()),
                        body=mediawiki_text_to_wikka(text_data), owner=rev['rev_user_text'].decode(),
                        user=rev['rev_user_text'].decode(), latest='N', note=rev['rev_comment'].decode())
        session.add(new_page)

    session.commit()


def wikka_img_to_dict(path):
    path += '/'
    src = os.listdir(path)
    skip = ['.htaccess', 'icons', 'email.gif', 'feed.png', 'lock.gif', 'wikka_logo.jpg', 'xml.png']
    files = []
    npath = path + 'temp_folder/'
    if os.path.exists(npath):
        rmtree(npath)
    os.makedirs(npath)
    for file in src:
        if file in skip:
            continue
        if os.path.isdir(path+file):
            newpath2 = path + file + '/'
            newsrc2 = os.listdir(newpath2)
            for file3 in newsrc2:
                if file3 in skip:
                    continue
                new_filename = file3.capitalize()
                file_tpath = npath + new_filename
                if os.path.exists(file_tpath):
                    continue
                copy2(newpath2 + file3, file_tpath)
                filedict = {}
                print(file_tpath)  # file to copy
                filedict['file_name'] = file3.capitalize()
                m = md5(new_filename.encode('utf-8')).hexdigest()
                filedict['md5'] = m
                filedict['file_path'] = file_tpath
                with Image.open(file_tpath) as img:
                    filedict['width'], filedict['height'] = img.size
                    filedict['file_format'] = img.format
                filedict['file_size'] = os.stat(file_tpath).st_size
                filedict['folder_1'] = m[0]
                filedict['folder_2'] = m[:2]
                filedict['description'] = ''
                files.append(filedict)

        else:
            new_filename = file.capitalize()
            file_tpath = npath + new_filename
            if os.path.exists(file_tpath):
                continue
            copy2(path + file, file_tpath)
            filedict = {}
            print(file_tpath)  # file to copy
            filedict['file_name'] = file.capitalize()
            m = md5(new_filename.encode('utf-8')).hexdigest()
            filedict['md5'] = m
            filedict['file_path'] = file_tpath
            with Image.open(file_tpath) as img:
                filedict['width'], filedict['height'] = img.size
                filedict['file_format'] = img.format
            filedict['file_size'] = os.stat(file_tpath).st_size
            filedict['folder_1'] = m[0]
            filedict['folder_2'] = m[:2]
            filedict['description'] = ''
            files.append(filedict)
    return files

def wikka_dict_to_files(dest_path, dicts):
    dest_path += '/'
    filenames_ = []

    cpath = dest_path
    if not os.path.exists(cpath):
        os.makedirs(cpath)

    src = os.listdir(dest_path)
    for file in src:
        filenames_.append(file.lower())
    for fd in dicts:
        if fd['file_name'].lower() in filenames_:
            continue
        copy2(fd['file_path'], cpath)


def wikka_text_to_mediawiki(strn, pages):
    nstr = strn

    while '{{image' in nstr:
        thumb = False
        # print(strn.find('[[File:'))
        bg = nstr.find('{{image')
        bgi = bg + len('{{image')
        bg_ = nstr.find('url="', bgi)
        bgi_ = bg_ + len('url="')
        endn = nstr.find('"', bgi_)
        endi = nstr.find('}}', bg_)
        end = endi + len('}}')
        old = nstr[bg:end]
        oldi = nstr[bgi:endi]
        oldn = nstr[bgi_:endn]
        # print(old)
        # print(oldi)
        # print(oldn)
        print(bg,'|',bgi,'|',endn,'|',endi,'|',end,'|',old,'|',oldi,'|',oldn)
        # sleep(0.2)
        fn = oldn.split('/')[-1]
        newstr = '[[File:' + fn + '|thumb]]'


        nstr = nstr.replace(old, newstr)

    # print(pages)
    i = 0
    while i < len(nstr) - 1:
        # print(i)
        # print(nstr[i])
        if nstr[i] == '[' and ((i == 0 and nstr[i+1] != '[') or (nstr[i-1] != '[' and nstr[i+1] != '[')):
            # print(strn.find('[[File:'))
            bg = i
            bgi = i + 1
            endi = nstr.find(']', bgi)
            end = endi + 1
            old = nstr[bg:end]
            oldi = nstr[bgi:endi]
            # print(old)
            # print(oldi)
            newstr = old.replace('|', ' ', 1)
            nstr = nstr.replace(old, newstr)
            i += len(newstr)
        i += 1

    i = 0
    while i < len(nstr):
        if nstr[i] == '[' and nstr[i + 1] == '[':
            # print(strn.find('[[File:'))
            bg = i
            bgi = i + len('[[')
            endi = nstr.find(']]', bg)
            end = endi + len(']]')
            old = nstr[bg:end]
            oldi = nstr[bgi:endi]
            if oldi[:5] == 'http:':
                newstr = '[[' + oldi.replace(' ', '|') + ']]'
                nstr = nstr.replace(old, newstr)
                i += len(newstr) - 1
            elif oldi[:5] == 'File:' or oldi[:6] == 'Media:':
                i += 1
                continue
            else:
                newstr = old
                for pg in pages:
                    # print(pg.replace(' ', '').lower(), oldi.lower())
                    if pg.replace(' ', '').lower() == oldi.lower():
                        newstr = '[[' + capitalize_words(pg) + ']]'
                        break

                nstr = nstr.replace(old, newstr)
                i += len(newstr) - 1
        i += 1

    nstr = nstr.replace('//', "''")
    nstr = nstr.replace("**", "'''")
    nstr = nstr.replace("http:''", "http://")
    nstr = nstr.replace("https:''", "https://")

    while '__' in nstr:
        bg = nstr.find('__')
        bgi = bg + len('__')
        endi = nstr.find('__', bgi)
        end = endi + len('__')
        old = nstr[bg:end]
        oldi = nstr[bgi:endi]
        # print(old)
        # print(oldi)
        newstr = '<u>' + oldi.strip() + '</u>'
        nstr = nstr.replace(old, newstr)

    while '++' in nstr:
        bg = nstr.find('++')
        bgi = bg + len('++')
        endi = nstr.find('++', bgi)
        end = endi + len('++')
        old = nstr[bg:end]
        oldi = nstr[bgi:endi]
        # print(old)
        # print(oldi)
        newstr = '<s>' + oldi.strip() + '</s>'
        nstr = nstr.replace(old, newstr)

    nstr = nstr.replace('\t\t\t\t~-', '*****')
    nstr = nstr.replace('\t\t\t~-', '****')
    nstr = nstr.replace('\t\t~-', '***')
    nstr = nstr.replace('\t~-', '**')
    nstr = nstr.replace('~-', '*')

    nstr = sub('\t\t\t\t~[0-9]\)', '######', nstr)
    nstr = sub('\t\t\t~[0-9]\)', '#####', nstr)
    nstr = sub('\t\t~[0-9]\)', '###', nstr)
    nstr = sub('\t~[0-9]\)', '##', nstr)
    nstr = sub('~[0-9]\)', '#', nstr)

    nstr = nstr.replace('======', "==")

    return nstr


def mediawiki_text_to_wikka(strn):
    nstr = strn

    nstr = nstr.replace('\n*****', '\n\t\t\t\t~-')
    nstr = nstr.replace('\n****', '\n\t\t\t~-')
    nstr = nstr.replace('\n***', '\n\t\t~-')
    nstr = nstr.replace('\n**', '\n\t~-')
    nstr = nstr.replace('\n*', '\n~-')

    while '[[File:' in nstr:
        thumb = False
        # print(strn.find('[[File:'))
        bg = nstr.find('[[File:')
        bgi = bg + len('[[File:')
        endi = nstr.find(']]', bg)
        end = endi + len(']]')
        old = nstr[bg:end]
        oldi = nstr[bgi:endi]
        # print(old)
        # print(oldi)
        cur = oldi.split('|')[0]

        newstr = '{{image url="images/' + cur +'"}}'

        nstr = nstr.replace(old, newstr)

    i = 0
    while i < len(nstr):
        if nstr[i] == '[' and nstr[i + 1] == '[':
            # print(strn.find('[[File:'))
            bg = i
            endi = nstr.find(']]', bg)
            end = endi + len(']]')
            old = nstr[bg:end]
            newstr = old.replace(' ', '')
            nstr = nstr.replace(old, newstr)
            i += len(newstr) - 1
        i += 1

    nstr = nstr.replace('<u>', '__')
    nstr = nstr.replace('</u>', '__')
    nstr = nstr.replace('<ins>', '__')
    nstr = nstr.replace('</ins>', '__')
    nstr = nstr.replace('<s>', '++')
    nstr = nstr.replace('</s>', '++')
    nstr = nstr.replace('<del>', '++')
    nstr = nstr.replace('</del>', '++')
    nstr = nstr.replace('<nowiki>', '')
    nstr = nstr.replace('</nowiki>', '')
    nstr = nstr.replace("'''", '**')
    nstr = nstr.replace("''", '//')
    nstr = nstr.replace('==', '======')

    i = 0

    while i < len(nstr):
        # print(i)
        # print('c')
        # print(nstr[i])
        if nstr[i] == '[' and ((i == 0 and nstr[i + 1] != '[') or (nstr[i - 1] != '[' and nstr[i + 1] != '[')):
            # print('d')
            space = False
            # print(strn.find('[[File:'))
            bg = i
            bgi = i + 1
            endi = nstr.find(']', bgi)
            end = endi + 1
            old = nstr[bg:end]
            oldi = nstr[bgi:endi]
            # print(old)
            # print(oldi)
            cur = oldi.split(' ')[0]
            if ' ' in old:
                space = True
                name = ' '.join(oldi.split(' ')[1:])
            if space:
                newstr = '[[' + cur + ' | ' + name + ']]'
            else:
                newstr = '[[' + cur + ']]'
            nstr = nstr.replace(old, newstr)
            i += len(newstr)
        i += 1

    k = 0
    i = 0

    while i < len(nstr) - 1:
        if nstr[i] == '\n' and nstr[i+1] == '#':
            k += 1
            start = i + 1
            n = start
            while n < len(nstr):
                if n == len(nstr) - 1:
                    end = n
                    break
                if nstr[n] == '\n' and nstr[n+1] != '#':
                    end = n
                    break
                n += 1
            end = n
            cur_str = nstr[start:end+1]
            j = 0
            newstr = cur_str
            while j < len(newstr):
                if j < len(newstr) - 4 and newstr[j:j+5] == '#####':
                    newstr = newstr.replace('#####', '\t\t\t\t~' + str(k) + ')', 1)
                elif j < len(newstr) - 3 and newstr[j:j+4] == '####':
                    newstr = newstr.replace('####', '\t\t\t~' + str(k) + ')', 1)
                elif j < len(newstr) - 2 and newstr[j:j+3] == '###':
                    newstr = newstr.replace('###', '\t\t~' + str(k) + ')', 1)
                elif j < len(newstr) - 1 and newstr[j:j+2] == '##':
                    newstr = newstr.replace('##', '\t~' + str(k) + ')', 1)
                elif newstr[j] == '#':
                    newstr = newstr.replace('#', '~' + str(k) + ')', 1)
                j += 1
            nstr = nstr.replace(cur_str, newstr)
            i += len(newstr)
        i += 1

    return nstr