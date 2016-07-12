import os

PICTURES_PATH = os.path.join(os.environ['HOME'], 'Pictures')


class Settings(object):
    """ a global settings class """

    photos_library_path = os.path.join(PICTURES_PATH,
                                       'Photos Library.photoslibrary')
    export_path = os.path.join(PICTURES_PATH, 'Photo Albums')
    verbose = 1
    do_copy = True
    copy_filter = None

    @classmethod
    def update(cls, settings):
        for k, v in settings.__dict__.items():
            if k.startswith('_'):
                continue
            setattr(cls, k, v)
