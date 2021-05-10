import yfinance as yf
from datetime import date, timedelta
import configparser
from write import resource_path


def get_settings():
    parser = configparser.ConfigParser()
    parser.read(resource_path("config.cfg"))

    SDVAperiod = int(parser.get("config", "SDVAperiod"))

    return SDVAperiod


def get_year_from_today():
    today = date.today()
    delta = timedelta(days=365)
    year_ago = today - delta

    return today, year_ago


def get_data_for_year(symbol):
    today, year_ago = get_year_from_today()
    year = yf.download(symbol, start=year_ago, end=today)

    return year


def compute_RSI(df, time_window):
    diff = df.diff(1).dropna()        # diff in one field(one day)

    # this preservers dimensions off diff values
    up_chg = 0 * diff
    down_chg = 0 * diff

    # up change is equal to the positive difference, otherwise equal to zero
    up_chg[diff > 0] = diff[diff > 0]

    # down change is equal to negative difference, otherwise equal to zero
    down_chg[diff < 0] = diff[diff < 0]

    up_chg_avg = up_chg.ewm(com=time_window-1, min_periods=time_window).mean()
    down_chg_avg = down_chg.ewm(com=time_window-1, min_periods=time_window).mean()

    rs = abs(up_chg_avg/down_chg_avg)
    rsi = 100 - 100/(1+rs)

    return rsi.iloc[-1]


def get_indicators(symbol):
    year = get_data_for_year(symbol)
    cur_price = year['Adj Close'][-1]
    data = year["Close"]

    SDVAperiod = get_settings()

    SMA50 = data[-50:].mean()
    SMA200 = data[-200:].mean()
    cross = recent_cross(data, SMA50, SMA200)

    percentd = (cur_price - SMA50) / SMA50 * 100
    RSI = compute_RSI(year["Adj Close"], 14)
    SDVA = year["Volume"].tail(SDVAperiod).mean()
    SDVAd = (year["Volume"].iloc[-1] - SDVA) / SDVA * 100

    return cur_price, SMA50, percentd, SMA200, cross, RSI, SDVA, SDVAd


def sf(number, significant):
    return round(number, significant - len(str(number)))


def recent_cross(data, SMA50, SMA200):
    daybeforeyestSMA50 = data[-51:-1].mean()
    daybeforeyestSMA200 = data[-201:-1].mean()

    if (daybeforeyestSMA50 > daybeforeyestSMA200) and (SMA50 > SMA200):
        return "None"
    elif (daybeforeyestSMA50 < daybeforeyestSMA200) and (SMA50 < SMA200):
        return "None"
    elif (daybeforeyestSMA50 < daybeforeyestSMA200) and (SMA50 > SMA200):
        return "Golden Cross"
    elif (daybeforeyestSMA50 > daybeforeyestSMA200) and (SMA50 < SMA200):
        return "Death Cross"
    return "None"


def add_columns(df):
    pricearr = []
    SMA50arr = []
    SMA200arr = []
    percentdarr = []
    crossarr = []
    RSIarr = []
    SDVAarr = []
    SDVAdarr = []

    for index, row in df.iterrows():
        try:
            symbol = row.Symbol

            cur_price, SMA50, percentd, SMA200, cross, RSI, SDVA, SDVAd = get_indicators(symbol)
            pricearr.append(cur_price)
            SMA50arr.append(round(SMA50, 2))
            percentdarr.append(str(round(percentd, 2))+'%')
            SMA200arr.append(round(SMA200, 2))
            crossarr.append(cross)
            RSIarr.append(round(RSI, 2))
            SDVAarr.append(SDVA)
            SDVAdarr.append(str(round(SDVAd, 2))+'%')

        except IndexError:
            print(f'Error with: {symbol}, might have been delisted')
            pricearr.append(-1)
            SMA50arr.append(-1)
            percentdarr.append(str(-1))
            SMA200arr.append(-1)
            crossarr.append('-1')
            RSIarr.append(-1)
            SDVAarr.append(-1)
            SDVAdarr.append(str(-1))
            continue

    df['Current Price'] = pricearr
    df['SMA50'] = SMA50arr
    df['% Change'] = percentdarr
    df['SMA200'] = SMA200arr
    df['Recent Cross'] = crossarr
    df['RSI'] = RSIarr
    df['SDVA'] = SDVAarr
    df['% Vol Change'] = SDVAdarr

    return df
