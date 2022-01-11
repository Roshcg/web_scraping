import re
import pickle
import os
from bs4 import BeautifulSoup
import requests
import csv

page = 'http://localhost:8000/home/m1049296/auto_mpg.html'

def process_data(soup):
    """
    Accepts a beautifulsoup object and processes data by extracting
    individual elements from html tags.
    :param soup: beautifulsoup object
    :return:
    """
    car_blocks = soup.find_all('div', class_='car_block')
    # print(car_blocks)
    rows = []
    for cb in car_blocks:
        row = extract_data(cb)
        rows.append(row)

    print(f'total entries {len(rows)}')
    print(type(row))
    print(rows[0])
    print(rows[-1])

    with open('scraped_cars.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames= row.keys())
        writer.writeheader()
        writer.writerows(rows)


def extract_data(cb):
    """
    Accepts individual car block having all the info about
    a single car
    :param cb: individual car block
    :return: a dict object having keys as field names and corresponding values
    """
    car_name = cb.find('span', class_='car_name').text
    mpg = extract_mpg(cb)
    cylinders = int(cb.find('span', class_='cylinders').text)
    hp = extract_horsepower(cb)
    weight = extract_weight(cb)
    acceleration = float(cb.find('span', class_='acceleration').text)
    country, year = extract_year_and_country(cb)
    displacement = extract_displacement(cb.text)
    row = dict(name=car_name,
               mpg=mpg,
               cylinders=cylinders,
               horse_power=hp,
               weight=weight,
               acceleration=acceleration,
               year=year,
               country=country,
               displacement=displacement)
    return row


def extract_year_and_country(cb):
    """
    Extract year and country from beautiful soup object
    """
    origin = cb.find('span', class_='from').text
    year, country = origin.strip('()').split(',')
    country = country.strip()
    return country, year


def extract_weight(cb):
    """
    Extract weight from beautiful soup object
    """
    weight_str = cb.find('span', class_='weight').text
    weight = int(weight_str.replace(',', ''))
    return weight


def extract_horsepower(cb):
    """
    Extract horsepower from beautiful soup object
    """
    try:
        hp = int(cb.find('span', class_='horsepower').text)
    except ValueError:
        hp = 'NULL'
    return hp


def extract_mpg(cb):
    """
    Extract miles per gallon from beautiful soup object
    """
    mpg_str = cb.find('span', class_='mpg').text
    try:
        mpg = float(mpg_str.split(' ')[0])
    except ValueError:
        mpg = 'NULL'
    return mpg


def extract_displacement(text):
    """
    Extract displacement from beautiful soup object
    """
    displacement_str = re.findall(r'.*(\d+.\d+) cubic inches', text)[0]
    displacement = float(displacement_str)
    return displacement


if __name__ == '__main__':
    file = 'scraped_web_results.pickle'
    # check for cached pickle file and load the contents
    # if it exists
    if os.path.exists(file):
        with open(file, 'rb') as f:
            print(f'Loading cached {file}')
            res = pickle.load(f)
    # if the pickle file doesn't exist create one and dump the data
    # scraped from the website
    else:
        res = requests.get(page)
        with open(file, 'wb') as f:
            print(f'Writing into cached {file}')
            pickle.dump(res, f)

    # check for the correct response from the site
    assert res.status_code == 200, f'received status code {res.status_code}'
    soup = BeautifulSoup(res.text, 'html.parser')
    process_data(soup)