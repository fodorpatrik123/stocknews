import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import time

def get_ticker_from_url(url):
    # Kinyerjük a ticker-t az URL-ből
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    ticker = query_params.get('q', [''])[0].upper()  # Az 'q' paraméter értéke, és nagybetűsítve
    
    return ticker

def scrape_webpages(urls, div_id, class_name, limit=5):
    # Az user-agent beállítása
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    while True:
        for url in urls:
            # Oldal letöltése
            response = requests.get(url, headers=headers)
            
            # Ellenőrizze a válasz státuszát
            if response.status_code == 200:
                # Oldal tartalmának analizálása BeautifulSoup segítségével
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Az adott div id alatti összes elem kinyerése
                div = soup.find(id=div_id)
                
                if div:
                    # Az összes elem kinyerése a megadott osztály név alapján
                    elements = div.find_all(class_=class_name, limit=limit)
                    
                    # Az elemek szövegének és a hozzájuk tartozó time elemek kiírása
                    for i, element in enumerate(elements, 1):
                        text = element.get_text().strip()
                        
                        # A hozzátartozó time elem keresése
                        time_element = element.find_next(class_='js-date-relative txt-muted h-100')
                        time_text = time_element.get_text().strip() if time_element else 'Nincs időbélyeg'
                        
                        # Ticker kinyerése az URL-ből
                        ticker = get_ticker_from_url(url)
                        
                        print(f'Ticker: {ticker} | News {i}: {text} | Time: {time_text}')
                else:
                    print(f'Nem létezik ilyen TICKER')
            else:
                print(f'Hiba a válaszkóddal')
        
        # Várakozás 1 perc, mielőtt újra lekérdezné az oldalakat
        time.sleep(60)

# Felhasználói inputok fogadása a tickerekhez
user_tickers = input("Adja meg a tickereket vesszővel elválasztva: ")
user_tickers_list = user_tickers.split(',')

# Az URL-ek generálása a felhasználó által megadott tickerek alapján
base_url = 'https://www.marketscreener.com/search/?q='
urls = [base_url + ticker.strip() for ticker in user_tickers_list]

div_id = 'advanced-search__news'
class_name = 'w-100'
scrape_webpages(urls, div_id, class_name)
