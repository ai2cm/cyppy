import os
import pytest
import cyppy


TEST_DIR = os.path.dirname(os.path.realpath(__file__))
PHYSICS_F90_DIR = os.path.join(TEST_DIR, '../lib/test')


def get_meta_files(dirname):
    return [fname for fname in os.listdir(dirname) if fname.endswith('.meta')]


@pytest.fixture(params=get_meta_files(PHYSICS_F90_DIR))
def meta_filename(request):
    return os.path.join(PHYSICS_F90_DIR, request.param)


def test_load_meta(meta_filename):
    cyppy.load_meta(meta_filename)


if __name__ == '__main__':
    test_load_meta()
