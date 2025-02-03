import argparse
import json
import os
import requests
from bs4 import BeautifulSoup

WATCHLIST_FILE = "watchlist.json"

print("Use python nepse.py --help if you need any help")

def get_stock_price(symbol):
    url = f"https://merolagani.com/CompanyDetail.aspx?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    price = soup.find("span", id="ctl00_ContentPlaceHolder1_CompanyDetail1_lblMarketPrice").text.strip()
    return float(price.replace(",", ""))

def load_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, "r") as file:
            return json.load(file)
    return {}

def save_watchlist(watchlist):
    with open(WATCHLIST_FILE, "w") as file:
        json.dump(watchlist, file, indent=4)

def add_stock(stock_name, bought_price, unit):
    watchlist = load_watchlist()
    if stock_name not in watchlist:
        watchlist[stock_name] = {"bought_price": bought_price, "unit": unit}
        save_watchlist(watchlist)
        print(f"Added {stock_name} ({unit} shares) to your watchlist.")
    else:
        print(f"{stock_name} is already in your watchlist.")

def remove_stock(stock_name):
    watchlist = load_watchlist()
    if stock_name in watchlist:
        del watchlist[stock_name]
        save_watchlist(watchlist)
        print(f"Removed {stock_name} from your watchlist.")
    else:
        print(f"{stock_name} is not in your watchlist.")

def display_watchlist():
    watchlist = load_watchlist()
    if not watchlist:
        print("Your watchlist is empty. Add stocks using 'nepse.py add <StockName> <BoughtPrice> <Unit>'.")
        return

    print("\nStock Name | LTP     | Change% | Unit | Total P/L")
    print("------------------------------------------------------")
    
    total_investment = 0
    total_gains = 0
    total_losses = 0

    for stock, data in watchlist.items():
        bought_price = data.get("bought_price")
        unit = data.get("unit")

        if bought_price is None or unit is None:
            print(f"Invalid data for {stock}. Skipping...")
            continue

        try:
            ltp = get_stock_price(stock)
            change_percent = ((ltp - bought_price) / bought_price) * 100
            total_pl = (ltp - bought_price) * unit
            investment = bought_price * unit
            total_investment += investment

            if total_pl > 0:
                total_gains += total_pl
            else:
                total_losses += total_pl

            print(f"{stock.ljust(10)} | {ltp:7.2f} | {change_percent:+.2f}%  | {unit:4} | {total_pl:+.2f}")
        except Exception as e:
            print(f"Error processing {stock}: {e}")

    print("\nSummary:")
    print(f"Total Investment: Rs {total_investment:.2f}")
    print(f"Total Gains:      Rs {total_gains:+.2f}")
    print(f"Total Losses:     Rs {total_losses:+.2f}")

def main():
    parser = argparse.ArgumentParser(description="NEPSE Stock Watchlist")
    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("add", help="Add a stock to your watchlist")
    add_parser.add_argument("stock_name", type=str, help="Name of the stock to add")
    add_parser.add_argument("bought_price", type=float, help="Price at which the stock was bought")
    add_parser.add_argument("unit", type=int, help="Number of shares bought")

    remove_parser = subparsers.add_parser("remove", help="Remove a stock from your watchlist")
    remove_parser.add_argument("stock_name", type=str, help="Name of the stock to remove")

    subparsers.add_parser("view", help="View your watchlist")

    args = parser.parse_args()

    if args.command == "add":
        add_stock(args.stock_name.upper(), args.bought_price, args.unit)
    elif args.command == "remove":
        remove_stock(args.stock_name.upper())
    elif args.command == "view":
        display_watchlist()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
