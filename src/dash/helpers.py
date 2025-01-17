from sklearn.preprocessing import Imputer
import pandas as pd
from openml import datasets
import scipy.stats
import numpy as np


def clean_dataset(df):

    df = df.loc[:, df.isnull().mean() < .8]
    out = df.fillna(df.mode().iloc[0])
    return out


def get_data_metadata(data_id: int):
    """ Download the dataset and get metadata

    :param data_id: ID of the OpenML dataset
    :return:
    """
    # Get data in pandas df format
    import time
    start = time.time()
    data = datasets.get_dataset(data_id)
    x, y, categorical, attribute_names = data.get_data()
    end = time.time()
    print("time taken get data", end-start)
    df = pd.DataFrame(x, columns=attribute_names)
    df.to_pickle('cache/df'+str(data_id)+'.pkl')

    # Get meta-features and add target
    features = pd.DataFrame([vars(data.features[i]) for i in range(0, len(data.features))])
    is_target = ["true" if name == data.default_target_attribute else "false" for name in features["name"]]
    features["Target"] = is_target

    # Extract #categories
    size = [str(len(value)) if value is not None else ' ' for value in features['nominal_values']]
    features['nominal_values'].replace({None: ' '}, inplace=True)
    features['# categories'] = size

    # choose features to be displayed
    meta_features = features[["name", "data_type", "number_missing_values", '# categories', "Target"]]
    meta_features.rename(columns={"name": "Attribute", "data_type": "DataType",
                                  "number_missing_values": "Missing values"}, inplace=True)
    meta_features.sort_values(by='Target', ascending=False, inplace=True)
    meta_features = meta_features[meta_features["Attribute"].isin(pd.Series(df.columns))]

    # Add entropy
    numerical_features = list(meta_features["Attribute"][meta_features["DataType"] == "numeric"])
    nominal_features = list(meta_features["Attribute"][meta_features["DataType"] == "nominal"])
    entropy = []

    for column in meta_features['Attribute']:
        if column in nominal_features:
            count = df[column].value_counts()
            ent = round(scipy.stats.entropy(count),2)
            entropy.append(ent)
        else:
            entropy.append(' ')
    meta_features['Entropy'] = entropy
    meta_features['Target'].replace({'false': ' '}, inplace=True)
    return df, meta_features, numerical_features, nominal_features, (vars(data)['name'])


def get_highest_rank(df, leaderboard):
    df.sort_values(by=['upload_time'], inplace=True)
    scores = []
    highest_rank = {}
    highest_score = {}

    setup_ids = []

    for index, row in df.iterrows():
        users = list(highest_score.keys())
        new_user = (row['uploader_name'] not in (users))
        if row['setup_id'] not in setup_ids or new_user:
            setup_ids.append(row['setup_id'])
            score = row['value']
            if new_user or (score not in scores):
                scores.append(score)
                scores.sort(reverse=True)
                rank = scores.index(score) + 1
                if new_user or (highest_score[row['uploader_name']] < score):
                   # highest_rank[row['uploader_name']] = rank
                    highest_score[row['uploader_name']] = score
                   # if highest_rank[row['uploader_name']] > row['Rank']:
                     #   highest_rank[row['uploader_name']] = row['Rank']
    #leaderboard['highest_rank'] = list(highest_rank.values())
    
    leaderboard['Top Score'] = list(highest_score.values())
    return leaderboard


def splitDataFrameList(df, target_column):
    """ df = dataframe to split,
    target_column = the column containing the values to split
    separator = the symbol used to perform the split
    returns: a dataframe with each entry for the target column separated, with each element moved into a new row.
    The values in the other columns are duplicated across the newly divided rows.
    """
    def splitListToRows(row,row_accumulator, target_column):
        split_row = row[target_column]
        for s in split_row:
            new_row = row.to_dict()
            new_row[target_column] = s
            row_accumulator.append(new_row)
    new_rows = []
    df.apply(splitListToRows,axis=1,args = (new_rows,target_column))
    new_df = pd.DataFrame(new_rows)
    return new_df
