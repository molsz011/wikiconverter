from random import random
from _datetime import datetime
from hashlib import sha1
import os
from shutil import copy2, rmtree
from hashlib import md5
from PIL import Image
ignore = ['Community', 'Community Members HomePage', 'HomePage', 'Instructions', 'Wiki Help']

def tiki_get_max_page_id(session, Page):
    ids = []
    ids.append(1)
    for page in session.query(Page).all():
        ids.append(page.page_id)
    return max(ids)

def tiki_get_max_rev_id(session, History):
    revs = []
    revs.append(1)
    for rev in session.query(History).all():
        revs.append(rev.historyId)
    return max(revs)

def mediawiki_time(epoch):
    date = datetime.fromtimestamp(epoch)

    year = str(date.year)

    if date.month < 10:
        month = '0' + str(date.month)
    else:
        month = str(date.month)

    if date.day < 10:
        day = '0' + str(date.day)
    else:
        day = str(date.day)

    if date.hour < 10:
        hour = '0' + str(date.hour)
    else:
        hour = str(date.hour)

    if date.minute < 10:
        minute = '0' + str(date.minute)
    else:
        minute = str(date.minute)

    if date.second < 10:
        second = '0' + str(date.second)
    else:
        second = str(date.second)

    return year+month+day+hour+minute+second

def time_mw_to_tiki(mw_time):
    date = datetime(year=int(mw_time[:4]), month=int(mw_time[4:6]), day=int(mw_time[6:8]), hour=int(mw_time[8:10]),
                 minute=int(mw_time[10:12]), second=int(mw_time[12:]))
    epoch = datetime(1970, 1, 1)
    return (date - epoch).total_seconds()


def tiki_pages_to_dict(session, Base):
    pages = []
    revs = []
    texts = []
    Page = Base.classes.tiki_pages
    Revision = Base.classes.tiki_history
    next_page_id = 1
    next_rev_id = 1
    next_text_id = 1
    queried_pages = session.query(Page).all()
    queried_revs = session.query(Revision).all()

    tiki_img = Base.classes.tiki_files
    file_dict = session.query(tiki_img.fileId, tiki_img.filename, tiki_img.name, tiki_img.filetype).filter_by(
        archiveId=0)
    files = []
    for file in file_dict:
        newfile = {}
        if file.filename == '':
            newfile['filename'] = file.name.capitalize() + '.' + file.filetype.split('/')[-1].replace('jpeg', 'jpg')
        else:
            newfile['filename'] = file.filename.capitalize()
        newfile['id'] = file.fileId
        files.append(newfile)
        print(newfile['id'], newfile['filename'])

    for page in queried_pages:
        if page.pageName in ignore:
            continue
        tempdict = {}
        tempdict['page_id'] = next_page_id
        tempdict['page_namespace'] = 0
        tempdict['page_title'] = bytes(str.replace(page.pageName, ' ', '_').title(), 'utf-8')
        tempdict['page_restrictions'] = bytes('', 'utf-8')
        tempdict['page_is_redirect'] = 0
        tempdict['page_is_new'] = 0
        tempdict['page_random'] = random()
        tempdict['page_touched'] = bytes(mediawiki_time(page.lastModif), 'utf-8')
        tempdict['page_links_updated'] = None
        tempdict['page_latest'] = next_rev_id
        tempdict['page_len'] = page.page_size
        tempdict['page_content_model'] = b'wikitext'
        if page.lang is None:
            tempdict['page_lang'] = None
        else:
            tempdict['page_lang'] = bytes(page.lang, 'utf-8')
        pages.append(tempdict)
        temprev = {}
        temprev['rev_id'] = next_rev_id
        temprev['rev_page'] = next_page_id
        temprev['rev_text_id'] = next_text_id
        temprev['rev_comment'] = b''
        temprev['rev_user'] = 0
        temprev['rev_user_text'] = bytes(page.user, 'utf-8')
        temprev['rev_timestamp'] = bytes(mediawiki_time(page.lastModif), 'utf-8')
        temprev['rev_version'] = page.version
        temprev['rev_previous'] = None
        temprev['rev_char_changed'] = 0
        temprev['rev_minor_edit'] = page.version_minor
        temprev['rev_deleted'] = 0
        temprev['rev_len'] = page.page_size
        temprev['rev_parent_id'] = 0
        temprev['rev_sha1'] = bytes(sha1(bytes(page.pageName, 'utf-8')).hexdigest(), 'utf-8')
        temprev['rev_content_model'] = None
        temprev['rev_content_format'] = None
        revs.append(temprev)
        temptext = {}
        newdata = tiki_text_to_mediawiki(page.data, files)
        temptext['old_id'] = next_text_id
        temptext['old_text'] = bytes(newdata, 'utf-8')
        temptext['old_flags'] = bytes('utf-8', 'utf-8')
        texts.append(temptext)
        next_rev_id += 1
        next_text_id += 1
        for rev in queried_revs:
            if rev.pageName == page.pageName:
                temprev = {}
                temprev['rev_id'] = next_rev_id
                temprev['rev_page'] = next_page_id
                temprev['rev_text_id'] = next_text_id
                temprev['rev_comment'] = bytes(rev.comment, 'utf-8')
                temprev['rev_user'] = 0
                temprev['rev_user_text'] = bytes(rev.user, 'utf-8')
                temprev['rev_timestamp'] = bytes(mediawiki_time(rev.lastModif), 'utf-8')
                temprev['rev_version'] = rev.version
                temprev['rev_previous'] = None
                temprev['rev_char_changed'] = 0
                temprev['rev_minor_edit'] = rev.version_minor
                temprev['rev_deleted'] = 0
                temprev['rev_len'] = len(rev.data)
                temprev['rev_parent_id'] = 0
                temprev['rev_sha1'] = bytes(sha1(bytes(rev.pageName, 'utf-8')).hexdigest(), 'utf-8')
                temprev['rev_content_model'] = None
                temprev['rev_content_format'] = None
                revs.append(temprev)
                temptext = {}
                temptext['old_id'] = next_text_id
                # temptext['old_text'] = bytes(rev.data, 'utf-8')
                newdata = tiki_text_to_mediawiki(rev.data.decode(), files)
                temptext['old_text'] = bytes(newdata, 'utf-8')
                temptext['old_flags'] = bytes('utf-8', 'utf-8')
                texts.append(temptext)
                next_text_id += 1
                next_rev_id += 1
        next_page_id += 1


        # print(revs_done, texts_done)

    return {'pages': pages, 'revs': revs, 'texts': texts}


def tiki_dict_to_pages(session, Base, dicts):
    Page = Base.classes.tiki_pages
    Revision = Base.classes.tiki_history
    tiki_img = Base.classes.tiki_files

    file_dict = session.query(tiki_img.fileId, tiki_img.filename, tiki_img.name, tiki_img.filetype).filter_by(archiveId=0)
    files = []
    for file in file_dict:
        newfile = {}
        if file.filename == '':
            newfile['filename'] = file.name.capitalize() + '.' + file.filetype.split('/')[-1].replace('jpeg', 'jpg')
        else:
            newfile['filename'] = file.filename.capitalize()
        newfile['id'] = file.fileId
        files.append(newfile)
        print(newfile['id'], newfile['filename'])

    max_page_id = tiki_get_max_page_id(session, Page)
    max_rev_id = tiki_get_max_rev_id(session, Revision)
    skip = ignore
    queried_pages = session.query(Page).all()
    for p in queried_pages:
        skip.append(str.replace(p.pageName, '_', ' ').title())
    done_revs = []
    for page in dicts['pages']:
        title = str.replace(page['page_title'].decode(), '_', ' ').title()
        while title in skip:
            title += '-Duplicate'
        page['page_title'] = title
        skip.append(title)
        print(skip)
        for rev in dicts['revs']:
            if rev['rev_id'] is page['page_latest']:
                done_revs.append(rev['rev_id'])
                current_text = rev['rev_text_id']
                minor = rev['rev_minor_edit']
                user = rev['rev_user_text'].decode()
                version = rev['rev_version']
                break
        for text in dicts['texts']:
            if text['old_id'] is current_text:
                text_data = text['old_text']
                break
        lang = None
        ntext = mediawiki_text_to_tiki(text_data.decode(), files)
        if page['page_lang'] is not None:
            lang = page['page_lang'].decode()
        new_page = Page(page_id=page['page_id']+max_page_id,
                        pageName=title.title(), pageSlug=str.replace(title, ' ', '+').title(), hits=0,
                        data=ntext, description='', lastModif=time_mw_to_tiki(page['page_touched'].decode()),
                        comment='', version=version, version_minor=minor, user=user, ip='0.0.0.0', flag='', points=None,
                        votes=None, cache=None, wiki_cache=None, cache_timestamp=None, page_size=page['page_len'],
                        lang=lang, lockedby='', is_html=0, created=time_mw_to_tiki(page['page_touched'].decode()),
                        wysiwyg='n', wiki_authors_style='', comments_enabled=None, keywords=None)
        session.add(new_page)

    for rev in dicts['revs']:
        # if rev['rev_id'] in done_revs:
        #     continue
        for page in dicts['pages']:
            if page['page_id'] == rev['rev_page']:
                current_page = page
                break
                # name = str.replace(page['page_title'].decode(), '_', ' ').title()
        current_text = rev['rev_text_id']
        for text in dicts['texts']:
            if text['old_id'] is current_text:
                text_data = text['old_text']
                break
        print(current_page['page_title'])
        ntext = mediawiki_text_to_tiki(text_data.decode(), files)
        new_rev = Revision(historyId=rev['rev_id']+max_rev_id, pageName=current_page['page_title'].title(),
                           version=rev['rev_version'], version_minor=rev['rev_minor_edit'],
                           lastModif=time_mw_to_tiki(rev['rev_timestamp'].decode()), description='',
                           user=rev['rev_user_text'].decode(), comment=rev['rev_comment'].decode(),
                           data=bytes(ntext, 'utf-8'), type=None, is_html=0)
        session.add(new_rev)

    session.commit()


def tiki_img_to_dict(session, Base, path):
    path += '/'
    Img = Base.classes.tiki_files
    files = []
    queried_images = session.query(Img).filter_by(archiveId=0)
    npath = path + 'temp_folder/'
    if os.path.exists(npath):
        rmtree(npath)
    os.makedirs(npath)
    for img in queried_images:
        filedict = {}
        if img.filename == '':
            new_filename = img.name.capitalize() + '.' + img.filetype.split('/')[-1].replace('jpeg', 'jpg')
        else:
            new_filename = img.filename.capitalize().replace('jpeg', 'jpg')
        if os.path.isfile(npath+new_filename):
            continue
        copy2(path+img.path, npath)
        os.rename(npath+img.path, npath+new_filename)
        m = md5(new_filename.encode('utf-8')).hexdigest()
        print(m)
        filedict['file_name'] = new_filename
        filedict['md5'] = m
        newpath = npath + new_filename
        filedict['file_path'] = newpath
        with Image.open(newpath) as img2:
            filedict['width'], filedict['height'] = img2.size
            filedict['file_format'] = img2.format
        filedict['file_size'] = os.stat(newpath).st_size
        filedict['folder_1'] = m[0]
        filedict['folder_2'] = m[:2]
        filedict['description'] = img.description

        files.append(filedict)

    return files


def tiki_dict_to_files(session, Base, dest_path, dicts):
    dest_path += '/'
    Img = Base.classes.tiki_files
    filenames_ = []
    file_ids = []
    file_ids.append(1)
    db_files = session.query(Img).all()
    for file in db_files:
        file_ids.append(file.fileId)
        if file.filename == '':
            new_filename = file.name.capitalize() + '.' + file.filetype.split('/')[-1].replace('jpeg', 'jpg')
        else:
            new_filename = file.filename.capitalize()
        filenames_.append(new_filename.lower())

    next_file_id = max(file_ids) + 1


    for fd in dicts:
        if fd['file_name'].lower() in filenames_:
            continue

        cpath = dest_path
        if not os.path.exists(cpath):
            os.makedirs(cpath)
        copy2(fd['file_path'], cpath)
        os.rename(cpath+fd['file_name'], cpath+fd['md5'])

        new_image = Img(fileId=next_file_id, galleryId=1, name=fd['file_name'].split('.')[0],
                        description=fd['description'], created=int(datetime.now().timestamp()),
                        filename=fd['file_name'], filesize=fd['file_size'], filetype='image/'+fd['file_format'].lower(),
                        data=None, user=None, author=None, hits=0, maxhits=None, lastDownload=None, votes=None,
                        points=None, path=fd['md5'], reference_url=None, is_reference=None, hash=None, search_data='',
                        metadata=None, lastModif=int(datetime.now().timestamp()), lastModifUser='', lockedby=None,
                        comment='', archiveId=0, deleteAfter=None)

        print(fd['file_name'] + ' uploaded.')
        next_file_id += 1
        session.add(new_image)

    session.commit()


def mediawiki_text_to_tiki(strn, files):
    nstr = strn
    while '[[File:' in nstr:
        thumb = False
        # print('a')
        # print(strn.find('[[File:'))
        bg = nstr.find('[[File:')
        bgi = bg + len('[[File:')
        endi = nstr.find(']]', bg)
        end = endi + len(']]')
        old = nstr[bg:end]
        oldi = nstr[bgi:endi]
        # print(old)
        # print(oldi)
        if 'thumb' in old:
            thumb = True
        cur = oldi.split('|')[0]
        fid = 0
        for f in files:
            if f['filename'].lower() == cur.lower():
                fid = f['id']
                break
        if thumb:
            newstr = '{img fileId="' + str(fid) + '" thumb="box"}'
        else:
            newstr = '{img fileId="' + str(fid) + '"}'

        nstr = nstr.replace(old, newstr)

    nstr = nstr.replace('[[', '((')
    nstr = nstr.replace(']]', '))')
    nstr = nstr.replace("'''", '__')

    while '==' in nstr:
        # print('b')
        bg = nstr.find('==')
        bgi = bg + len('==')
        endi = nstr.find('==', bgi)
        end = endi + len('==')
        old = nstr[bg:end]
        oldi = nstr[bgi:endi]
        # print(old)
        # print(oldi)
        newstr = '!' + oldi.strip()
        nstr = nstr.replace(old, newstr)

    nstr = nstr.replace('<u>', '===')
    nstr = nstr.replace('</u>', '===')
    nstr = nstr.replace('<ins>', '===')
    nstr = nstr.replace('</ins>', '===')
    nstr = nstr.replace('<s>', '--')
    nstr = nstr.replace('</s>', '--')
    nstr = nstr.replace('<del>', '--')
    nstr = nstr.replace('</del>', '--')
    nstr = nstr.replace('<nowiki>', '~np~')
    nstr = nstr.replace('</nowiki>', '~/np~')

    i = 0

    while i < len(nstr):
        # print(i)
        # print('c')
        # print(nstr[i])
        if nstr[i] == '[':
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
                newstr = '[' + cur + '|' + name + ']'
            else:
                newstr = '[' + cur + ']'
            nstr = nstr.replace(old, newstr)
            i += len(newstr)
        i += 1


    return nstr


def tiki_text_to_mediawiki(strn, files):
    nstr = strn
    while '{img fileId=' in nstr:
        thumb = False
        # print(strn.find('[[File:'))
        bg = nstr.find('{img fileId="')
        bgi = bg + len('{img fileId="')
        endn = nstr.find('"', bgi)
        endi = nstr.find('}', bg)
        end = endi + len('}')
        old = nstr[bg:end]
        oldi = nstr[bgi:endi]
        oldn = nstr[bgi:endn]
        # print(old)
        # print(oldi)
        # print(oldn)
        if 'thumb="box"' in old:
            thumb = True
        fn = 'Example.jpg'
        for f in files:
            if f['id'] == int(oldn):
                fn = f['filename']
                break
        if thumb:
            newstr = '[[File:' + fn + '|thumb]]'
        else:
            newstr = '[[File:' + fn + ']]'

        nstr = nstr.replace(old, newstr)

    nstr = nstr.replace('((', '[[')
    nstr = nstr.replace('))', ']]')
    nstr = nstr.replace("__", "'''")

    while '===' in nstr:
        bg = nstr.find('===')
        bgi = bg + len('===')
        endi = nstr.find('===', bgi)
        end = endi + len('===')
        old = nstr[bg:end]
        oldi = nstr[bgi:endi]
        # print(old)
        # print(oldi)
        newstr = '<u>' + oldi.strip() + '</u>'
        nstr = nstr.replace(old, newstr)

    nstr = nstr.replace('---', '{{temp-line}}')

    while '--' in nstr:
        bg = nstr.find('--')
        bgi = bg + len('--')
        endi = nstr.find('--', bgi)
        end = endi + len('--')
        old = nstr[bg:end]
        oldi = nstr[bgi:endi]
        # print(old)
        # print(oldi)
        newstr = '<s>' + oldi.strip() + '</s>'
        nstr = nstr.replace(old, newstr)

    nstr = nstr.replace('{{temp-line}}', '----')

    nstr = nstr.replace('~np~', '<nowiki>')
    nstr = nstr.replace('~/np~', '</nowiki>')

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

    while ('\n!') in nstr:
        bg = nstr.find('\n!')
        bgi = bg + len('\n!')
        endi = nstr.find('\n', bgi)
        end = endi + len('\n')
        old = nstr[bg:end]
        oldi = nstr[bgi:endi]
        tr = nstr[bg:endi]
        # print(old)
        # print(oldi)
        newstr = '== ' + tr.strip()[1:] + ' ==\n'
        nstr = nstr.replace(old, newstr)

    return nstr