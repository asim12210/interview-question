from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from datetime import datetime
import sqlite3
from typing import List, Optional
import pdfkit
from pdfkit.api import configuration

app = FastAPI()

DATABASE = 'racing_data.db'
wkhtml_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

class RaceData(BaseModel):
    日期: str
    場次: str
    名次: str
    馬號: str
    馬名: str
    騎師: str
    練馬師: str
    排位體重: int
    實際負磅: int
    檔位: int
    頭馬距離: str
    沿途走位: str
    完成時間: str
    獨嬴賠率: float

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def convert_date_format(input_date: str) -> str:
    try:
        dt = datetime.strptime(input_date, '%Y-%m-%d')
        return dt.strftime('%d/%m/%Y')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

@app.get("/races", response_model=List[RaceData])
def read_races():
    conn = get_db_connection()
    races = conn.execute('SELECT * FROM races ORDER BY 日期 ASC, 場次 ASC').fetchall()
    conn.close()
    return [dict(race) for race in races]

@app.get("/races/{date}", response_model=List[RaceData], description="Dates must be in YYYY-MM-DD format.")
def read_races_by_date(date: str = Path(description='日期 YYYY-MM-DD'), race_no: int | None = Query(default=None, description='場次')):
    date = convert_date_format(date)
    conn = get_db_connection()
    print(f'日期:{date}')
    if race_no is not None:
        races = conn.execute('SELECT * FROM races WHERE 日期 = ? AND 場次 = ?', (date, race_no)).fetchall()
    else:
        races = conn.execute('SELECT * FROM races WHERE 日期 = ? ORDER BY 日期 DESC, 場次 ASC', (date,)).fetchall()
    conn.close()
    if not races:
        raise HTTPException(status_code=404, detail="No races found for the given date and race number")
    return [dict(race) for race in races]
    
def generate_pdf(races: List[dict], pdf_path: str):
    date = ''
    race_no = ''
    if races[0]['日期'] == races[-1]['日期']:
        date = f"日期：{datetime.strptime(races[0]['日期'], '%d/%m/%Y').strftime('%Y-%m-%d')}"
        if races[0]['場次'] == races[-1]['場次']:
            race_no = f"場次：{races[0]['場次']}"
        else:
            race_no = f"場次：{races[0]['場次']} - {races[-1]['場次']}"
    else:
        date = f"日期：{datetime.strptime(races[0]['日期'], '%d/%m/%Y').strftime('%Y-%m-%d')} - {datetime.strptime(races[-1]['日期'], '%d/%m/%Y').strftime('%Y-%m-%d')}"
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Racing Data PDF</title>
        <style>
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                border: 1px solid black;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
                white-space: nowrap;
            }}
        </style>
    </head>
    <body>
        <h1>Racing Data</h1>
        <h2>{ date }</h2>
        <h3>{ race_no }</h3>
        <table>
            <thead>
                <tr>
                    <th>日期</th>
                    <th>場次</th>
                    <th>名次</th>
                    <th>馬號</th>
                    <th>馬名</th>
                    <th>騎師</th>
                    <th>練馬師</th>
                    <th>排位體重</th>
                    <th>實際負磅</th>
                    <th>檔位</th>
                    <th>頭馬距離</th>
                    <th>沿途走位</th>
                    <th>完成時間</th>
                    <th>獨嬴賠率</th>
                </tr>
            </thead>
            <tbody>
    '''
    for race in races:
        html_content += f'''
            <tr>
                <td>{ race["日期"] }</td>
                <td>{ race["場次"] }</td>
                <td>{ race["名次"] }</td>
                <td>{ race["馬號"] }</td>
                <td>{ race["馬名"] }</td>
                <td>{ race["騎師"] }</td>
                <td>{ race["練馬師"] }</td>
                <td>{ race["排位體重"] }</td>
                <td>{ race["實際負磅"] }</td>
                <td>{ race["檔位"] }</td>
                <td>{ race["頭馬距離"] }</td>
                <td>{ race["沿途走位"] }</td>
                <td>{ race["完成時間"] }</td>
                <td>{ race["獨嬴賠率"] }</td>
            </tr>
        '''
    html_content += '''
            </tbody>
        </table>
    </body>
    </html>
    '''
    options = {
        'page-size': 'Letter',
        'margin-top': '0.25in',
        'margin-right': '0.25in',
        'margin-bottom': '0.25in',
        'margin-left': '0.25in',
        'encoding': "UTF-8",
        'no-outline': None
    }
    
    pdfkit.from_string(
        html_content, 
        pdf_path, 
        configuration = pdfkit.configuration(wkhtmltopdf = wkhtml_path),
        options=options
    )

@app.get("/download/races")
def download_races():
    races_data = read_races()
    if not races_data:
        raise HTTPException(status_code=404, detail="No races data")
    pdf_path = r"\racing_data.pdf"
    pdf_name = "racing_data.pdf"
    generate_pdf(races_data, pdf_path)
    return FileResponse(pdf_path, media_type='application/pdf', filename=pdf_name)

@app.get("/download/races/{date}")
def download_races_by_date(date: str, race_no: Optional[int] = Query(None)):
    races_data = read_races_by_date(date, race_no)
    if not races_data:
        raise HTTPException(status_code=404, detail="No races found for the given date and race number")
    pdf_path = r"\racing_data.pdf"
    pdf_name = f"racing_data_{date}.pdf" if race_no is None else f"racing_data_{date}_{race_no}.pdf"
    generate_pdf(races_data, pdf_path)
    return FileResponse(pdf_path, media_type='application/pdf', filename=pdf_name)

