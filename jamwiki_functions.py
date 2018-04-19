from random import random
from _datetime import datetime
from hashlib import sha1

import os
from shutil import copy2, rmtree
from hashlib import md5
from PIL import Image
ignore = ['StartingPoints']

def jam_get_max_page_id(session, Page):
    ids = []
    ids.append(1)
    for page in session.query(Page).all():
        ids.append(page.topic_id)
    return max(ids)

def jam_get_max_rev_id(session, History):
    revs = []
    revs.append(1)
    for rev in session.query(History).all():
        revs.append(rev.topic_version_id)
    return max(revs)

def jam_get_max_file_id(session, Files):
    files_ = []
    files_.append(1)
    for file in session.query(Files).all():
        files_.append(file.file_id)
    return max(files_)

def jam_get_max_file_ver_id(session, Files_v):
    files_ = []
    files_.append(1)
    for file in session.query(Files_v).all():
        files_.append(file.file_version_id)
    return max(files_)

def mediawiki_time(dt):

    date = dt

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

def time_mw_to_jam(mw_time):
    date = datetime(year = int(mw_time[:4]), month = int(mw_time[4:6]), day = int(mw_time[6:8]), hour = int(mw_time[8:10]),
                 minute = int(mw_time[10:12]), second = int(mw_time[12:]))
    return date

def jam_pages_to_dict(session, Base):
    pages = []
    revs = []
    texts = []
    Page = Base.classes.jam_topic
    Revision = Base.classes.jam_topic_version
    next_page_id = 1
    next_rev_id = 1
    next_text_id = 1
    queried_pages = session.query(Page).all()
    queried_revs = session.query(Revision).all()
    revs_done = []
    for page in queried_pages:
        if page.topic_name in ignore or page.namespace_id != 0:
            continue
        tempdict = {}
        current_rev_id = page.current_version_id
        for rev in queried_revs:
            if rev.topic_version_id == current_rev_id:
                current_rev = rev
                revs_done.append(current_rev_id)
                break
        tempdict['page_id'] = next_page_id
        tempdict['page_namespace'] = page.namespace_id
        tempdict['page_title'] = bytes(str.replace(page.topic_name, ' ', '_').title(), 'utf-8')
        tempdict['page_restrictions'] = bytes('', 'utf-8')
        tempdict['page_is_redirect'] = 0
        tempdict['page_is_new'] = 0
        tempdict['page_random'] = random()
        tempdict['page_touched'] = bytes(mediawiki_time(current_rev.edit_date), 'utf-8')
        tempdict['page_links_updated'] = None
        tempdict['page_latest'] = next_rev_id
        tempdict['page_len'] = len(current_rev.version_content)
        tempdict['page_content_model'] = b'wikitext'
        tempdict['page_lang'] = None
        pages.append(tempdict)
        temprev = {}
        temprev['rev_id'] = next_rev_id
        temprev['rev_page'] = next_page_id
        temprev['rev_text_id'] = next_text_id
        temprev['rev_comment'] = bytes(current_rev.edit_comment, 'utf-8')
        temprev['rev_user'] = 0
        temprev['rev_user_text'] = bytes(current_rev.wiki_user_display, 'utf-8')
        temprev['rev_timestamp'] = bytes(mediawiki_time(current_rev.edit_date), 'utf-8')
        temprev['rev_version'] = 0
        temprev['rev_previous'] = current_rev.previous_topic_version_id
        temprev['rev_char_changed'] = current_rev.characters_changed
        temprev['rev_minor_edit'] = 0
        temprev['rev_deleted'] = 0
        temprev['rev_len'] = len(current_rev.version_content)
        temprev['rev_parent_id'] = 0
        temprev['rev_sha1'] = bytes(sha1(bytes(page.topic_name, 'utf-8')).hexdigest(), 'utf-8')
        temprev['rev_content_model'] = None
        temprev['rev_content_format'] = None
        revs.append(temprev)
        temptext = {}
        temptext['old_id'] = next_text_id
        temptext['old_text'] = bytes(current_rev.version_content, 'utf-8')
        temptext['old_flags'] = bytes('utf-8', 'utf-8')
        texts.append(temptext)
        next_rev_id += 1
        next_text_id += 1
        version = 1
        for rev in queried_revs:
            if rev.topic_id == page.topic_id and rev.topic_version_id not in revs_done:
                current_rev = rev
                temprev = {}
                temprev['rev_id'] = next_rev_id
                temprev['rev_page'] = next_page_id
                temprev['rev_text_id'] = next_text_id
                temprev['rev_comment'] = bytes(current_rev.edit_comment, 'utf-8')
                temprev['rev_user'] = 0
                temprev['rev_user_text'] = bytes(current_rev.wiki_user_display, 'utf-8')
                temprev['rev_timestamp'] = bytes(mediawiki_time(current_rev.edit_date), 'utf-8')
                temprev['rev_version'] = version
                temprev['rev_previous'] = current_rev.previous_topic_version_id
                temprev['rev_char_changed'] = current_rev.characters_changed
                temprev['rev_minor_edit'] = 0
                temprev['rev_deleted'] = 0
                temprev['rev_len'] = len(current_rev.version_content)
                temprev['rev_parent_id'] = 0
                temprev['rev_sha1'] = bytes(sha1(bytes(page.topic_name, 'utf-8')).hexdigest(), 'utf-8')
                temprev['rev_content_model'] = None
                temprev['rev_content_format'] = None
                revs.append(temprev)
                temptext = {}
                temptext['old_id'] = next_text_id
                temptext['old_text'] = bytes(current_rev.version_content, 'utf-8')
                temptext['old_flags'] = bytes('utf-8', 'utf-8')
                texts.append(temptext)
                next_text_id += 1
                next_rev_id += 1
                version += 1
        next_page_id += 1

    return {'pages': pages, 'revs': revs, 'texts': texts}


def jamwiki_dict_to_pages(session, Base, dicts):
    Page = Base.classes.jam_topic
    Revision = Base.classes.jam_topic_version
    max_page_id = jam_get_max_page_id(session, Page)
    max_rev_id = jam_get_max_rev_id(session, Revision)
    skip = ignore
    queried_pages = session.query(Page).all()
    for p in queried_pages:
        skip.append(str.replace(p.topic_name, '_', ' ').title())
    done_revs = []
    for page in dicts['pages']:
        title = str.replace(page['page_title'].decode(), '_', ' ')
        while title.title() in skip:
            title += '-Duplicate'
        skip.append(title.title())
        for rev in dicts['revs']:
            if rev['rev_id'] is page['page_latest']:
                done_revs.append(rev['rev_id'])
                break
        # new_page = Page(page_id=page['page_id'] + max_page_id,
        #                 pageName=str.replace(page['page_title'].decode(), '_', ' ').title(),
        #                 pageSlug=str.replace(page['page_title'].decode(), '_', '+').title(), hits=0,
        #                 data=text_data.decode(), description='',
        #                 lastModif=time_mw_to_tiki(page['page_touched'].decode()), comment='', version=version,
        #                 version_minor=minor, user=user, ip='0.0.0.0', flag='', points=None, votes=None, cache=None,
        #                 wiki_cache=None, cache_timestamp=None, page_size=page['page_len'],
        #                 lang=lang, lockedby='', is_html=0, created=time_mw_to_tiki(page['page_touched'].decode()),
        #                 wysiwyg='n', wiki_authors_style='', comments_enabled=None, keywords=None)
        new_page = Page(topic_id=page['page_id']+max_page_id, virtual_wiki_id=1, namespace_id=page['page_namespace'],
                        topic_name=title, page_name=title, page_name_lower=title.lower(), delete_date=None,
                        topic_read_only=0, topic_admin_only=0, current_version_id=None,
                        topic_type=1, redirect_to=None)
        session.add(new_page)
    session.commit()
        # print(new_page.__dict__)
    for rev in dicts['revs']:
        # if rev['rev_id'] in done_revs:
        #     continue
        for page in dicts['pages']:
            if page['page_id'] is rev['rev_page']:
                current_page_id = page['page_id']
                current_text = rev['rev_text_id']
            for text in dicts['texts']:
                if text['old_id'] is current_text:
                    text_data = text['old_text']
        previous = None
        if rev['rev_previous'] is not None:
            previous = rev['rev_previous']+max_rev_id
        new_rev = Revision(topic_version_id=max_rev_id+rev['rev_id'], topic_id=max_page_id+current_page_id,
                           edit_comment=rev['rev_comment'].decode(), version_content=text_data.decode(),
                           wiki_user_id=None, wiki_user_display=rev['rev_user_text'].decode(),
                           edit_date=time_mw_to_jam(rev['rev_timestamp'].decode()), edit_type=1,
                           previous_topic_version_id=previous, characters_changed=rev['rev_char_changed'],
                           version_params=None)
        session.add(new_rev)
    session.commit()

    i = 0
    queried_pages = session.query(Page).all()
    for p in queried_pages:
        if p.topic_id <= max_page_id:
            continue
        p.current_version_id = dicts['pages'][i]['page_latest'] + max_rev_id
        i += 1

    session.commit()

def jamwiki_img_to_dict(session, Base, path):
    path += '/'
    Img = Base.classes.jam_file
    Img_v = Base.classes.jam_file_version
    files = []
    queried_images = session.query(Img).all()
    queried_versions = session.query(Img_v.upload_comment, Img_v.file_url).all()
    temp_path = path + 'temp_folder/'
    if os.path.exists(temp_path):
        rmtree(temp_path)
    os.makedirs(temp_path)
    for img in queried_images:
        filedict = {}
        newpath = path + img.file_url[1:]
        ntemp_path = temp_path + img.file_url.split('/')[-1]
        new_temp_path = temp_path + img.file_name.capitalize()
        copy2(newpath, temp_path)
        os.rename(ntemp_path, new_temp_path)
        filedict['file_name'] = img.file_name.capitalize()
        m = md5(img.file_name.capitalize().encode('utf-8')).hexdigest()
        filedict['md5'] = m

        filedict['file_path'] = new_temp_path
        with Image.open(new_temp_path) as img2:
            filedict['width'], filedict['height'] = img2.size
            filedict['file_format'] = img2.format
        filedict['file_size'] = os.stat(new_temp_path).st_size
        filedict['folder_1'] = m[0]
        filedict['folder_2'] = m[:2]
        for fl in queried_versions:
            if fl.file_url == img.file_url:
                filedict['description'] = fl.upload_comment
        files.append(filedict)

    return files

def jamwiki_dict_to_files(session, Base, path, dicts):
    path += '/'
    Img = Base.classes.jam_file
    Img_v = Base.classes.jam_file_version
    Topic = Base.classes.jam_topic
    Version = Base.classes.jam_topic_version
    first_file_id = jam_get_max_file_id(session, Img) + 1
    first_file_ver_id = jam_get_max_file_ver_id(session, Img_v) + 1
    first_topic_id = jam_get_max_page_id(session, Topic) + 1
    first_ver_id = jam_get_max_rev_id(session, Version) + 1
    skip = []

    filenames_ = session.query(Img.file_name).all()
    for name in filenames_:
        skip.append(name.file_name.lower())
    ct = datetime.now()
    date_str = mediawiki_time(ct)
    next_file_id = first_file_id
    next_file_ver_id = first_file_ver_id
    next_topic_id = first_topic_id
    for img in dicts:
        fn = img['file_name']
        if fn.lower() in skip:
            continue
        new_fn = fn.split('.')[0] + '-' + date_str[6:] + '.' + fn.split('.')[-1]
        url_ = 'en/' + date_str[:4] + '/' + str(ct.month) + '/'
        url = url_ + new_fn
        print(path+url)
        if not os.path.exists(path+url_):
            os.makedirs(path+url_)
        copy2(img['file_path'], path+url)

        new_file = Img(file_id=next_file_id, virtual_wiki_id=1, file_name=fn, delete_date=None, file_read_only=0,
                       file_admin_only=0, file_url='/'+url, mime_type='image/'+img['file_format'].lower(),
                       topic_id=next_topic_id, file_size=img['file_size'])
        session.add(new_file)
        new_file_v = Img_v(file_version_id=next_file_ver_id, file_id=next_file_id, upload_comment=img['description'],
                           file_url='/'+url, wiki_user_id=None, wiki_user_display='0:0:0:0:0:0:0:1', upload_date=ct,
                           mime_type='image/'+img['file_format'].lower(), file_size=img['file_size'])
        session.add(new_file_v)
        new_topic=Topic(topic_id=next_topic_id, virtual_wiki_id=1, namespace_id=6, topic_name='File:'+fn, page_name=fn,
                        page_name_lower=fn.lower(), delete_date=None, topic_read_only=0, topic_admin_only=0,
                        current_version_id=None, topic_type=4, redirect_to=None)
        session.add(new_topic)
        next_file_id += 1
        next_file_ver_id += 1
        next_topic_id += 1

    session.commit()

    next_topic_id = first_topic_id
    next_ver_id = first_ver_id

    for img in dicts:
        fn = img['file_name']
        if fn.lower() in skip:
            continue
        new_fn = fn.split('.')[0] + '-' + date_str[6:] + '.' + fn.split('.')[-1]
        url = 'en/' + date_str[:4] + '/' + str(ct.month) + '/' + new_fn
        print(path+url)
        copy2(img['file_path'], path+url)

        new_topic_v=Version(topic_version_id=next_ver_id, topic_id=next_topic_id, edit_comment=img['description'],
                            version_content=img['description'], wiki_user_id=None, wiki_user_display='0:0:0:0:0:0:0:1',
                            edit_date=ct, edit_type=9, previous_topic_version_id=None, characters_changed=0,
                            version_params='File:'+fn)
        session.add(new_topic_v)
        next_ver_id += 1
        next_topic_id += 1
    session.commit()

    queried_pages = session.query(Topic).filter(Topic.topic_id >= first_topic_id)
    next_ver_id = first_ver_id
    for p in queried_pages:
        p.current_version_id = next_ver_id
        next_ver_id += 1

    session.commit()