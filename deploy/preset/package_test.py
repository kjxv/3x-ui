import hashlib
import pathlib
import tempfile
import unittest

from package import verify_file


class FrozenPackageVerificationTest(unittest.TestCase):
    def test_corruption_cannot_be_packaged(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = pathlib.Path(directory) / 'runtime.tar.gz'
            original = b'frozen runtime bundle'
            archive.write_bytes(original)
            expected = hashlib.sha256(original).hexdigest()
            verify_file(archive, expected)
            archive.write_bytes(original + b'corrupt')
            with self.assertRaises(ValueError):
                verify_file(archive, expected)


if __name__ == '__main__':
    unittest.main()
