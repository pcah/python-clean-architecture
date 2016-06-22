from contextlib import contextmanager
import warnings


@contextmanager
def catch_warning(warning_cls):
    with warnings.catch_warnings():
        warnings.filterwarnings('error', category=warning_cls)
        yield
