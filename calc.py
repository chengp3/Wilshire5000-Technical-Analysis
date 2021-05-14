import yfinance as yf
from datetime import date, timedelta
import configparser
from write import resource_path


def get_settings(): #settings in config.cfg
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
    #year is a pandas df with daily bar info with open, close, high, low, adjusted close, volume
    #adj close is close adjusted for dividends, splits etc

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


def get_100_companies(symbols):
    today, year_ago = get_year_from_today()
    year_data_all = yf.download(symbols, start=year_ago, end=today) #100 companies year data

    return year_data_all


def SMA(closes,period):
    return closes[-period:].mean()


def cross(beforeSMA50, beforeSMA200, SMA50, SMA200):
    if (beforeSMA50 > beforeSMA200) and (SMA50 > SMA200):
        return "None"
    elif (beforeSMA50 < beforeSMA200) and (SMA50 < SMA200):
        return "None"
    elif (beforeSMA50 < beforeSMA200) and (SMA50 > SMA200):
        return "Golden Cross"
    elif (beforeSMA50 > beforeSMA200) and (SMA50 < SMA200):
        return "Death Cross"
    return "None"

#period is trading days, not actual days
def recent_cross(closes,period=30):
    #for every day in last month, calculate 4 SMAs, run it through cross()
        #start with yesterday, if cross, return cross type, else increment
    i = 0
    while i < period:
        beforeSMA50 = SMA(closes[:-i-1],50)
        beforeSMA200 = SMA(closes[:-i-1],200)
        if i == 0:
            SMA50 = SMA(closes,50)
            SMA200 = SMA(closes,200)    
        else: 
            SMA50 = SMA(closes[:-i],50)
            SMA200 = SMA(closes[:-i],200)
        crosstype = cross(beforeSMA50, beforeSMA200, SMA50, SMA200)
        if crosstype == "None":
            i += 1
        elif crosstype != "None":
            return f'{crosstype} at {str(closes.index[-i])}'
    return "None"

def analyze(adj_closes, closes, vols):
    try:
        closes = closes.dropna()
        adj_closes = adj_closes.dropna()
        vols = vols.dropna()
        cur_price = closes[-1]
        
        SDVAperiod = 14
        #SDVAperiod = get_settings()

        SMA50 = SMA(closes,50) #50 period moving average
        SMA200 = SMA(closes,200) #200 period
        cross = recent_cross(closes,period =30) #looking for golden/death cross

        percentd = (cur_price - SMA50) / SMA50 #yesterday's change
        RSI = compute_RSI(adj_closes, 14)
        SDVA = vols.tail(SDVAperiod).mean() #simple daily volume average
        SDVAd = (vols.iloc[-1] - SDVA) / SDVA #volume change

        return cur_price, SMA50, percentd, SMA200, cross, RSI, SDVA, SDVAd
    except IndexError:
        return -1, -1, -1, -1, -1, -1, -1, -1


def add_indicators(df):

    symbols = list(df.Symbol)
    year_data_all = get_100_companies(symbols)
    
    pricearr = []
    SMA50arr = []
    SMA200arr = []
    percentdarr = []
    crossarr = []
    RSIarr = []
    SDVAarr = []
    SDVAdarr = []
    
    for symbol in symbols:
        adj_closes = year_data_all["Adj Close"][symbol]
        closes = year_data_all["Close"][symbol]
        vols = year_data_all["Volume"][symbol]
        
        cur_price, SMA50, percentd, SMA200, cross, RSI, SDVA, SDVAd = analyze(adj_closes, closes, vols)
        
        pricearr.append(cur_price)
        SMA50arr.append(round(SMA50, 2))
        percentdarr.append(percentd)
        SMA200arr.append(round(SMA200, 2))
        crossarr.append(cross)
        RSIarr.append(round(RSI, 2))
        SDVAarr.append(SDVA)
        SDVAdarr.append(SDVAd)

    df['Current Price'] = pricearr
    df['SMA50'] = SMA50arr
    df['% Change'] = percentdarr
    df['SMA200'] = SMA200arr
    df['Recent Cross'] = crossarr
    df['RSI'] = RSIarr
    df['SDVA'] = SDVAarr
    df['% Vol Change'] = SDVAdarr

    return df
