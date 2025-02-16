import numpy as np
import pandas as pd

def aggregate_sum(dataframe, new_col_row_name, subregion_array):
    ret_df = dataframe.copy()
    row_sum = ret_df[ret_df.index.isin(subregion_array)].sum(axis=0)
    ret_df.loc[new_col_row_name] = row_sum
    
    # delete extra DHA subregions from rows
    ret_df = ret_df.loc[
    ~ret_df.index.isin(subregion_array)
    ]
    
    # columns
    col_sum = ret_df[subregion_array].sum(axis=1)
    ret_df.loc[:,new_col_row_name] = col_sum
    
    # delete extra LHA subregion from columns
    ret_df = ret_df.drop(subregion_array, axis=1)
    return ret_df

def aggregate_average(dataframe, new_col_row_name, subregion_array):
    ret_df = dataframe.copy()
    row_sum = ret_df[ret_df.index.isin(subregion_array)].mean(axis=0)
    ret_df.loc[new_col_row_name] = row_sum
    
    # delete extra DHA subregions from rows
    ret_df = ret_df.loc[
    ~ret_df.index.isin(subregion_array)
    ]
    
    # columns
    col_sum = ret_df[subregion_array].mean(axis=1)
    ret_df.loc[:,new_col_row_name] = col_sum
    
    # delete extra LHA subregion from columns
    ret_df = ret_df.drop(subregion_array, axis=1)
    return ret_df


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

def build_corr_matrix(df, ROI_list, filter_flag = False, min_num_connections=2):
    # dataframes representing connections FROM rows to columns (outgoing connections)
    df_from_ROI = df[df.index.isin(ROI_list)]

    # dataframes representing connections TO rows from columns (incoming connections)
    df_to = df.T
    df_to_ROI = df_to[df_to.index.isin(ROI_list)]

    # drop ROI columns
    # from - outgoing
    df_from_ROI = df_from_ROI.drop(ROI_list, axis=1)

    # to - incoming
    df_to_ROI = df_to_ROI.drop(ROI_list, axis=1)

    # filter dataframes if filter flag is passed
    if filter_flag:
        df_from_ROI = df_from_ROI.loc[:,df_from_ROI.apply(np.count_nonzero, axis=0) >=3]
        df_to_ROI = df_to_ROI.loc[:,df_to_ROI.apply(np.count_nonzero, axis=0) >=3]

    # create RSA matrix for incoming connections and outgoing connections
    rsa_mat_to_ROI = df_to_ROI.corr()
    rsa_mat_from_ROI = df_from_ROI.corr()

    # return tuple of rsa matrices. 
    # 1st represents representational similarity between regions that have incoming connections to ROI
    # 2nd represents representational similarity between regions that recieve outgoing connections from ROI
    return (rsa_mat_to_ROI, rsa_mat_from_ROI)

def visualize_rsa(corr_matrix, output_file, file_format="svg", figsize=(20,20), fig_title="RSA"):
    # plot heatmap of rsa using pearson correlation
    plt.figure(figsize=(20, 20))
    sns.heatmap(corr_matrix, fmt=".2f", cbar=True, square=True, xticklabels=True, yticklabels=True)
    plt.title(fig_title)
    plt.tight_layout()
    
    # Save the heatmap as an SVG file
    plt.savefig(output_file, format=file_format)
    
    # Show the plot
    plt.show()
    
    







