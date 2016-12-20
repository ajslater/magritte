"""Load data from the Apple Photos database."""
import os
import sqlite3

from magritte.settings import Settings

EXCLUDE_FOLDER_NAMES = ('Trash', 'TopLevelBooks', 'TopLevelKeepsakes',
                        'TopLevelLightTables', 'Projects',
                        'TopLevelWebProjects', 'TopLevelSlideshows')

EXCLUDE_ALBUM_NAMES = ('All Photos', 'Last Import',
                       'Favorites', 'Hidden', 'Bursts', 'Panoramas',
                       'Screenshots', 'Videos', 'Slo-mo', 'Time-lapse',
                       'My Photo Stream', 'Selfies', 'People', 'Places',
                       'Favorite Memories', 'Depth Effect')


def get_folders(cursor):
    """Get the folders from the db."""
    sql = 'SELECT modelId, folderPath, parentFolderUuid, name, uuid ' \
          'FROM RKFolder WHERE name IS NOT NULL ' \
          'AND NOT isInTrash AND folderType <> 2 '
    sql += 'AND name NOT IN %s' % (EXCLUDE_FOLDER_NAMES,)
    rows = cursor.execute(sql)

    folders_by_model = {}
    folders_by_uuid = {}
    for row in rows:
        row_dict = dict(row)
        folders_by_model[row['modelId']] = row_dict
        folders_by_uuid[row['uuid']] = row_dict

    return folders_by_model, folders_by_uuid


def get_albums(cursor, folder_uuids):
    """Get the albums from the db."""
    albums = {}

    sql = 'SELECT modelId, name, folderUuid FROM RKAlbum ' \
          'WHERE name IS NOT NULL ' \
          'AND NOT isInTrash '
    sql += 'AND folderUuid IN %s' % (tuple(folder_uuids),)
    sql += 'AND name NOT IN %s' % (EXCLUDE_ALBUM_NAMES,)
    rows = cursor.execute(sql)
    for row in rows:
        albums[row['modelId']] = dict(row)
    return albums


def fill_albums(cursor, albums):
    """Fill the albums with photos from the db."""
    for album in albums.values():
        album_id = album.get('modelId')
        sql = 'SELECT imagePath, fileName FROM RKMaster WHERE modelId IN' \
              '(SELECT masterId FROM RKVersion WHERE modelId IN ' \
              '(SELECT versionId FROM RKAlbumVersion '
        sql += 'WHERE albumId = %s))' % album_id
        rows = cursor.execute(sql)
        album['media'] = []
        for row in rows:
            album['media'].append(dict(row))


def get_conn():
    """Get a database connection."""
    db_path = os.path.join(Settings.photos_library_path, 'database',
                           'photos.db')
    # if it's not a new Photos lib, try the old file name
    if not os.path.exists(db_path):
        db_path = os.path.join(Settings.photos_library_path, 'Database',
                               'apdb', 'Library.apdb')
    db_uri = 'file://%s?mode=ro' % db_path
    conn = sqlite3.connect(db_uri, uri=True)
    conn.row_factory = sqlite3.Row
    if Settings.verbose > 2:
        print('using database: %s' % db_path)
    return conn


def load_data():
    """Get a db connection, load folders, albums, and photos."""
    conn = get_conn()
    cursor = conn.cursor()

    folders_by_model, folders_by_uuid = get_folders(cursor)
    all_albums = get_albums(cursor, folders_by_uuid.keys())
    fill_albums(cursor, all_albums)

    cursor.close()
    conn.close()

    return folders_by_model, folders_by_uuid, all_albums
