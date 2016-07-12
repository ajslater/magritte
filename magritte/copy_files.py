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
    copied = 0
    if not dst_exists or os.stat(src).st_mtime > os.stat(dst).st_mtime:
        if Settings.verbose > 2:
            print('cp %s -> %s' % (src, dst))
        shutil.copy2(src, dst)
        copied = 1
    return copied


def copy_album(album, folder_name, indent):
    media = album.get('media')
    album_name = os.path.join(folder_name, album.get('name'))
    total_copied = 0
    if len(media) <= 0:
        if Settings.verbose > 1:
            print(' %s%s EMPTY ALBUM!' % (indent, album_name))
        return total_copied
    if Settings.do_copy:
        mkdir_if_not_exist(album_name)
    print(' %s%s' % (indent, album.get('name')))
    for item in media:
        file_dst_path = os.path.join(Settings.export_path, album_name,
                                     item.get('fileName'))
        outstr = '  %s%s' % (indent, item.get('fileName'))
        file_src_path = os.path.join(IMAGE_ROOT,
                                     item.get('imagePath'))
        src_exists = os.path.exists(file_src_path)
        if src_exists:
            if Settings.do_copy:
                total_copied += copy_if_newer(file_src_path, file_dst_path)
        else:
            outstr += ' NOT FOUND'
            print(outstr)
    print('  %scopied %s/%s items' % (indent, total_copied, len(media)))
    return total_copied


def copy_folder(folder, parents):
    folder_name = os.path.sep.join(parents + [folder.get('name')])
    indent = ' ' * len(parents)
    print('%s%s' % (indent, folder_name))
    albums = folder.get('albums', {})

    total_copied = 0
    for album in albums.values():
        total_copied += copy_album(album, folder_name, indent)
    return total_copied


def copy_folders(folder, parents, hide):
    total_copied = 0
    if not folder:
        if Settings.verbose > 1:
            print('NULL FOLDER')
        return total_copied
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
        total_copied += copy_folder(folder, parents)

    children = folder.get('children')
    if not children:
        return total_copied
    new_parents = copy.deepcopy(parents)
    if folder_name not in TOP_FOLDER_NAMES:
        new_parents += [folder_name]
    for child in children.values():
        total_copied += copy_folders(child, new_parents, hide)
    return total_copied
