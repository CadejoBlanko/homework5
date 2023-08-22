from datetime import datetime, timedelta
import logging

import aiohttp
import asyncio


async def request(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    r = await resp.json()
                    return r
                logging.error(f"Error status: {resp.status} for {url}")
                return None
        except aiohttp.ClientConnectionError as err:
            logging.error(f"Connection error: {str(err)}")
            return None


async def get_exchange(currency_code, valid_date):
    result = await request(f"https://api.privatbank.ua/p24api/exchange_rates?date={valid_date}")
    if result: 
        rates = result.get('exchangeRate')
        exc, = list(filter(lambda element: element["currency"] == currency_code, rates))
        return f"{currency_code}: buy: {exc['purchaseRateNB']}, sale: {exc['saleRateNB']}. Date: {valid_date}"
    return "Failed to retrieve data"


def get_valid_date():
    while True:
        try:
            input_date_str = input("Enter a date (dd.mm.yyyy): ")
            input_date = datetime.strptime(input_date_str, "%d.%m.%Y")
            
            current_date = datetime.now()
            max_valid_date = current_date + timedelta(days=10)
            
            if input_date <= max_valid_date:
                return input_date.strftime("%d.%m.%Y")
            else:
                print("The date should be within the next 10 days.")
        except ValueError:
            print("Invalid date format. Please use dd.mm.yyyy.")


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    currency_code = input("Currency code: ")
    valid_date = get_valid_date()
    result = asyncio.run(get_exchange(currency_code, valid_date))
    print(result)