"""Copy files from Apple Photos library to external filesystem."""
import os
import shutil
import copy

from magritte.settings import Settings


TOP_FOLDER_NAMES = ('', 'TopLevelAlbums')


def mkdir_if_not_exist(sub_path):
    """Make a directory if it doesn't exist."""
    full_path = os.path.join(Settings.export_path, sub_path)
    if os.path.exists(full_path):
        return
    os.makedirs(full_path)


def is_newer(filename_a, filename_b):
    """Compare file mtimes."""
    return os.path.getmtime(filename_a) > os.path.getmtime(filename_b)


def copy_if_newer(src, dst):
    """Only copy the file if its newer than the old one."""
    dst_exists = os.path.exists(dst)
    copied = 0
    if not dst_exists or is_newer(src, dst):
        if Settings.do_copy:
            if Settings.do_link:
                if dst_exists and is_newer(src, dst):
                    os.remove(dst)
                os.link(src, dst)
            else:
                shutil.copy2(src, dst)
        copied = 1
    if Settings.verbose > 3:
        operation = 'ln' if Settings.do_link else 'cp'
        skipped = 'skipped (newer target)' if copied == 0 else ''
        print('%s %s -> %s %s' % (operation, src, dst, skipped))
    return copied


def copy_album(album, folder_name, indent):
    """Copy an entire album."""
    media = album.get('media')
    album_fn = album.get('name').replace('/',' - ').replace(':',' - ')
    album_name = os.path.join(folder_name, album_fn)
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
        file_src_path = os.path.join(os.path.join(Settings.photos_library_path, 'Masters'),
                                     item.get('imagePath'))
        src_exists = os.path.exists(file_src_path)
        if src_exists:
            if Settings.do_copy:
                total_copied += copy_if_newer(file_src_path, file_dst_path)
        else:
            outstr += ' (%s) NOT FOUND' % file_src_path
            print(outstr)
    print('  %scopied %s/%s items' % (indent, total_copied, len(media)))
    return total_copied


def copy_folder(folder, parents):
    """Copy an Apple Photos folder."""
    folder_name = os.path.sep.join(parents + [folder.get('name')])
    indent = ' ' * len(parents)
    print('%s%s' % (indent, folder_name))
    albums = folder.get('albums', {})

    total_copied = 0
    for album in albums.values():
        total_copied += copy_album(album, folder_name, indent)
    return total_copied


def copy_folders(folder, parents, hide):
    """Copy all the folders."""
    total_copied = 0
    if not folder:
        if Settings.verbose > 1:
            print('NULL FOLDER')
        return total_copied
    if Settings.copy_filter is None and \
            (folder.get('parentFolderUuid') == 'TopLevelAlbums' or
            folder.get('parentFolderUuid') == 'LibraryFolder'):
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
