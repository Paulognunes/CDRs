# Imports
import pickle


def save_with_pickle(file, directory, file_name):
    path = directory + file_name + '.pkl'
    with open(path, "wb") as f:
        pickle.dump(file, f)


def load_with_pickle(directory, file_name):
    path = directory + file_name + '.pkl'
    with open(path, "rb") as f:
        return pickle.load(f)
