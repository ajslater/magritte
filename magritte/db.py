#!/usr/bin/env python
import os
import sqlite3

from magritte.settings import Settings

EXCLUDE_FOLDER_NAMES = ('Trash', 'TopLevelBooks', 'TopLevelKeepsakes',
                        'TopLevelLightTables', 'Projects',
                        'TopLevelWebProjects', 'TopLevelSlideshows')
# TODO: trim keys in select
FOLDER_KEYS = ('modelId', 'folderPath', 'folderType', 'parentFolderUuid',
               'name', 'uuid')
ALBUM_KEYS = ('modelId', 'name', 'uuid', 'folderUuid')
MASTER_KEYS = ('uuid', 'fileName', 'projectUuid', 'imagePath')


def row_to_dict(row, keys):
    row_dict = {}
    for key in keys:
        row_dict[key] = row[key]

    return row_dict


def get_folders(cursor):
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

    return folders_by_model, folders_by_uuid


def get_albums(cursor, folder_uuids):
    albums = {}

    sql = 'SELECT * FROM RKAlbum WHERE name IS NOT NULL AND NOT isInTrash '
    sql += 'AND folderUuid IN %s' % (tuple(folder_uuids),)
    rows = cursor.execute(sql)
    for row in rows:
        albums[row['modelId']] = row_to_dict(row, ALBUM_KEYS)
    return albums


def fill_albums(cursor, albums):
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


def get_conn():
    db_path = os.path.join(Settings.photos_library_path, 'Database',
                           'apdb', 'Library.apdb')
    db_uri = 'file://%s?mode=ro' % db_path
    conn = sqlite3.connect(db_uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def load_data():
    # TODO with style?
    conn = get_conn()
    cursor = conn.cursor()

    folders_by_model, folders_by_uuid = get_folders(cursor)
    all_albums = get_albums(cursor, folders_by_uuid.keys())
    fill_albums(cursor, all_albums)

    cursor.close()
    conn.close()

    return folders_by_model, folders_by_uuid, all_albums
