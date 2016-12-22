"""Build the folder and album tree in memory."""


def build_folder_tree(folders):
    """Build the folder tree."""
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
    """Assign albums to folders."""
    for album in albums.values():
        folder_uuid = album.get('folderUuid')
        folder = folders.get(folder_uuid)
        if not folder:
            print('No folder for uuid: %s' % folder_uuid)
            continue
        if 'albums' not in folder:
            folder['albums'] = {}
        folder['albums'][album.get('modelId')] = album


def build(folders_by_model, folders_by_uuid, albums):
    """Build the entire folder and album tree."""
    root_folder = build_folder_tree(folders_by_model)
    assign_albums_to_folders(folders_by_uuid, albums)
    return root_folder
