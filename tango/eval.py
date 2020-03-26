# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/02_eval.ipynb (unless otherwise specified).

__all__ = ['calc_tf_idf', 'cosine_similarity']

# Cell
def calc_tf_idf(tfs, dfs):
    tf_idf = np.array([])
    for tf, df in zip(tfs, dfs):
        tf = tf / np.sum(tfs)
        idf = np.log(len(tfs) / (df + 1))
        tf_idf = np.append(tf_idf, tf * idf)

    return tf_idf

# Cell
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))