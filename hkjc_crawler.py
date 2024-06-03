import requests
from bs4 import BeautifulSoup
import json
import os
import sqlite3
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = 'https://racing.hkjc.com/racing/information/Chinese/Racing/LocalResults.aspx'
DATABASE = 'racing_data.db'

def fetch_race_data(date, race_no):
    data = []
    try:
        url = f'{BASE_URL}?RaceDate={date}&RaceNo={race_no}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        race_table = soup.select_one('.table_bd')  # Find the first table in html
        if race_table:
            header = race_table.find_all('tr')[1]
            rows = race_table.find_all('tr')[1:]  # Skip header

            for row in rows:
                columns = row.find_all('td')
                pos = ''
                finish_time = '---'
                win_odds = 0.0
                if len(columns) == 12: # If race not established column[11] not exists
                    pos         = columns[9].get_text(" ", strip=True) # keep space in string
                    finish_time = columns[10].get_text(strip=True)
                    win_odds    = float(columns[11].get_text(strip=True) if columns[11].get_text(strip=True) != '---' else '0.0') # If no data give 0.0  
                else: 
                    finish_time = columns[9].get_text(strip=True)
                race_data = {
                    "日期": convert_date_format(date),
                    "場次": str(race_no),
                    "名次": columns[0].get_text(strip=True),
                    "馬號": columns[1].get_text(strip=True),
                    "馬名": columns[2].get_text(strip=True),
                    "騎師": columns[3].get_text(strip=True),
                    "練馬師": columns[4].get_text(strip=True),
                    "排位體重": int(columns[5].get_text(strip=True) if columns[5].get_text(strip=True) != '---' else '0'), # If no data give 0  
                    "實際負磅": int(columns[6].get_text(strip=True) if columns[6].get_text(strip=True) != '---' else '0'), # If no data give 0  
                    "檔位":    int(columns[7].get_text(strip=True) if columns[7].get_text(strip=True) != '---' else '0'), # If no data give 0  
                    "頭馬距離": columns[8].get_text(strip=True),
                    "沿途走位": str(pos),
                    "完成時間": finish_time,
                    "獨嬴賠率": win_odds
                }
                
                data.append(race_data)
    except Exception as e:
        # print(f'error ==> date:{date}&race_no:{race_no} exception: {e}')
        pass
    return data

def fetch_all_races(conn):
    all_race_data = []
    dates = get_available_dates()
    today = datetime.now()
    for date in dates:
        if datetime.strptime(date, '%d/%m/%Y') > today: # If date grather then today, don't fetch
            continue
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {}
            race_no = 1
            while True:
                if is_fetched(date, race_no, conn): # Check date&race_no from db, avoid fetch data duplicate 
                    race_no += 1
                    continue
                futures[executor.submit(fetch_race_data, date, race_no)] = race_no
                if race_no > 15:  # Assuming a maximum of 15 races per day, usually 8~9 races per day
                    break
                race_no += 1
            for future in as_completed(futures):
                race_no = futures[future]
                try:
                    race_data = future.result()
                    if race_data:
                        all_race_data.extend(race_data)
                except Exception as e:
                    # print(f'error ==> date:{date}&race_no:{race_no} exception: {e}')
                    pass
    return all_race_data

def convert_date_format(input_date: str) -> str:
    dt = datetime.strptime(input_date, '%d/%m/%Y')
    return dt.strftime('%Y-%m-%d')

def get_available_dates():
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    date_elements = soup.select_one('#selectId').find_all('option')  # Find all option from the date select
    dates = [element['value'] for element in date_elements if 'value' in element.attrs]  # Get value from the option
    return dates

def save_to_json(data, filename='race_data.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS races (
            日期 TEXT,
            場次 TEXT,
            名次 TEXT,
            馬號 TEXT,
            馬名 TEXT,
            騎師 TEXT,
            練馬師 TEXT,
            排位體重 INTEGER,
            實際負磅 INTEGER,
            檔位 INTEGER,
            頭馬距離 TEXT,
            沿途走位 TEXT,
            完成時間 TEXT,
            獨嬴賠率 REAL
        )
    ''')
    conn.commit()
    conn.close()

def save_to_sqlite(data, db_name='racing_data.db'):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    
    for race in data:
        c.execute('''
            INSERT INTO races VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (race['日期'], race['場次'], race['名次'], race['馬號'], race['馬名'], race['騎師'], race['練馬師'],
              race['排位體重'], race['實際負磅'], race['檔位'], race['頭馬距離'], race['沿途走位'], race['完成時間'], race['獨嬴賠率']))
    conn.commit()
    conn.close()

def is_fetched(date, race_no, conn):
    c = conn.cursor()
    c.execute('SELECT 1 FROM races WHERE 日期 = ? AND 場次 = ?', (date, race_no))
    return c.fetchone() is not None

def update_daily_data():
    create_db()
    conn = get_db_connection()
    all_race_data = fetch_all_races(conn)
    # save_to_json(all_race_data, filename='racing_data.json')
    save_to_sqlite(all_race_data, db_name='racing_data.db')
    conn.close()