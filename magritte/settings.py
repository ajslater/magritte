"""Settings class for magritte."""
import os

PICTURES_PATH = os.path.join(os.environ['HOME'], 'Pictures')


class Settings(object):
    """A global settings class."""

    photos_library_path = os.path.join(PICTURES_PATH,
                                       'Photos Library.photoslibrary')
    export_path = os.path.join(PICTURES_PATH, 'Photos Export')
    verbose = 1
    do_copy = True
    do_link = False
    copy_filter = None

    @classmethod
    def update(cls, settings):
        """Update settings class from a dictionary."""
        for key, val in settings.__dict__.items():
            if key.startswith('_'):
                continue
            setattr(cls, key, val)
