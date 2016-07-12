import sys
from unittest import TestCase
from magritte.cli import main


class TestConsole(TestCase):
    def test_basic(self):
        sys.argv += ['-V']
        with self.assertRaises(SystemExit) as cm:
            main()

        self.assertEqual(cm.exception.code, 0)
