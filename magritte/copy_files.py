import os
import shutil
import copy

from magritte.settings import Settings

IMAGE_ROOT = os.path.join(Settings.photos_library_path, 'Masters')
TOP_FOLDER_NAMES = ('', 'TopLevelAlbums')


def mkdir_if_not_exist(sub_path):
    full_path = os.path.join(Settings.export_path, sub_path)
    if os.path.exists(full_path):
        return
    os.makedirs(full_path)


def copy_if_newer(src, dst):
    dst_exists = os.path.exists(dst)
    if not dst_exists or os.stat(src).st_mtime > os.stat(dst).st_mtime:
        print('cp %s -> %s' % (src, dst))
        shutil.copy2(src, dst)


def copy_album(album, folder_name, indent):
    media = album.get('media')
    album_name = os.path.join(folder_name, album.get('name'))
    if len(media) <= 0:
        if Settings.verbose > 1:
            print(' %s%s EMPTY ALBUM!' % (indent, album_name))
        return
    if Settings.do_copy:
        mkdir_if_not_exist(album_name)
    print(' %s%s' % (indent, album.get('name')))
    print('  %s%s items' % (indent, len(media)))
    for item in media:
        file_dst_path = os.path.join(Settings.export_path, album_name,
                                     item.get('fileName'))
        outstr = '  %s%s' % (indent, item.get('fileName'))
        file_src_path = os.path.join(IMAGE_ROOT,
                                     item.get('imagePath'))
        src_exists = os.path.exists(file_src_path)
        if src_exists:
            if Settings.do_copy:
                copy_if_newer(file_src_path, file_dst_path)
        else:
            outstr += ' NOT FOUND'
            print(outstr)


def copy_folder(folder, parents):
    folder_name = os.path.sep.join(parents + [folder.get('name')])
    indent = ' ' * len(parents)
    print('%s%s' % (indent, folder_name))
    albums = folder.get('albums', {})

    for album in albums.values():
        copy_album(album, folder_name, indent)


def copy_folders(folder, parents, hide):
    if not folder:
        if Settings.verbose > 1:
            print('NULL FOLDER')
        return
    if Settings.copy_filter is None and \
            folder.get('parentFolderUuid') == 'TopLevelAlbums':
        hide = False
    folder_name = folder.get('name')
    if Settings.copy_filter and folder_name == Settings.copy_filter:
        hide = False
    indent = ' ' * len(parents)
    if hide:
        if Settings.verbose > 1:
            print('%s%s type:%s HIDDEN FOLDER %s %s' %
                  (indent, folder_name, folder.get('folderType'),
                   folder.get('modelId'), folder.get('folderPath'))
                  )
    else:
        copy_folder(folder, parents)

    children = folder.get('children')
    if not children:
        return
    new_parents = copy.deepcopy(parents)
    if folder_name not in TOP_FOLDER_NAMES:
        new_parents += [folder_name]
    for child in children.values():
        copy_folders(child, new_parents, hide)
