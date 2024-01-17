import time
import pandas as pd
import datetime
import os
import matplotlib.pyplot as plt
import requests
import csv


def acquire_user_input():

    user_name = input('Please enter user name: ')

    user_name = user_name.lower()

    ticker = input('Please enter a valid stock ticker: ')

    valid_ticker = validate_stock_ticker(ticker)

    while valid_ticker == False:
        ticker = input(
            'Error: Invalid ticker. Please enter a valid stock ticker: ')
        valid_ticker = validate_stock_ticker(ticker)

    year1 = int(
        input('Please enter the year of which to begin our data analysis: '))

    month1 = int(
        input('Please enter the month of which to begin our data analysis (1-12): '))
    while month1 < 1 or month1 > 12:
        month1 = int(
            input('Error: Invalid month. Please enter the month of which to begin our data analysis (1-12): '))

    year2 = int(
        input('Please enter the year of which to end our data analysis: '))

    month2 = int(
        input('Please enter the month of which to end our data analysis: (1-12) '))
    while month2 < 1 or month2 > 12:
        month2 = int(
            input('Error: Invalid month. Please enter the month of which to begin our data analysis (1-12): '))
    interval_options = ('1d', '1wk', '1mo')

    interval = input(
        'Enter the interval of which to gather data from (1d/1wk/1mo): ')

    while interval not in interval_options:
        interval = input(
            'Error: Invalid Input. Enter the interval of which to gather data from (1d/1wk/1mo): ')
    if month1 < 10:

        start_date = f'{year1}-0{month1}-01'
    else:
        start_date = f'{year1}-{month1}-01'

    if month2 < 10:

        end_date = f'{year2}-0{month2}-28'
    else:
        end_date = f'{year2}-{month2}-28'

    return user_name, ticker, year1, month1, year2, month2, interval, start_date, end_date


# def get_earliest_year(ticker):
#     url = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}'

#     params = {'period1': 0, 'period2': int(
#         datetime.datetime.now().timestamp()), 'interval': '1d'}
#     response = requests.get(url, params=params)

#     lines = response.text.strip().splitlines()
#     header = lines[0]

#     earliest_date_str = lines[-1].split(',')[0]

#     earliest_date = datetime.datetime.strptime(
#         earliest_date_str, "%r")

#     return earliest_date.year


def validate_stock_ticker(ticker):
    url = f'https://www.cnbc.com/quotes/{ticker}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return True

    except:
        return False


def get_sp500_data(interval, curr_spy_start_date, curr_spy_end_date):

    start_year = curr_spy_start_date[:4]
    start_month = curr_spy_start_date[5:7]
    end_year = curr_spy_end_date[:4]
    end_month = curr_spy_end_date[5:7]

    period1 = int(time.mktime(datetime.datetime(
        int(start_year), int(start_month), 1, 23, 59).timetuple()))

    period2 = int(time.mktime(datetime.datetime(
        int(end_year), int(end_month), 28, 23, 59).timetuple()))

    url = f'https://query1.finance.yahoo.com/v7/finance/download/SPY?period1={period1}&period2={period2}&interval={interval}&events=history&includeAdjustedClose=true'

    out = pd.read_csv(url)

    return out


def get_user_choice_stock_info(ticker, year1, year2, month1, month2, interval):

    period1 = int(time.mktime(datetime.datetime(
        year1, month1, 1, 23, 59).timetuple()))

    period2 = int(time.mktime(datetime.datetime(
        year2, month2, 28, 23, 59).timetuple()))

    url = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={period1}&period2={period2}&interval={interval}&events=history&includeAdjustedClose=true'

    out = pd.read_csv(url)

    return out


def create_new_csv_file(user_name):
    file_path = f'{user_name}.csv'

    fp = open(file_path, 'w', newline='')

    fp.close()

    return fp


def clear_csv_file(user_name):

    file_path = f'{user_name}.csv'

    with open(file_path, mode='w', newline='') as csv_file:
        pass


def write_to_csv(user_name, stock_name, data):

    file_path = f'{user_name}.csv'

    data.to_csv(file_path, index=False)


def check_if_file_exists(user_name):

    file_path = f'{user_name}.csv'

    if os.path.exists(file_path):
        return True
    return False


def add_ticker_to_csv(ticker, file):
    df = pd.read_csv(file)

    df['Stock Ticker'] = ticker

    df.to_csv(file, index=False)


def plot_closing_price(user_name, ticker, year1, month1, year2, month2):
    df = pd.read_csv(f'{user_name}.csv', parse_dates=['Date'])

    plt.plot(df['Date'], df['Close'], label='Stock Closing Price')

    plt.xlabel('Date')

    plt.ylabel('Closing Price')
    plt.title(f'{ticker} Closing Price From {month1}/{year1} - {month2}/{year2}')
    plt.legend()
    plt.show()


def add_to_existing_portfolio(user_name, data, ticker):
    file_path = f'{user_name}.csv'

    exist_data = pd.read_csv(file_path)

    data_frame = pd.DataFrame(data, columns=exist_data.columns)
    data_frame['Stock Ticker'] = ticker

    updated = pd.concat([exist_data, data_frame], ignore_index=True)
    updated.to_csv(file_path, index=False)


def main():
    curr_spy_start_date = '2050-01-01'
    curr_spy_end_date = '1800-01-01'

    repeat = True
    add_another = 0

    while repeat:

        user_name, ticker, year1, month1, year2, month2, interval, start_date, end_date = acquire_user_input()
        spy_user_name = f'{user_name}_spy'

        rewrite = False

        if start_date < curr_spy_start_date:
            curr_spy_start_date = start_date
            rewrite = True

        if end_date > curr_spy_end_date:
            curr_spy_end_date = end_date
            rewrite = True

        if rewrite == True:

            spy_data = get_sp500_data(
                interval, curr_spy_start_date, curr_spy_end_date)

            spy_data = pd.DataFrame(spy_data)

            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)

            write_to_csv(spy_user_name, ticker, spy_data)

        exists = check_if_file_exists(user_name)

        if exists:

            clear = input(
                'Would you like to clear your existing portfolio or continue to add to it? (clear/add): ')
            clear = clear.lower()

            while not (clear == 'clear' or clear == 'add'):

                clear = input(
                    'Error: Please enter a valid command: (clear/add): ')
                clear = clear.lower()

            if clear == 'clear':
                clear_csv_file(user_name)

        else:
            fp = create_new_csv_file(user_name)

        stock_data = get_user_choice_stock_info(
            ticker, year1, year2, month1, month2, interval)

        # This creates the dataframe of the pandas object to be able to write it to csv file
        data = pd.DataFrame(stock_data)

        # Display all rows and columns in the pandas object
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)

        if add_another > 0:
            add_to_existing_portfolio(user_name, data, ticker)
        else:

            # This writes the data to a csv file
            write_to_csv(user_name, ticker, data)

            add_ticker_to_csv(ticker, f'{user_name}.csv')

        spy_user_name = f'{user_name}_spy'

        spy_data = get_sp500_data(
            interval, curr_spy_start_date, curr_spy_end_date)

        spy_data = pd.DataFrame(spy_data)

        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)

        write_to_csv(spy_user_name, ticker, spy_data)

        show_plot = input(
            'Would you like to see a visual representation of your chosen stock closing price over time? (y/n): ')

        if show_plot.lower() == 'y':
            show_plot = True
        else:
            show_plot = False
        if show_plot:
            plot_closing_price(user_name, ticker, year1, month1, year2, month2)

        repeat = input(
            'Would you like to add another stock to your portfolio? (y/n): ')

        repeat = repeat.lower()

        if repeat == 'y':
            add_another += 1

            repeat = True
        else:
            repeat = False


main()
