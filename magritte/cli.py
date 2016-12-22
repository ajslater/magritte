#!/usr/bin/env python3
"""CLI for copying photos from macOS Photos to the filesystem."""
import argparse

from magritte.settings import Settings
from magritte.db import load_data
from magritte.build import build
from magritte.copy_files import copy_folders
from magritte import __version__


def get_arguments():
    """Parse the command line."""
    usage = "%(prog)s [arguments] [image files]"
    description = "Exports all albums from macOS Photos to the filesystem"
    parser = argparse.ArgumentParser(usage=usage, description=description)
    parser.add_argument("-v", "--verbose", action="count",
                        dest="verbose", default=0,
                        help="Display more output. -v (default) and -vv "
                        "(noisy)")
    parser.add_argument("-Q", "--quiet", action="store_const",
                        dest="verbose", const=-1,
                        help="Display little to no output")
    parser.add_argument("-l", "--photos-library-path", action="store",
                        dest="photos_library_path",
                        default=Settings.photos_library_path,
                        help="Location of the Photos App Library to copy")
    parser.add_argument("-e", "--export-path", action="store",
                        dest="export_path", default=Settings.export_path,
                        help="Path to export to")
    parser.add_argument("-f", "--copy-filter", action="store",
                        dest="copy_filter", default=Settings.copy_filter,
                        help="Path to export to")
    parser.add_argument("-c", "--copy", action="store_true",
                        dest="do_copy", default=False,
                        help="Actually copy files. Default behavior is "
                             "only to print what files would be copied")
    parser.add_argument("-L", "--link", action="store_true",
                        dest="do_link", default=False,
                        help="Hard link files instead of copying. "
                             "This overwrites the copy option "
                             "(which is also still needed to "
                             "actually do something)")
    parser.add_argument("-V", "--version", action="version",
                        version=__version__,
                        help="display the version number")

    return parser.parse_args()


def process_arguments(arguments):
    """Recompute special cases for input arguments."""
    Settings.update(arguments)

    Settings.verbose = arguments.verbose + 1

    return arguments


def main():
    """Process arguments, load data and copy to filesystem."""
    raw_arguments = get_arguments()
    process_arguments(raw_arguments)

    folders_by_model, folders_by_uuid, albums = load_data()
    root_folder = build(folders_by_model, folders_by_uuid, albums)
    total_copied = copy_folders(root_folder, [], True)
    print('copied %s items in total' % total_copied)


if __name__ == '__main__':
    main()
