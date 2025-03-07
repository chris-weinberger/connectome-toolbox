import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_distances
from sklearn.metrics import pairwise_distances
from sklearn.manifold import MDS


 
def remove_self_connections(df):
    for i in range(len(df.index)):
        df.iloc[i,i] = 0


def analyze_data(file_path, columns):
    """Loads the dataset and returns basic statistics for the specified columns."""
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)
    else:
        return "Unsupported file format."

    missing_columns = [col for col in columns if col not in df.columns]
    if missing_columns:
        return f"Columns not found: {', '.join(missing_columns)}"

    stats = df[columns].describe().to_string()
    return f"Summary Statistics:\n{stats}"

def build_corr_matrix_full(df, distance_metric='pearson'):
    return compute_distance_matrix(df, metric=distance_metric)

    

def build_corr_matrix(df, ROI_list, filter_flag = False, min_num_connections=3, distance_metric='pearson'):
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
        cosine_distance_df = cosine_distance_df.dropna(axis=0, how='all').dropna(axis=1, how='all')
        return cosine_distance_df
    elif metric == "braycurtis":
        # using bray-curtis
        distance_matrix_bc = pairwise_distances(df.T, metric='braycurtis')
        bc_distance_df = pd.DataFrame(distance_matrix_bc, index=df.columns, columns=df.columns)
        bc_distance_df = bc_distance_df.dropna(axis=0, how='all').dropna(axis=1, how='all')
        return bc_distance_df
    elif metric == "pearson":
        # using pearson correlation
        distance_matrix = pd.DataFrame(1 - df.corr(), index=df.columns, columns=df.columns)
        distance_matrix = distance_matrix.dropna(axis=0, how='all').dropna(axis=1, how='all')
        return distance_matrix
    elif metric == "spearman":
        distance_matrix = pd.DataFrame(1 - df.corr(method='spearman'), index=df.columns, columns=df.columns)
        distance_matrix = distance_matrix.dropna(axis=0, how='all').dropna(axis=1, how='all')
        return distance_matrix
    else:
        distance_matrix = pd.DataFrame(1 - df.corr(), index=df.columns, columns=df.columns)
        distance_matrix = distance_matrix.dropna(axis=0, how='all').dropna(axis=1, how='all')
        return distance_matrix

# TODO: Implement this function -- When to clean the data?
def clean_correlation_matrix(df, major_division_labels):
    # get rows with all NaNs
    nan_rows = df.isna().all(axis=1)

    # drop rows and columns with all NaNs
    df_ret = df.dropna(axis=0, how='all').dropna(axis=1, how='all')

    # drop major division labels corresponding to rows with all NaNs
    major_division_labels_ret = major_division_labels[~nan_rows]

    return (df_ret, major_division_labels_ret)

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
    







