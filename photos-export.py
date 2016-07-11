#!/usr/bin/env python

import os
import sqlite3
import shutil
import copy

PHOTOS_APP_PATH = os.path.join(os.environ['HOME'], 'Pictures',
                               'Photos Library.photoslibrary')
LIBRARY_PATH = os.path.join(PHOTOS_APP_PATH, 'Database', 'apdb',
                            'Library.apdb')
FOLDER_KEYS = ('modelId', 'folderPath', 'folderType', 'parentFolderUuid',
               'name', 'uuid')
EXCLUDE_FOLDER_NAMES = ('Trash', 'TopLevelBooks', 'TopLevelKeepsakes',
                        'TopLevelLightTables', 'Projects',
                        'TopLevelWebProjects', 'TopLevelSlideshows')
ALBUM_KEYS = ('modelId', 'name', 'uuid', 'folderUuid')
VERSION_KEYS = ('uuid', 'fileName', 'projectUuid')
MASTER_KEYS = ('uuid', 'fileName', 'projectUuid', 'imagePath')
IMAGE_ROOT = os.path.join(PHOTOS_APP_PATH, 'Masters')
EXPORT_PATH = os.path.join(os.environ['HOME'], 'Pictures',
                           'Photo Albums')
ROOT_FOLDER = ':TopLevelAlbums:'


def row_to_dict(row, keys):
    row_dict = {}
    for key in keys:
        row_dict[key] = row[key]

    return row_dict


def get_folders(conn):
    cursor = conn.cursor()
    sql = 'SELECT * FROM RKFolder WHERE name IS NOT NULL ' \
          'AND NOT isInTrash AND folderType <> 2 '
    sql += 'AND name NOT IN %s' % (EXCLUDE_FOLDER_NAMES,)
    rows = cursor.execute(sql)

    folders_by_model = {}
    folders_by_uuid = {}
    for row in rows:
        row_dict = row_to_dict(row, FOLDER_KEYS)
        folders_by_model[row['modelId']] = row_dict
        folders_by_uuid[row['uuid']] = row_dict

    cursor.close()

    return folders_by_model, folders_by_uuid


def get_albums(conn, folder_uuids):
    albums = {}
    cursor = conn.cursor()

    sql = 'SELECT * FROM RKAlbum WHERE name IS NOT NULL AND NOT isInTrash '
    sql += 'AND folderUuid IN %s' % (tuple(folder_uuids),)
    rows = cursor.execute(sql)
    for row in rows:
        albums[row['modelId']] = row_to_dict(row, ALBUM_KEYS)
    cursor.close()
    return albums


def fill_albums(conn, albums):
    cursor = conn.cursor()
    for album in albums.values():
        album_id = album.get('modelId')
        rows = cursor.execute(
            'SELECT * FROM RKMaster WHERE modelId IN'
            '(SELECT masterId FROM RKVersion WHERE modelId IN '
            '(SELECT versionId FROM RKAlbumVersion '
            'WHERE albumId = %s))' % album_id)
        album['media'] = []
        for row in rows:
            media = row_to_dict(row, MASTER_KEYS)
            album['media'].append(media)
    cursor.close()


def build_folder_tree(folders):
    root_folder = None
    for model_id, folder in folders.items():
        folder_paths_str = folder.get('folderPath').strip('/')
        folder_paths = folder_paths_str.split('/')
        if len(folder_paths) <= 1:
            if folder.get('parentFolderUuid') is None:
                root_folder = folder
        else:
            parent_model_id = int(folder_paths[-2])
            parent = folders[parent_model_id]
            if 'children' not in parent:
                parent['children'] = {}
            parent['children'][model_id] = folder
    return root_folder


def assign_albums_to_folders(folders, albums):
    for album in albums.values():
        folder_uuid = album.get('folderUuid')
        folder = folders.get(folder_uuid)
        if not folder:
            print('No folder for uuid: %s' % folder_uuid)
            continue
        if 'albums' not in folder:
            folder['albums'] = {}
        folder['albums'][album.get('modelId')] = album


def mkdir_if_not_exist(sub_path):
    full_path = os.path.join(EXPORT_PATH, sub_path)
    if os.path.exists(full_path):
        return
    os.makedirs(full_path)


def copy_if_newer(src, dst):
    dst_exists = os.path.exists(dst)
    if not dst_exists or os.stat(src).st_mtime > os.stat(dst).st_mtime:
        print('cp %s -> %s' % (src, dst))
        shutil.copy2(src, dst)

TOP_FOLDER_NAMES = ('', 'TopLevelAlbums')


def copy_folder(folder, parents, do_copy=False):
    folder_name = os.path.sep.join(parents + [folder.get('name')])
    indent = ' ' * len(parents)
    print('%s%s type:%s' % (indent, folder_name,
                            folder.get('folderType')
                            )
          )
    albums = folder.get('albums')
    if albums:
        for album in albums.values():
            media = album.get('media')
            album_name = os.path.join(folder_name, album.get('name'))
            if len(media) <= 0:
                print(' %s%s EMPTY ALBUM!' % (indent, album_name))
                continue
            if do_copy:
                mkdir_if_not_exist(album_name)
            print(' %s%s' % (indent, album.get('name')))
            print('  %s%s items' % (indent, len(media)))
            for item in media:
                file_dst_path = os.path.join(EXPORT_PATH, album_name,
                                             item.get('fileName'))
                outstr = '  %s%s' % (indent, item.get('fileName'))
                file_src_path = os.path.join(IMAGE_ROOT,
                                             item.get('imagePath'))
                src_exists = os.path.exists(file_src_path)
                if src_exists:
                    if do_copy:
                        copy_if_newer(file_src_path, file_dst_path)
                else:
                    outstr += ' NOT FOUND'
                    print(outstr)


def copy_folders(folder, parents, hide, do_copy=False):
    if not folder:
        print('NULL FOLDER')
        return
    if folder.get('parentFolderUuid') == 'TopLevelAlbums':
        hide = False
    indent = ' ' * len(parents)
    folder_name = folder.get('name')
    if hide:
        print('%s%s type:%s HIDDEN FOLDER %s %s' % (indent, folder_name,
                                                    folder.get('folderType'),
                                                    folder.get('modelId'),
                                                    folder.get('folderPath')
                                                    )
              )
    else:
        copy_folder(folder, parents, do_copy)

    children = folder.get('children')
    if not children:
        return
    new_parents = copy.deepcopy(parents)
    if folder_name not in TOP_FOLDER_NAMES:
        new_parents += [folder_name]
    for child in children.values():
        copy_folders(child, new_parents, hide, do_copy)


def main():
    conn = sqlite3.connect('file:'+LIBRARY_PATH+'?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    folders_by_model, folders_by_uuid = get_folders(conn)
    root_folder = build_folder_tree(folders_by_model)

    all_albums = get_albums(conn, folders_by_uuid.keys())
    assign_albums_to_folders(folders_by_uuid, all_albums)
    fill_albums(conn, all_albums)
    copy_folders(root_folder, [], True, True)


if __name__ == '__main__':
    main()
