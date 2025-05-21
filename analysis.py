import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_distances
from sklearn.metrics import pairwise_distances
from sklearn.manifold import MDS



def build_corr_matrix_full(df, distance_metric='pearson'):
    return compute_distance_matrix(df, metric=distance_metric)


def build_corr_matrix(df, ROI_list, filter_flag = False, min_num_connections=1, distance_metric='pearson'):
    # if they haven't supplied columns, just perform RSA on all columns
    if (len(ROI_list) == 0):
        rsa_mat = compute_distance_matrix(df, metric=distance_metric)
        return (rsa_mat, rsa_mat)
    # dataframes representing connections FROM rows to columns (outgoing connections)
    df_from_ROI = df[df.index.isin(ROI_list)]

    # dataframes representing connections TO rows from columns (incoming connections)
    df_to = df.T
    df_to_ROI = df_to[df_to.index.isin(ROI_list)]

    # drop ROI columns
    # from (outgoing)
    df_from_ROI = df_from_ROI.drop(ROI_list, axis=1)

    # to (incoming)
    df_to_ROI = df_to_ROI.drop(ROI_list, axis=1)

    # filter dataframes if filter flag is passed
    if filter_flag:
        df_from_ROI = df_from_ROI.loc[:,df_from_ROI.apply(np.count_nonzero, axis=0) >= min_num_connections]
        df_to_ROI = df_to_ROI.loc[:,df_to_ROI.apply(np.count_nonzero, axis=0) >= min_num_connections]

    # create RSA matrix for incoming connections and outgoing connections
    rsa_mat_to_ROI = compute_distance_matrix(df_to_ROI, metric=distance_metric)
    rsa_mat_from_ROI = compute_distance_matrix(df_from_ROI, metric=distance_metric)

    # clean the data by removing the rows and columns with all NaNs
    rsa_mat_to_ROI = rsa_mat_to_ROI.dropna(axis=0, how='all').dropna(axis=1, how='all')
    rsa_mat_from_ROI = rsa_mat_from_ROI.dropna(axis=0, how='all').dropna(axis=1, how='all')

    # return tuple of rsa matrices. 
    # 1st represents representational similarity between regions that have incoming connections to ROI
    # 2nd represents representational similarity between regions that recieve outgoing connections from ROI
    return (rsa_mat_to_ROI, rsa_mat_from_ROI)

def compute_distance_matrix(df, metric="pearson"):
    # compute distance matrix, drop rows and columns with all NaNs
    if metric == "cosine":
        # using cosine distances
        cosine_distance_matrix = cosine_distances(df.T)
        cosine_distance_df = pd.DataFrame(cosine_distance_matrix, index=df.columns, columns=df.columns)
        return cosine_distance_df
    elif metric == "braycurtis":
        # using bray-curtis
        distance_matrix_bc = pairwise_distances(df.T, metric='braycurtis')
        bc_distance_df = pd.DataFrame(distance_matrix_bc, index=df.columns, columns=df.columns)
        return bc_distance_df
    elif metric == "pearson":
        # using pearson correlation
        distance_matrix = pd.DataFrame(1 - df.corr(), index=df.columns, columns=df.columns)
        return distance_matrix
    elif metric == "spearman":
        distance_matrix = pd.DataFrame(1 - df.corr(method='spearman'), index=df.columns, columns=df.columns)
        return distance_matrix
    else:
        distance_matrix = pd.DataFrame(1 - df.corr(), index=df.columns, columns=df.columns)
        return distance_matrix

def compute_mds(rsa_matrix, n_components=2, group_labels=None):
    #MDS requires dissimilarity matrix
    # Perform MDS
    mds = MDS(n_components=n_components, dissimilarity='precomputed', random_state=42)
    embedding = mds.fit_transform(rsa_matrix)

    # Create a DataFrame for the results
    mds_result = pd.DataFrame(embedding, columns=['Dim1', 'Dim2'], index=rsa_matrix.index)

    if group_labels is not None:
        mds_result['Group'] = group_labels

    return mds_result
    
    # TODO: Implement this function -- When to clean the data?
def clean_correlation_matrix(df, major_division_labels):
    # get rows with all NaNs
    nan_rows = df.isna().all(axis=1)

    # drop rows and columns with all NaNs
    df_ret = df.dropna(axis=0, how='all').dropna(axis=1, how='all')

    # drop major division labels corresponding to rows with all NaNs
    major_division_labels_ret = major_division_labels[~nan_rows]

    return (df_ret, major_division_labels_ret)
    

