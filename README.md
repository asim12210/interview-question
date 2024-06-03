# Interview Question Repository

## Files

1. **hkjc_crawler.py**: A web crawler script designed to fetch races data(local) from the Hong Kong Jockey Club (HKJC) website.

2. **main.py**: The main script to execute the crawler and handle the data.

## Requirements

- Python 3.x
- Required libraries: requests, BeautifulSoup4, fastapi, uvicorn, pydantic, pdfkit.
- `wkhtmltopdf` for PDF generation

## Setup

1. Clone the repository:
	```bash
	git clone https://github.com/asim12210/interview-question.git
	```
2. Install the required libraries:
	```bash
	pip install -r requirements.txt
	```
3. (optional) Install `wkhtmltopdf`for download data in PDF file:
	On Ubuntu:
	```bash
	sudo apt-get install wkhtmltopdf
	```
	On macOS using Homebrew:
	```bash
	brew install wkhtmltopdf
	```	
	On Windows:
	-   Download the installer from the <a href="https://wkhtmltopdf.org/">wkhtmltopdf website</a>.
	-   Run the installer and follow the instructions.
4. (optional) Edit the `main.py` file to configure the path for `pdfkit`
	```python
	wkhtml_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
	```
	Replace `C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe` with the actual path to the `wkhtmltopdf` executable like the example below:
-   On Ubuntu: `/usr/local/bin/wkhtmltopdf`
-   On macOS (with Homebrew): `/usr/local/bin/wkhtmltopdf`
-   On Windows: `C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe`

## Usage
### Start web server
Run the main script
 ```bash
python main.py
```

### Start crawler
1.  Open your web browser and navigate to `http://localhost:8000/start-crawler`.
2.  The crawler will start, and you can monitor its progress via the terminal or browser interface.

### Using the API to get data
**Get all data**

 1. Endpoint: `/races`
 2. Method: GET
 3. Example:
	 ``` bash
	curl -X GET "http://localhost:8000/races"
	```


**Get data by date**
 1. Endpoint: `/races/<date>`
 2. Method: GET
 3. Path Parameter: `date` (required): Specify a date to fetch data for a particular day. Format: `YYYY-MM-DD`.
 4. Query Parameter: `race_no` (optional): Specify the race number to fetch data for a particular race on that day
  
5. Example request with race number:
	```bash
	curl -X GET "http://localhost:8000/races/2024-05-29?race_no=2"
	```
 6. Example request without race number:
	```bash
	curl -X GET "http://localhost:8000/races/2024-05-26"
	```

**Download data in PDF (wkhtmltopdf is required)**
 1. Endpoint: `/races`
 2. Method: GET
 3. Example:
	 ``` bash
	curl -X GET "http://localhost:8000/download/races"
	```

**Download data in PDF by date (wkhtmltopdf is required)**
 1. Endpoint: `/download/races/<date>`
 2. Method: GET
 3. Path Parameter: `date` (required): Specify a date to fetch data for a particular day. Format: `YYYY-MM-DD`.
 4. Query Parameter: `race_no` (optional): Specify the race number to fetch data for a particular race on that day
 5. Example request with race number:
	 ``` bash
	curl -X GET "http://localhost:8000/download/races/2024-05-29?race_no=2"
	```
6. Example request without race number:
	``` bash
	curl -X GET "http://localhost:8000/download/races/2024-05-26"
	```

