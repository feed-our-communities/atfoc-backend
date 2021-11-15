from .tests import TEST_DIR
import shutil

def pytest_sessionfinish(session, exitstatus):
    shutil.rmtree(TEST_DIR)