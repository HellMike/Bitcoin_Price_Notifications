import requests
import time
from datetime import datetime
from collections.abc import Mapping

BITCOIN_API_URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
IFTTT_WEBHOOKS_URL = 'https://maker.ifttt.com/trigger/{}/with/key/csR7yQI3KCqE1SgDp2XzSk'
BITCOIN_PRICE_THRESHOLD = 10000


def get_latest_bitcoin_price():
    parameters = {
        'symbol': 'BTC,ETH',
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': 'ab0d1ade-88d7-49f1-bada-5086107a0fea',
    }

    response = requests.get(BITCOIN_API_URL, params=parameters, headers=headers).json()
    return float(response['data']['BTC']['quote']['USD']['price'])


def post_ifttt_webhook(event, value):
    # The payload that will be sent to IFTTT service
    data = {'value1': value}
    # inserts desired event
    ifttt_event_url = IFTTT_WEBHOOKS_URL.format(event)
    # Sends a HTTP POST request to the webhook URL
    requests.post(ifttt_event_url, json=data)


def format_bitcoin_history(bitcoin_history):
    rows = []
    for bitcoin_price in bitcoin_history:
        # Formats the date into a string: '24.02.2018 15:09'
        date = bitcoin_price['date'].strftime('%d.%m.%Y %H:%M')
        price = bitcoin_price['price']
        row = '{}: $<b>{}</b>'.format(date, price)
        rows.append(row)
    return '<br>'.join(rows)


def main():
    bitcoin_history = []
    while True:
        price = get_latest_bitcoin_price()
        date = datetime.now()
        bitcoin_history.append({'date': date, 'price': price})

        # Send an emergency notification
        if price < BITCOIN_PRICE_THRESHOLD:
            post_ifttt_webhook('bitcoin_price_emergency', price)

        # Send a Telegram notification
        if len(bitcoin_history) == 5:
            post_ifttt_webhook('bitcoin_price_update', format_bitcoin_history(bitcoin_history))
            # Reset the history
            bitcoin_history = []

        # Sleep for 5 minutes
        time.sleep(5 * 60)


if __name__ == '__main__':
    main()
