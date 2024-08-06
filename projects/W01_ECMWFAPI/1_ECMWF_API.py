# -*- coding: utf-8 -*-
"""
Created on Sun May 19 15:39:52 2024

@author: Soyeon Park

Description: Download ECMWF forecast results using API

How to use: python ECMWF_API.py --save <savepath> --date <forecast date to download>
Example usage: python ECMWF_API.py -s D:\Extract_spectra\ECMWF_forecast -d 20240311 20240312

"""

import os
import requests
from bs4 import BeautifulSoup
from typing import List
import argparse

def download_grib_files(url_template: str, date: str, base_dir: str, time: str, types: List[str]) -> None:
    """
    Download GRIB files for a specific date and time.
    
    Args:
    - url_template (str): URL template to construct the base URL.
    - date (str): Date string in the format YYYYMMDD.
    - base_dir (str): Base directory to save the files.
    - time (str): Time string (e.g., '00z', '12z').
    - types (List[str]): List of file types to download.
    """
    date_fmt = f"{date[:4]}_{date[4:6]}_{date[6:]}"
    target_dir = os.path.join(base_dir, date_fmt, time)
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    for t in types:
        url = url_template.format(date=date, time=time, file_type=t)
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a')
            
            for link in links:
                href = link.get('href')
                if href and href.endswith('.grib2'):
                    file_name = os.path.basename(href)
                    file_url = url + file_name
                    file_path = os.path.join(target_dir, file_name)
                    
                    with requests.get(file_url, stream=True) as r:
                        with open(file_path, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                    
                    print(f'{file_name} downloaded.')
            
            print(f'All files have been downloaded for {date} at {time}.')
        else:
            print(f'Failed to access {url}')

def lists_by_dates(dates: List[str], base_dir: str) -> None:
    """
    Download GRIB files for a list of dates and predefined times.
    
    Args:
    - dates (List[str]): List of date strings in the format YYYYMMDD.
    - base_dir (str): Base directory to save the files.
    """
    url_template = 'https://data.ecmwf.int/forecasts/{date}/{time}/ifs/0p25/{file_type}/'
    times_types = {
        '00z': ['oper', 'wave'],
        '12z': ['oper', 'wave'],
        '06z': ['scda', 'scwv'],
        '18z': ['scda', 'scwv']
    }

    for date in dates:
        for time, types in times_types.items():
            download_grib_files(url_template, date, base_dir, time, types)

def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
    - argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description='Download ECMWF forecasts')
    parser.add_argument('-s', '--save', type=str, required=True, help='Base directory to save the files')
    parser.add_argument('-d', '--date', type=str, nargs='+', required=True, help='List of dates in the format YYYYMMDD')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    lists_by_dates(args.date, args.save)


