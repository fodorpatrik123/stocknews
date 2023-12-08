from flask import Flask, render_template, request, redirect, url_for
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import json

app = Flask(__name__)

def get_ticker_from_url(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    ticker = query_params.get('q', [''])[0].upper()
    return ticker

def scrape_webpages(urls, div_id, class_name, limit=5):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    results = []
    for url in urls:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            div = soup.find(id=div_id)
            
            if div:
                elements = div.find_all(class_=class_name, limit=limit)
                for i, element in enumerate(elements, 1):
                    text = element.get_text().strip()
                    time_element = element.find_next(class_='js-date-relative txt-muted h-100')
                    time_text = time_element.get_text().strip() if time_element else 'Nincs időbélyeg'
                    ticker = get_ticker_from_url(url)
                    results.append({'ticker': ticker, 'news': text, 'time': time_text})
            else:
                results.append({'error': 'Nem létezik ilyen TICKER'})
        else:
            results.append({'error': 'Hiba a válaszkóddal'})
    
    return results

def save_tickers(tickers):
    with open('tickers.json', 'w') as file:
        json.dump(tickers, file)

def load_tickers():
    try:
        with open('tickers.json', 'r') as file:
            tickers = json.load(file)
    except FileNotFoundError:
        tickers = []
    return tickers

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ticker', methods=['GET', 'POST'])
def ticker():
    if request.method == 'POST':
        tickers = request.form.get('tickers')
        user_tickers_list = tickers.split(',')
        save_tickers(user_tickers_list)
        return render_template('ticker.html', tickers=user_tickers_list)
    tickers = load_tickers()
    return render_template('ticker.html', tickers=tickers)

@app.route('/result', methods=['POST'])
def result():
    tickers = load_tickers()
    base_url = 'https://www.marketscreener.com/search/?q='
    urls = [base_url + ticker.strip() for ticker in tickers]
    
    div_id = 'advanced-search__news'
    class_name = 'w-100'
    
    results = scrape_webpages(urls, div_id, class_name)
    
    return render_template('result.html', results=results)

@app.route('/manage')
def manage():
    tickers = load_tickers()
    return render_template('manage.html', tickers=tickers)

@app.route('/add_ticker', methods=['POST'])
def add_ticker():
    new_ticker = request.form.get('new_ticker')
    tickers = load_tickers()
    tickers.append(new_ticker)
    save_tickers(tickers)
    return redirect('/manage')

@app.route('/delete_ticker', methods=['POST'])
def delete_ticker():
    delete_ticker = request.form.get('delete_ticker')
    tickers = load_tickers()
    if delete_ticker in tickers:
        tickers.remove(delete_ticker)
        save_tickers(tickers)
    return redirect('/manage')
if __name__ == '__main__':
    app.run(host='0.0.0.0')
