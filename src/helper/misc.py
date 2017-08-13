"""Collection of miscellaneous helper functions
"""
import itertools

# Fantastic function from http://stackoverflow.com/a/39946744/4943106
# to split columns with separators
def tidy_split(df, column, sep='|', keep=False):
    """
    Split the values of a column and expand so the new DataFrame has one split
    value per row. Filters rows where the column is missing.

    Args:
        df: A DataFrame with the column to split and expand
        column: The column to split and expand
        sep: The string used to split the column's values
        keep: Whether to retain the presplit value as it's own row

    Returns:
        A dataframe with the same columns as `df`
    """
    indexes = list()
    new_values = list()
    df = df.dropna(subset=[column])
    for i, presplit in enumerate(df[column].astype(str)):
        values = presplit.split(sep)
        if keep and len(values) > 1:
            indexes.append(i)
            new_values.append(presplit)
        for value in values:
            indexes.append(i)
            new_values.append(value)
    new_df = df.iloc[indexes, :].copy()
    new_df[column] = new_values

    return new_df

def generate_combinations(current_group):
    """Generates every combination given two lists

    Returns:
        A list of tuples containing every combinations from the two lists
    """
    cele = current_group['cele']
    hsap = current_group['hsap']
    orthologs = list(itertools.product(cele, hsap))
    return [(cele_tup, hsap_tup) for cele_tup, hsap_tup in orthologs]
