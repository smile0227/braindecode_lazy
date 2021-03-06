import pandas as pd
import numpy as np
import sys

from braindecode_lazy.datasets.dataset import Dataset

# avoid duplicates for reading file names by this ugly import
sys.path.insert(1, "/home/gemeinl/code/brainfeatures/")
from brainfeatures.data_set.tuh_abnormal import read_all_file_names


class Tuh(Dataset):
    def __init__(self, data_folder, n_recordings=None, target="pathological"):
        self.task = target
        assert data_folder.endswith("/"), "data_folder has to end with '/'"
        self.file_paths = read_all_file_names(data_folder, ".h5", key="time")
        self.gender_int_map = {"F": 1, "M": 0}
        self.channels = None
        if n_recordings is not None:
            self.file_paths = self.file_paths[:n_recordings]

        self.X, self.y, self.pathologicals = self.load(self.file_paths)

    def load(self, files):
        X, y, pathologicals = [], [], []
        for i, file_ in enumerate(files):
            x = pd.read_hdf(file_, key="data")
            if self.channels is None:
                self.channels = list(x.columns)
            xdim, ydim = x.shape
            if xdim > ydim:
                x = x.T
            x = np.array(x).astype(np.float32)
            X.append(x)

            info_df = pd.read_hdf(file_, key="info")
            assert len(info_df) == 1, "too many rows in info df"
            info = info_df.iloc[-1].to_dict()
            y_ = info[self.task]
            y.append(y_)
            pathologicals.append(info["pathological"])

        if self.task == "age":
            y = np.array(y).astype(np.float32)
        else:
            assert self.task in ["pathological", "gender"], "unknown task"
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # hacky, not necessary in newer versions of preprocessed data
            y = [self.gender_int_map[e]
                 if e in self.gender_int_map.keys()
                 else e
                 for e in y]
            y = np.array(y).astype(np.int64)
        return X, y, pathologicals


class TuhSubset(Dataset):
    def __init__(self, dataset, indices):
        self.task = dataset.task
        self.X = [dataset.X[i] for i in indices]
        self.y = np.array([dataset.y[i] for i in indices])
        self.file_paths = np.array([dataset.file_paths[i] for i in indices])
        self.pathologicals = np.array([dataset.pathologicals[i] for i in indices])
