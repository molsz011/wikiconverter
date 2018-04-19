from random import random
from _datetime import datetime
from hashlib import sha1
from jamwiki_functions import time_mw_to_jam as time_mw_to_wacko
from jamwiki_functions import mediawiki_time
from mediawiki_functions import capitalize_words
import os
from shutil import copy2, rmtree
from hashlib import md5
from PIL import Image
from re import sub

ignore = ['homepage', 'users/', 'category', 'permalink', 'groups', 'users', 'recentchanges', 'recentlycommented',
          'pageindex', 'registration', 'password', 'search', 'login', 'settings']

def wacko_get_max_page_id(session, Page):
    ids = []
    ids.append(1)
    for page in session.query(Page).all():
        ids.append(page.page_id)
    return max(ids)

def wacko_get_max_rev_id(session, History):
    revs = []
    revs.append(1)
    for rev in session.query(History).all():
        revs.append(rev.revision_id)
    return max(revs)

def wacko_get_username(id, queried_users):
    for user in queried_users:
        if user.user_id == id:
            return user.user_name
    return ''

def wacko_get_max_rev_page(id, queried_revs):
    revs = []
    revs.append(1)
    for rev in queried_revs:
        if rev.page_id == id:
            revs.append(rev.revision_id)
    return max(revs)

def wacko_get_user_id(name, users):
    for user in users:
        if user['name'].lower() == name.lower():
            return user['id']
    return 0

def wacko_get_max_user_id(queried_users):
    ids = []
    for user in queried_users:
        ids.append(user.user_id)
    return max(ids) + 1

def wacko_pages_to_dict(session, Base):
    pages = []
    revs = []
    texts = []
    pages_links = []
    Page = Base.classes.wacko_page
    Revision = Base.classes.wacko_revision
    Users = Base.classes.wacko_user
    next_page_id = 1
    next_rev_id = 1
    next_text_id = 1
    queried_pages = session.query(Page).all()
    queried_revs = session.query(Revision).all()
    queried_users = session.query(Users).all()

    for page in queried_pages:
        pages_links.append(page.title)

    for page in queried_pages:
        skip = False
        for ign in ignore:
            if page.tag.lower().startswith(ign):
                skip = True
                continue
        if skip:
            continue
        # print(wacko_get_username(page.user_id, queried_users) + ' ' + wacko_get_username(page.owner_id, queried_users))
        tempdict = {}
        tempdict['page_id'] = next_page_id
        tempdict['page_namespace'] = 0
        tempdict['page_title'] = bytes(str.replace(page.title, ' ', '_').title(), 'utf-8')
        tempdict['page_restrictions'] = bytes('', 'utf-8')
        tempdict['page_is_redirect'] = 0
        tempdict['page_is_new'] = 0
        tempdict['page_random'] = random()
        tempdict['page_touched'] = bytes(mediawiki_time(page.modified), 'utf-8')
        tempdict['page_links_updated'] = None
        tempdict['page_latest'] = next_rev_id
        tempdict['page_len'] = len(page.body)
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
        temprev['rev_comment'] = bytes(page.edit_note, 'utf-8')
        temprev['rev_user'] = 0
        user_text = ''
        get_usr = wacko_get_username(page.user_id, queried_users)
        if get_usr != '':
            user_text = get_usr
        temprev['rev_user_text'] = bytes(user_text, 'utf-8')
        temprev['rev_timestamp'] = bytes(mediawiki_time(page.modified), 'utf-8')
        temprev['rev_version'] = wacko_get_max_rev_page(page.page_id, queried_revs) + 1
        temprev['rev_previous'] = None
        temprev['rev_char_changed'] = 0
        temprev['rev_minor_edit'] = page.minor_edit
        temprev['rev_deleted'] = page.deleted
        temprev['rev_len'] = len(page.body)
        temprev['rev_parent_id'] = page.parent_id
        temprev['rev_sha1'] = bytes(sha1(bytes(page.title, 'utf-8')).hexdigest(), 'utf-8')
        temprev['rev_content_model'] = None
        temprev['rev_content_format'] = None
        revs.append(temprev)
        temptext = {}
        temptext['old_id'] = next_text_id
        temptext['old_text'] = bytes(wacko_text_to_mediawiki(page.body, pages_links), 'utf-8')
        temptext['old_flags'] = bytes('utf-8', 'utf-8')
        texts.append(temptext)
        next_rev_id += 1
        next_text_id += 1
        for rev in queried_revs:
            if rev.page_id == page.page_id:
                temprev = {}
                temprev['rev_id'] = next_rev_id
                temprev['rev_page'] = next_page_id
                temprev['rev_text_id'] = next_text_id
                temprev['rev_comment'] = b''
                temprev['rev_user'] = 0
                temprev['rev_user_text'] = bytes(wacko_get_username(rev.user_id, queried_users), 'utf-8')
                temprev['rev_timestamp'] = bytes(mediawiki_time(rev.modified), 'utf-8')
                temprev['rev_version'] = rev.version_id
                temprev['rev_previous'] = None
                temprev['rev_char_changed'] = 0
                temprev['rev_minor_edit'] = rev.minor_edit
                temprev['rev_deleted'] = rev.deleted
                temprev['rev_len'] = len(rev.body)
                temprev['rev_parent_id'] = 0
                temprev['rev_sha1'] = bytes(sha1(bytes(page.title, 'utf-8')).hexdigest(), 'utf-8')
                temprev['rev_content_model'] = None
                temprev['rev_content_format'] = None
                revs.append(temprev)
                temptext = {}
                temptext['old_id'] = next_text_id
                temptext['old_text'] = bytes(wacko_text_to_mediawiki(rev.body, pages_links), 'utf-8')
                temptext['old_flags'] = bytes('utf-8', 'utf-8')
                texts.append(temptext)
                next_text_id += 1
                next_rev_id += 1
        next_page_id += 1

    return {'pages': pages, 'revs': revs, 'texts': texts}

def wacko_dict_to_pages(session, Base, dicts):
    Page = Base.classes.wacko_page
    Revision = Base.classes.wacko_revision
    Users = Base.classes.wacko_user
    max_page_id = wacko_get_max_page_id(session, Page)
    max_rev_id = wacko_get_max_rev_id(session, Revision)
    skip = ignore
    queried_pages = session.query(Page).all()
    queried_users = session.query(Users).all()
    max_user_id = wacko_get_max_user_id(queried_users)
    for p in queried_pages:
        skip.append(p.tag.lower())
    revs_done = []
    # for p in dicts['pages']:
    #     print(str.replace(p['page_title'].decode(), '_', ''))
    #
    #
    # for s in skip:
    #     print(s)
    usr = []
    for user in queried_users:
        nusr = {}
        nusr['name'] = user.user_name
        nusr['id'] = user.user_id
        usr.append(nusr)
    ct = datetime.now()
    for page in dicts['pages']:
        title = str.replace(page['page_title'].decode(), '_', ' ')
        tag_ = str.replace(page['page_title'].decode(), '_', '')
        tag = str.replace(tag_, '-', '')
        supertag = tag.lower()
        while tag.lower() in skip:
            tag += 'Duplicate'
            supertag += 'duplicate'
            title += '-Duplicate'
        skip.append(tag.lower())
        page['page_title'] = title
        for rev in dicts['revs']:
            if rev['rev_id'] == page['page_latest']:
                current_rev = rev
                revs_done.append(current_rev['rev_id'])
                break
        for text in dicts['texts']:
            if text['old_id'] == current_rev['rev_text_id']:
                text_data = mediawiki_text_to_wacko(text['old_text'].decode())

        lang = None
        if page['page_lang'] is not None:
            lang = page['page_lang'].decode()
        author_id = wacko_get_user_id(current_rev['rev_user_text'].decode(), usr)
        if author_id == 0:
            new_user = Users(user_id=max_user_id, user_name=current_rev['rev_user_text'].decode(), real_name='', password='',
                             salt='', email='', account_type=0, enabled=1, signup_time=ct, change_password='',
                             email_confirm='', session_time=ct, session_expire=0, last_mark=ct, login_count=0,
                             lost_password_request_count=0, failed_login_count=0, total_pages=0, total_revisions=0,
                             total_comments=0, total_uploads=0, fingerprint=None)
            nusr = {}
            nusr['name'] = current_rev['rev_user_text'].decode()
            nusr['id'] = max_user_id
            usr.append(nusr)
            author_id = max_user_id
            max_user_id += 1
            session.add(new_user)
        new_page = Page(page_id=page['page_id']+max_page_id, owner_id=author_id, user_id=author_id, title=title,
                        tag=tag, supertag=supertag, menu_tag='', depth=1, parent_id=current_rev['rev_parent_id'],
                        created=time_mw_to_wacko(page['page_touched'].decode()),
                        modified=time_mw_to_wacko(page['page_touched'].decode()), body=text_data, body_r='',
                        body_toc='', formatting='wacko', edit_note=current_rev['rev_comment'].decode(),
                        minor_edit=current_rev['rev_minor_edit'], reviewed=0,
                        reviewed_time=time_mw_to_wacko(page['page_touched'].decode()), reviewer_id=author_id, ip='::1',
                        latest=2, handler='page', comment_on_id=0, comments=0, hits=0, theme=None,
                        lang=lang, commented=time_mw_to_wacko(page['page_touched'].decode()), description='',
                        keywords='', footer_comments=None, footer_files=None, footer_rating=None, hide_toc=None,
                        hide_index=None, tree_level=0, show_menu_tag=0, allow_rawhtml=None, disable_safehtml=None,
                        noindex=0, deleted=current_rev['rev_deleted'])
        session.add(new_page)

    for rev in dicts['revs']:
        if rev['rev_id'] in revs_done:
            continue

        for page in dicts['pages']:
            if page['page_id'] == rev['rev_page']:
                current_page = page
                break

        for text in dicts['texts']:
            if text['old_id'] == rev['rev_text_id']:
                current_text = text
                break

        title = str.replace(page['page_title'], '_', ' ')
        tag_ = str.replace(page['page_title'], '_', '')
        tag = str.replace(tag_, '-', '')
        supertag = tag.lower()
        # while tag.lower() in skip:
        #     tag += 'Duplicate'
        #     supertag += 'duplicate'
        #     title += '-Duplicate'
        lang = None
        ctext = mediawiki_text_to_wacko(current_text['old_text'].decode())
        if current_page['page_lang'] is not None:
            lang = current_page['page_lang'].decode()
        author_id = wacko_get_user_id(current_rev['rev_user_text'].decode(), usr)
        if author_id == 0:
            new_user = Users(user_id=max_user_id, user_name=current_rev['rev_user_text'].decode(), real_name='', password='',
                             salt='', email='', account_type=0, enabled=1, signup_time=ct, change_password='',
                             email_confirm='', session_time=ct, session_expire=0, last_mark=ct, login_count=0,
                             lost_password_request_count=0, failed_login_count=0, total_pages=0, total_revisions=0,
                             total_comments=0, total_uploads=0, fingerprint=None)
            nusr = {}
            nusr['name'] = current_rev['rev_user_text'].decode()
            nusr['id'] = max_user_id
            usr.append(nusr)
            author_id = max_user_id
            max_user_id += 1
            session.add(new_user)
        new_rev = Revision(revision_id=rev['rev_id']+max_rev_id, page_id=rev['rev_page']+max_page_id,
                           version_id=rev['rev_version'], owner_id=author_id, user_id=author_id, title=title, tag=tag,
                           supertag=supertag, menu_tag='', created=time_mw_to_wacko(rev['rev_timestamp'].decode()),
                           modified=time_mw_to_wacko(rev['rev_timestamp'].decode()),
                           body=ctext, body_r='', formatting='wacko',
                           edit_note=rev['rev_comment'].decode(), minor_edit=rev['rev_minor_edit'], reviewed=0,
                           reviewed_time=time_mw_to_wacko(rev['rev_timestamp'].decode()), reviewer_id=author_id,
                           latest=0, ip='::1', handler='page', comment_on_id=0, lang=lang, description='', keywords='',
                           deleted=rev['rev_deleted'])
        session.add(new_rev)
        print(tag)
        print(skip)
    session.commit()


def wacko_img_to_dict(session, Base, path):
    path += '/'
    Img = Base.classes.wacko_upload
    files = []
    queried_images = session.query(Img).filter(Img.file_name != 'wacko_logo.png')
    npath = path + 'temp_folder/'
    if os.path.exists(npath):
        rmtree(npath)
    os.makedirs(npath)
    for img in queried_images:
        filedict = {}
        new_filename = img.file_name.capitalize()
        file_tpath = npath+new_filename
        copy2(path+img.file_name, file_tpath)
        # os.rename(npath+img.path, npath+new_filename)
        m = md5(new_filename.encode('utf-8')).hexdigest()
        print(m)
        filedict['file_name'] = new_filename
        filedict['md5'] = m
        filedict['file_path'] = file_tpath
        with Image.open(file_tpath) as img2:
            filedict['width'], filedict['height'] = img2.size
            filedict['file_format'] = img2.format
        filedict['file_size'] = os.stat(file_tpath).st_size
        filedict['folder_1'] = m[0]
        filedict['folder_2'] = m[:2]
        filedict['description'] = img.file_description

        files.append(filedict)

    return files

def wacko_dict_to_files(session, Base, dest_path, dicts):
    dest_path += '/'
    Img = Base.classes.wacko_upload
    filenames_ = []
    file_ids = []
    db_files = session.query(Img.upload_id, Img.file_name).all()
    for file in db_files:
        file_ids.append(file.upload_id)
        new_filename = file.file_name.capitalize()
        filenames_.append(new_filename.lower())

    next_file_id = max(file_ids) + 1
    dt = datetime.now()

    for fd in dicts:
        if fd['file_name'].lower() in filenames_:
            continue

        cpath = dest_path
        if not os.path.exists(cpath):
            os.makedirs(cpath)
        copy2(fd['file_path'], cpath)

        new_image = Img(upload_id=next_file_id, page_id=0, user_id=0, file_name=fd['file_name'], lang='en',
                      file_description=fd['description'], uploaded_dt=dt, file_size=fd['file_size'],
                      picture_w=fd['width'], picture_h=fd['height'], file_ext=fd['file_name'].split('.')[-1], hits=0,
                      deleted=0)

        print(fd['file_name'] + ' uploaded.')
        next_file_id += 1
        session.add(new_image)

    session.commit()


def mediawiki_text_to_wacko(strn):
    nstr = strn

    nstr = nstr.replace('\n*****', '\n          *')
    nstr = nstr.replace('\n****', '\n        *')
    nstr = nstr.replace('\n***', '\n      *')
    nstr = nstr.replace('\n**', '\n    *')
    nstr = nstr.replace('\n*', '\n  *')

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

        newstr = 'file:' + cur

        nstr = nstr.replace(old, newstr)

    while '[[Media:' in nstr:
        thumb = False
        # print(strn.find('[[File:'))
        bg = nstr.find('[[Media:')
        bgi = bg + len('[[Media:')
        endi = nstr.find(']]', bg)
        end = endi + len(']]')
        old = nstr[bg:end]
        oldi = nstr[bgi:endi]
        # print(old)
        # print(oldi)
        cur = oldi.split('|')[0]

        newstr = 'file:' + cur

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
    nstr = nstr.replace('<s>', '--')
    nstr = nstr.replace('</s>', '--')
    nstr = nstr.replace('<del>', '--')
    nstr = nstr.replace('</del>', '--')
    nstr = nstr.replace('<nowiki>', '')
    nstr = nstr.replace('</nowiki>', '')
    nstr = nstr.replace("'''", '**')
    nstr = nstr.replace("''", '//')

    i = 0

    while i < len(nstr):
        # print(i)
        # print(nstr[i])
        if nstr[i] == '[' and ((i == 0 and nstr[i + 1] != '[') or (nstr[i - 1] != '[' and nstr[i + 1] != '[')):
            # print(strn.find('[[File:'))
            bg = i
            bgi = i + 1
            endi = nstr.find(']', bgi)
            end = endi + 1
            old = nstr[bg:end]
            oldi = nstr[bgi:endi]
            # print(old)
            # print(oldi)
            newstr = '[' + old + ']'
            nstr = nstr.replace(old, newstr)
            i += 1
        i += 1

    i = 0

    while i < len(nstr) - 1:
        if nstr[i] == '\n' and nstr[i+1] == '#':
            five = 1
            four = 1
            three = 1
            two = 1
            one = 1
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
                    newstr = newstr.replace('#####', '          ' + str(five) + '.', 1)
                    five += 1
                elif j < len(newstr) - 3 and newstr[j:j+4] == '####':
                    newstr = newstr.replace('####', '        ' + str(four) + '.', 1)
                    five = 1
                    four += 1
                elif j < len(newstr) - 2 and newstr[j:j+3] == '###':
                    newstr = newstr.replace('###', '      ' + str(three) + '.', 1)
                    five = 1
                    four = 1
                    three += 1
                elif j < len(newstr) - 1 and newstr[j:j+2] == '##':
                    newstr = newstr.replace('##', '    ' + str(two) + '.', 1)
                    five = 1
                    four = 1
                    three = 1
                    two += 1
                elif newstr[j] == '#':
                    newstr = newstr.replace('#', '  ' + str(one) + '.', 1)
                    five = 1
                    four = 1
                    three = 1
                    two = 1
                    one += 1
                j += 1
            nstr = nstr.replace(cur_str, newstr)
            i += len(newstr)
        i += 1

    return nstr

def wacko_text_to_mediawiki(strn, pages):
    nstr = strn
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
            newstr = old
            if ' ' in oldi or oldi[:4] == 'http':
                newstr = '[' + oldi + ']'
            else:
                for pg in pages:
                    if pg.replace(' ', '').lower() == oldi.lower():
                        newstr = '[[' + capitalize_words(pg) + ']]'
                        break

            nstr = nstr.replace(old, newstr)
            i += len(newstr) - 1
        i += 1

    i = 0
    while i < len(nstr) - 2:
        if nstr[i] == '(' and nstr[i + 1] == '(':
            # print(strn.find('[[File:'))
            bg = i
            bgi = i + len('((')
            endi = nstr.find('))', bg)
            end = endi + len('))')
            old = nstr[bg:end]
            oldi = nstr[bgi:endi]
            newstr = old
            if ' ' in oldi or oldi[:4] == 'http':
                newstr = '[' + oldi.replace(' ', '|') + ']'
            else:
                newstr = '[' + oldi + ']'

            nstr = nstr.replace(old, newstr)
            i += len(newstr) - 1
        i += 1

    while 'file:' in nstr:
        thumb = False
        # print(strn.find('[[File:'))
        bg = nstr.find('file:')
        bgi = bg + len('file:')
        endn = nstr.find('\n', bgi)
        endi = nstr.find('\n', bg)
        end = endi + len('\n')
        old = nstr[bg:end]
        if ' ' in old:
            endn = nstr.find(' ', bgi)
            endi = nstr.find(' ', bg)
            end = endi + len(' ')
        if endn < 0:
            endn = len(nstr)
            endi = len(nstr)
            end = len(nstr)
        old = nstr[bg:end]
        oldi = nstr[bgi:endi]
        oldn = nstr[bgi:endn]
        fn = oldn.split(' ')[0]
        # newstr = '[[File:' + fn + '|thumb]] '
        newstr = '[[File:' + fn + ']] '
        # print(bg,bgi,endn,endi,end,old,oldi,oldn)
        nstr = nstr.replace(old, newstr)

    nstr = nstr.replace('**', "!!!BOLD!!!")
    nstr = nstr.replace('//', "''")
    nstr = nstr.replace('----', "!!!LINE!!!")
    nstr = nstr.replace('---', "!!!LINE!!!")
    nstr = nstr.replace("http:''", "http://")
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

    nstr = nstr.replace('\n', '\n\n')

    nstr = nstr.replace('\n\n          *', '\n*****')
    nstr = nstr.replace('\n\n        *', '\n****')
    nstr = nstr.replace('\n\n      *', '\n***')
    nstr = nstr.replace('\n\n    *', '\n**')
    nstr = nstr.replace('\n\n  *', '\n*')

    nstr = sub('\n\n          [0-9]\.', '\n######', nstr)
    nstr = sub('\n\n        [0-9]\.', '\n#####', nstr)
    nstr = sub('\n\n      [0-9]\.', '\n###', nstr)
    nstr = sub('\n\n    [0-9]\.', '\n##', nstr)
    nstr = sub('\n\n  [0-9]\.', '\n#', nstr)

    while '\n\n\n' in nstr:
        nstr = nstr.replace('\n\n\n', '\n\n')

    nstr = nstr.replace("!!!BOLD!!!", "'''")
    nstr = nstr.replace("!!!LINE!!!", '\n----')
    return nstr