import json
import threading
from pkg_resources import resource_filename


class LazyLoadedDict(dict):
    BASE_PACKAGE = "fixinventorydata"
    DATA_DIR = "data"

    def __init__(self, filename):
        self._data_file = resource_filename(self.BASE_PACKAGE, f"{self.DATA_DIR}/{filename}")
        self._data = None
        self._lock = threading.Lock()

    def _load_data(self):
        if self._data is None:
            with self._lock:
                if self._data is None:
                    with open(self._data_file) as f:
                        self._data = json.load(f)
                    super().update(self._data)

    def __getitem__(self, key):
        self._load_data()
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        self._load_data()
        super().__setitem__(key, value)

    def __delitem__(self, key):
        self._load_data()
        super().__delitem__(key)

    def __contains__(self, key):
        self._load_data()
        return super().__contains__(key)

    def __len__(self):
        self._load_data()
        return super().__len__()

    def __iter__(self):
        self._load_data()
        return super().__iter__()

    def keys(self):
        self._load_data()
        return super().keys()

    def values(self):
        self._load_data()
        return super().values()

    def items(self):
        self._load_data()
        return super().items()

    def get(self, key, default=None):
        self._load_data()
        return super().get(key, default)

    def pop(self, key, default=None):
        self._load_data()
        return super().pop(key, default)

    def popitem(self):
        self._load_data()
        return super().popitem()

    def update(self, *args, **kwargs):
        self._load_data()
        super().update(*args, **kwargs)

    def setdefault(self, key, default=None):
        self._load_data()
        return super().setdefault(key, default)

    def copy(self):
        self._load_data()
        return super().copy()

    def __eq__(self, other):
        if not isinstance(other, dict):
            return NotImplemented
        self._load_data()
        return super().__eq__(other)

    def __ne__(self, other):
        if not isinstance(other, dict):
            return NotImplemented
        self._load_data()
        return super().__ne__(other)
