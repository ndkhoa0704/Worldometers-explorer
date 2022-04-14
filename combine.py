# Combine multiple data files

import pandas as pd
import re
import os
import datetime as dt

def load(path: str):
    files = os.listdir(path)
    # Extract
    dates = []
    for f in files:
        tmp = re.search(r'\d{4}-\d{1}[4]-\d{2}', f)
        if tmp != None:
            dates.append(dt.datetime.strptime(tmp.group(), r'%Y-%m-%d'))

    # Sort dates
    dates = sorted(dates,reverse=False)
    dates = [i.strftime('%Y-%m-%d') for i in dates]
    # Create a dict with keys are dates and values are data of those dates
    dfs_raw = {d: pd.read_csv(f'{path}/worldometers-{d}.tsv',sep="\t") for d in dates}

    return dfs_raw, dates

def combine(raw: dict, dates: list, path: str):
    # Countries
    features = list(raw[dates[0]].columns)
    countries = list(raw[dates[0]]['Country,Other'])
    for c in countries:
        country_df = pd.DataFrame(columns=['Date'] + features)
        for d in dates:
            row = pd.Series([d]).append(pd.Series(raw[d][raw[d]['Country,Other'] == c].iloc[0].to_list()))
            row.index=['Date'] + features
            row.name = 0
            country_df = country_df.append(row, ignore_index=True)

        country_df.to_csv(path + f'/Countries/{c}.tsv', sep='\t',index=False)
    
    # World
    world = pd.DataFrame(columns=['Date'] + features[1:-1])
    for d in dates:
        row = pd.Series([d], index=['Date']).append(raw[d].iloc[:, 1:-1].sum(axis=0))
        world = world.append(row, ignore_index=True)

    world.to_csv(path + '/World.tsv', sep='\t', index=False)

def main():
    data_path = './data'
    processed_path = './combined'
    raw, dates = load(data_path)
    combine(raw, dates, processed_path)

if __name__=='__main__':
    main()
