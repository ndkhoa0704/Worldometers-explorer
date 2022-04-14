# Combine multiple data files
import pandas as pd
import numpy as np
import re
import os
import datetime as dt

def load(file_path):
    files = os.listdir(file_path)
    # Sort dates
    dates = [dt.datetime.strptime(re.findall(r'\d{4}-[04]-\d{2}',f)[0],'%Y-%m-%d') for f in files]
    dates = sorted(dates,reverse=False)
    dates = [i.strftime('%Y-%m-%d') for i in dates]
    # Create a dict with keys are dates and values are data of those dates
    dfs_raw = {d: pd.read_csv(f'{file_path}/worldometers-{d}.tsv',sep="\t") for d in dates}
    print(dfs_raw.keys())
# def combine():
    

def main():
    file_path = '../data'
    load(file_path)

if __name__=='__main__':
    main()
