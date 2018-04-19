from _datetime import datetime
from random import random
from shutil import *
from hashlib import md5
import os
from PIL import Image
from shutil import copy2
ignore = ['Main_Page', b'Main_Page']

def capitalize_words(string):
    words = string.split()
    return ' '.join([word.capitalize() for word in words])

def mediawiki_currenttime():
    date = datetime.now()
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


def get_max_page_id(session, Page):
    ids = []
    ids.append(1)
    for page in session.query(Page).all():
        ids.append(page.page_id)
    return max(ids)


def get_max_rev_id(session, Revision):
    revs = []
    revs.append(1)
    for rev in session.query(Revision).all():
        revs.append(rev.rev_id)
    return max(revs)


def get_max_text_id(session, Text):
    texts = []
    texts.append(1)
    for text in session.query(Text).all():
        texts.append(text.old_id)
    return max(texts)


def mediawiki_pages_to_dict(session, Base):
    pages = []
    revs = []
    texts = []
    Page = Base.classes.page
    Revision = Base.classes.revision
    Text = Base.classes.text
    next_page_id = get_max_page_id(session, Page) + 1
    next_rev_id = get_max_rev_id(session, Revision) + 1
    next_text_id = get_max_text_id(session, Text) + 1
    queried_pages = session.query(Page).all()
    queried_revs = session.query(Revision).all()
    queried_texts = session.query(Text).all()
    revs_done = []
    texts_done = []
    for page in queried_pages:
        if page.page_title in ignore or page.page_namespace != 0:
            continue
        tempdict = {}
        # tempdict['page_id'] = next_page_id
        tempdict['page_id'] = page.page_id
        tempdict['page_namespace'] = page.page_namespace
        tempdict['page_title'] = page.page_title
        tempdict['page_restrictions'] = page.page_restrictions
        tempdict['page_is_redirect'] = page.page_is_redirect
        tempdict['page_is_new'] = page.page_is_new
        tempdict['page_random'] = random()
        tempdict['page_touched'] = page.page_touched
        tempdict['page_links_updated'] = page.page_links_updated
        # tempdict['page_latest'] = next_rev_id
        tempdict['page_latest'] = page.page_latest
        tempdict['page_len'] = page.page_len
        tempdict['page_content_model'] = page.page_content_model
        tempdict['page_lang'] = page.page_lang
        pages.append(tempdict)
        version = 1
        for rev in queried_revs:
            temprev = {}
            if rev.rev_page == page.page_id and rev.rev_id not in revs_done:
                revs_done.append(rev.rev_id)
                # temprev['rev_id'] = next_rev_id
                # temprev['rev_page'] = next_page_id
                # temprev['rev_text_id'] = next_text_id
                temprev['rev_id'] = rev.rev_id
                temprev['rev_page'] = rev.rev_page
                temprev['rev_text_id'] = rev.rev_text_id
                temprev['rev_comment'] = rev.rev_comment
                temprev['rev_user'] = rev.rev_user
                temprev['rev_user_text'] = rev.rev_user_text
                temprev['rev_timestamp'] = rev.rev_timestamp
                temprev['rev_version'] = version
                temprev['rev_previous'] = None
                temprev['rev_char_changed'] = 0
                temprev['rev_minor_edit'] = rev.rev_minor_edit
                temprev['rev_deleted'] = rev.rev_deleted
                temprev['rev_len'] = rev.rev_len
                temprev['rev_parent_id'] = rev.rev_parent_id
                temprev['rev_sha1'] = rev.rev_sha1
                temprev['rev_content_model'] = rev.rev_content_model
                temprev['rev_content_format'] = rev.rev_content_format
                revs.append(temprev)
                version += 1
                for text in queried_texts:
                    temptext = {}
                    if text.old_id == rev.rev_text_id and text.old_id not in texts_done:
                        texts_done.append(text.old_id)
                        temptext['old_id'] = text.old_id
                        # temptext['old_id'] = next_text_id
                        temptext['old_text'] = text.old_text
                        temptext['old_flags'] = text.old_flags
                        texts.append(temptext)
                        next_text_id += 1
                next_rev_id += 1
        next_page_id += 1

        # print(revs_done, texts_done)

    return {'pages': pages, 'revs': revs, 'texts': texts}


def mediawiki_dict_to_pages(session, Base, dicts):
    Page = Base.classes.page
    Revision = Base.classes.revision
    Text = Base.classes.text
    skip = ignore
    next_page_id = get_max_page_id(session, Page)
    next_rev_id = get_max_rev_id(session, Revision)
    next_text_id = get_max_text_id(session, Text)
    queried_pages = session.query(Page).all()
    for p in queried_pages:
        skip.append(p.page_title.decode().title())
    for page in dicts['pages']:
        title = page['page_title'].decode().title()
        while title in skip:
            title += '-Duplicate'
        skip.append(title)
        title = bytes(title, 'utf-8')
        new_page = Page(page_id=page['page_id']+next_page_id, page_namespace=page['page_namespace'], page_title=title,
                        page_restrictions=page['page_restrictions'], page_is_redirect=page['page_is_redirect'],
                        page_is_new=page['page_is_new'], page_random=page['page_random'],
                        page_touched=page['page_touched'], page_links_updated=page['page_links_updated'],
                        page_latest=page['page_latest']+next_rev_id, page_len=page['page_len'],
                        page_content_model=page['page_content_model'], page_lang=page['page_lang'])
        print("page " + str(page['page_id']))
        session.add(new_page)

    for rev in dicts['revs']:
        new_revision = Revision(rev_id=rev['rev_id']+next_rev_id, rev_page=rev['rev_page']+next_page_id,
                                rev_text_id=rev['rev_text_id']+next_text_id, rev_comment=rev['rev_comment'],
                                rev_user=rev['rev_user'], rev_user_text=rev['rev_user_text'],
                                rev_timestamp=rev['rev_timestamp'], rev_minor_edit=rev['rev_minor_edit'],
                                rev_deleted=rev['rev_deleted'], rev_len=rev['rev_len'],
                                rev_parent_id=rev['rev_parent_id'], rev_sha1=rev['rev_sha1'],
                                rev_content_model=rev['rev_content_model'],
                                rev_content_format=rev['rev_content_format'])
        session.add(new_revision)

    for text in dicts['texts']:
        new_text = Text(old_id=text['old_id']+next_text_id, old_text=text['old_text'], old_flags=text['old_flags'])
        session.add(new_text)

    session.commit()

def mediawiki_img_to_dict(session, Base, path):
    path += '/'
    src = os.listdir(path)
    skip = ['archive', 'lockdir', 'temp', 'thumb', '.htaccess', 'README', '.stylelintrc']
    Img = Base.classes.image
    db_files = session.query(Img.img_name, Img.img_description).all()
    files = []
    for file in src:
        if file in skip:
            continue

        if os.path.isdir(path+file):
            newpath = path + file + '/'
            newsrc = os.listdir(newpath)
            print(newpath)
            for file2 in newsrc:
                if file2 in skip:
                    continue
                newpath2 = newpath + file2 + '/'
                newsrc2 = os.listdir(newpath2)
                print(newpath2)
                for file3 in newsrc2:
                    if file3 in skip:
                        continue
                    filedict = {}
                    newpath3 = newpath2 + file3
                    print(newpath3) # file to copy
                    filedict['file_name'] = file3
                    m = md5(file3.encode('utf-8')).hexdigest()
                    filedict['md5'] = m
                    filedict['file_path'] = newpath3
                    with Image.open(newpath3) as img:
                        filedict['width'], filedict['height'] = img.size
                        filedict['file_format'] = img.format
                    filedict['file_size'] = os.stat(newpath3).st_size
                    filedict['folder_1'] = m[0]
                    filedict['folder_2'] = m[:2]
                    filedict['description'] = ''
                    for fl in db_files:
                        if fl.img_name.decode() == filedict['file_name'] and (fl.img_description.decode() is not None):
                            filedict['description'] = fl.img_description.decode()
                            break
                    files.append(filedict)
        else:
            filedict = {}
            newpath3 = path + file
            print(newpath3) # file to copy
            filedict['file_name'] = file
            m = md5(file.encode('utf-8')).hexdigest()
            filedict['md5'] = m
            filedict['file_path'] = newpath3
            with Image.open(newpath3) as img:
                filedict['width'], filedict['height'] = img.size
                filedict['file_format'] = img.format
            filedict['file_size'] = os.stat(newpath3).st_size
            filedict['folder_1'] = m[0]
            filedict['folder_2'] = m[:2]
            filedict['description'] = ''
            for fl in db_files:
                if fl.img_name.decode() == filedict['file_name'] and (fl.img_description.decode() is not None):
                    filedict['description'] = fl.img_description.decode()
                    break
            files.append(filedict)

    # images = Base.classes.image
    # queried_images = session.query(images).all()
    #
    # for image in queried_images:
    #     current_img = {}
    #     for dictimg in files:
    #         if dictimg['file_name'] == image.img_name.decode():
    #             current_img = dictimg
    #     current_img['img_name'] = image.img_name
    #     current_img['img_size'] = image.img_size
    #     current_img['img_width'] = image.img_width
    #     current_img['img_height'] = image.img_height
    #     current_img['img_metadata'] = image.img_metadata
    #     current_img['img_bits'] = image.img_bits
    #     current_img['img_media_type'] = image.img_media_type
    #     current_img['img_major_mime'] = image.img_major_mime
    #     current_img['img_minor_mime'] = image.img_minor_mime
    #     current_img['img_description'] = image.img_description
    #     current_img['img_user'] = image.img_user
    #     current_img['img_user_text'] = image.img_user_text
    #     current_img['img_timestamp'] = image.img_timestamp
    #     current_img['img_sha1'] = image.img_sha1

    return files


def mediawiki_dict_to_files(session, Base, dest_path, dicts):
    dest_path += '/'
    Image = Base.classes.image
    filenames_ = []
    db_files = session.query(Image.img_name).all()
    for file in db_files:
        print(file.img_name)
        filenames_.append(file.img_name.decode().lower())

    for fd in dicts:
        if fd['file_name'].lower() in filenames_:
            continue

        cpath = dest_path + fd['folder_1'] + '/' + fd['folder_2']
        if not os.path.exists(cpath):
            os.makedirs(cpath)
        copy2(fd['file_path'], cpath)

        new_image = Image(img_name=bytes(fd['file_name'], 'utf-8'), img_size=fd['file_size'], img_width=fd['width'],
                          img_height=fd['height'], img_metadata=b'', img_bits=8, img_media_type='BITMAP',
                          img_major_mime='image', img_minor_mime=bytes(fd['file_format'].lower(), 'utf-8'),
                          img_description=bytes(fd['description'], 'utf-8'), img_user=0, img_user_text=b'',
                          img_timestamp=bytes(mediawiki_currenttime(), 'utf-8'), img_sha1=b'')

        print(fd['file_name'] + ' uploaded.')
        session.add(new_image)

    session.commit()