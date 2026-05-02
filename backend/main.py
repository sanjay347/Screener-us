from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import numpy as np
import json
from typing import Optional

app = FastAPI(title="US Stock Screener API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def clean(val):
    if val is None:
        return None
    if isinstance(val, float) and (np.isnan(val) or np.isinf(val)):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    return val

def df_to_records(df: pd.DataFrame):
    if df is None or df.empty:
        return {}
    df = df.copy()
    df.columns = [str(c).split(" 00:00:00")[0] for c in df.columns]
    df.index = [str(i) for i in df.index]
    result = {}
    for col in df.columns:
        result[col] = {}
        for idx in df.index:
            result[col][idx] = clean(df.loc[idx, col])
    return result

US_EXCHANGES = {"NYQ", "NMS", "NGM", "NCM", "PCX", "ASE", "NYB", "CBT", "CME", "NYM", "OBB", "PNK"}

@app.get("/api/search")
def search_stocks(q: str = Query(..., min_length=1)):
    try:
        search_results = yf.Search(q.strip(), max_results=12)
        quotes = search_results.quotes if hasattr(search_results, 'quotes') else []

        # Prefer US equities, filter out options/futures/funds unless no equity found
        us_equities = [r for r in quotes if r.get("quoteType") == "EQUITY" and r.get("exchange") in US_EXCHANGES]
        all_equities = [r for r in quotes if r.get("quoteType") == "EQUITY"]
        candidates = us_equities if us_equities else all_equities if all_equities else quotes

        results = []
        for r in candidates[:8]:
            results.append({
                "symbol": r.get("symbol", ""),
                "name": r.get("longname") or r.get("shortname", ""),
                "exchange": r.get("exchDisp") or r.get("exchange", ""),
                "sector": r.get("sectorDisp") or r.get("sector", ""),
                "industry": r.get("industryDisp") or r.get("industry", ""),
                "type": r.get("typeDisp") or r.get("quoteType", ""),
            })
        return {"results": results}
    except Exception as e:
        return {"results": [], "error": str(e)}

@app.get("/api/stock/{ticker}/info")
def get_stock_info(ticker: str):
    try:
        t = yf.Ticker(ticker.upper())
        info = t.info
        if not info or not info.get("symbol"):
            raise HTTPException(status_code=404, detail="Stock not found")

        # Fast facts panel (like screener.in top table)
        facts = {
            "symbol": info.get("symbol"),
            "name": info.get("longName") or info.get("shortName"),
            "exchange": info.get("exchange"),
            "currency": info.get("currency", "USD"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "website": info.get("website"),
            "country": info.get("country"),
            "fullTimeEmployees": clean(info.get("fullTimeEmployees")),
            "longBusinessSummary": info.get("longBusinessSummary"),
            # Price info
            "currentPrice": clean(info.get("currentPrice") or info.get("regularMarketPrice")),
            "previousClose": clean(info.get("previousClose") or info.get("regularMarketPreviousClose")),
            "open": clean(info.get("open") or info.get("regularMarketOpen")),
            "dayHigh": clean(info.get("dayHigh") or info.get("regularMarketDayHigh")),
            "dayLow": clean(info.get("dayLow") or info.get("regularMarketDayLow")),
            "fiftyTwoWeekHigh": clean(info.get("fiftyTwoWeekHigh")),
            "fiftyTwoWeekLow": clean(info.get("fiftyTwoWeekLow")),
            "volume": clean(info.get("volume") or info.get("regularMarketVolume")),
            "averageVolume": clean(info.get("averageVolume")),
            # Valuation
            "marketCap": clean(info.get("marketCap")),
            "enterpriseValue": clean(info.get("enterpriseValue")),
            "trailingPE": clean(info.get("trailingPE")),
            "forwardPE": clean(info.get("forwardPE")),
            "pegRatio": clean(info.get("pegRatio")),
            "priceToBook": clean(info.get("priceToBook")),
            "priceToSalesTrailing12Months": clean(info.get("priceToSalesTrailing12Months")),
            "enterpriseToRevenue": clean(info.get("enterpriseToRevenue")),
            "enterpriseToEbitda": clean(info.get("enterpriseToEbitda")),
            # Profitability
            "profitMargins": clean(info.get("profitMargins")),
            "grossMargins": clean(info.get("grossMargins")),
            "operatingMargins": clean(info.get("operatingMargins")),
            "ebitdaMargins": clean(info.get("ebitdaMargins")),
            "returnOnAssets": clean(info.get("returnOnAssets")),
            "returnOnEquity": clean(info.get("returnOnEquity")),
            # Financial data
            "totalRevenue": clean(info.get("totalRevenue")),
            "revenueGrowth": clean(info.get("revenueGrowth")),
            "revenuePerShare": clean(info.get("revenuePerShare")),
            "grossProfits": clean(info.get("grossProfits")),
            "ebitda": clean(info.get("ebitda")),
            "netIncomeToCommon": clean(info.get("netIncomeToCommon")),
            "earningsGrowth": clean(info.get("earningsGrowth")),
            "earningsQuarterlyGrowth": clean(info.get("earningsQuarterlyGrowth")),
            "trailingEps": clean(info.get("trailingEps")),
            "forwardEps": clean(info.get("forwardEps")),
            # Balance sheet
            "totalCash": clean(info.get("totalCash")),
            "totalCashPerShare": clean(info.get("totalCashPerShare")),
            "totalDebt": clean(info.get("totalDebt")),
            "debtToEquity": clean(info.get("debtToEquity")),
            "currentRatio": clean(info.get("currentRatio")),
            "quickRatio": clean(info.get("quickRatio")),
            "bookValue": clean(info.get("bookValue")),
            # Cash flow
            "freeCashflow": clean(info.get("freeCashflow")),
            "operatingCashflow": clean(info.get("operatingCashflow")),
            # Dividends
            "dividendRate": clean(info.get("dividendRate")),
            "dividendYield": clean(info.get("dividendYield")),
            "exDividendDate": str(info.get("exDividendDate")) if info.get("exDividendDate") else None,
            "payoutRatio": clean(info.get("payoutRatio")),
            "fiveYearAvgDividendYield": clean(info.get("fiveYearAvgDividendYield")),
            # Shares
            "sharesOutstanding": clean(info.get("sharesOutstanding")),
            "floatShares": clean(info.get("floatShares")),
            "sharesShort": clean(info.get("sharesShort")),
            "shortRatio": clean(info.get("shortRatio")),
            "shortPercentOfFloat": clean(info.get("shortPercentOfFloat")),
            "heldPercentInsiders": clean(info.get("heldPercentInsiders")),
            "heldPercentInstitutions": clean(info.get("heldPercentInstitutions")),
            # Moving averages
            "fiftyDayAverage": clean(info.get("fiftyDayAverage")),
            "twoHundredDayAverage": clean(info.get("twoHundredDayAverage")),
            # Returns
            "52WeekChange": clean(info.get("52WeekChange")),
            "SandP52WeekChange": clean(info.get("SandP52WeekChange")),
            # Analyst
            "targetHighPrice": clean(info.get("targetHighPrice")),
            "targetLowPrice": clean(info.get("targetLowPrice")),
            "targetMeanPrice": clean(info.get("targetMeanPrice")),
            "targetMedianPrice": clean(info.get("targetMedianPrice")),
            "recommendationMean": clean(info.get("recommendationMean")),
            "recommendationKey": info.get("recommendationKey"),
            "numberOfAnalystOpinions": clean(info.get("numberOfAnalystOpinions")),
            # Beta
            "beta": clean(info.get("beta")),
        }
        return facts
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock/{ticker}/history")
def get_history(ticker: str, period: str = "1y", interval: str = "1d"):
    try:
        t = yf.Ticker(ticker.upper())
        hist = t.history(period=period, interval=interval)
        if hist.empty:
            return {"data": []}
        hist = hist.reset_index()
        records = []
        for _, row in hist.iterrows():
            records.append({
                "date": str(row["Date"]).split(" ")[0],
                "open": clean(row.get("Open")),
                "high": clean(row.get("High")),
                "low": clean(row.get("Low")),
                "close": clean(row.get("Close")),
                "volume": clean(row.get("Volume")),
            })
        return {"data": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock/{ticker}/financials")
def get_financials(ticker: str):
    try:
        t = yf.Ticker(ticker.upper())
        return {
            "annual": {
                "income_stmt": df_to_records(t.income_stmt),
                "balance_sheet": df_to_records(t.balance_sheet),
                "cashflow": df_to_records(t.cashflow),
            },
            "quarterly": {
                "income_stmt": df_to_records(t.quarterly_income_stmt),
                "balance_sheet": df_to_records(t.quarterly_balance_sheet),
                "cashflow": df_to_records(t.quarterly_cashflow),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock/{ticker}/holders")
def get_holders(ticker: str):
    try:
        t = yf.Ticker(ticker.upper())

        major = None
        institutional = None
        mutualfund = None
        insider = None

        try:
            mh = t.major_holders
            if mh is not None and not mh.empty:
                major = mh.to_dict()
        except:
            pass

        try:
            ih = t.institutional_holders
            if ih is not None and not ih.empty:
                ih = ih.copy()
                ih.columns = [str(c) for c in ih.columns]
                if "Date Reported" in ih.columns:
                    ih["Date Reported"] = ih["Date Reported"].astype(str)
                institutional = ih.head(20).to_dict(orient="records")
        except:
            pass

        try:
            mf = t.mutualfund_holders
            if mf is not None and not mf.empty:
                mf = mf.copy()
                mf.columns = [str(c) for c in mf.columns]
                if "Date Reported" in mf.columns:
                    mf["Date Reported"] = mf["Date Reported"].astype(str)
                mutualfund = mf.head(20).to_dict(orient="records")
        except:
            pass

        try:
            it = t.insider_transactions
            if it is not None and not it.empty:
                it = it.copy()
                it.columns = [str(c) for c in it.columns]
                for col in it.select_dtypes(include=["datetime64"]).columns:
                    it[col] = it[col].astype(str)
                insider = it.head(20).to_dict(orient="records")
        except:
            pass

        return {
            "major": major,
            "institutional": institutional,
            "mutualfund": mutualfund,
            "insider": insider,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock/{ticker}/dividends")
def get_dividends(ticker: str):
    try:
        t = yf.Ticker(ticker.upper())
        div = t.dividends
        splits = t.splits
        result_div = []
        result_splits = []
        if div is not None and not div.empty:
            div = div.reset_index()
            for _, row in div.iterrows():
                result_div.append({
                    "date": str(row["Date"]).split(" ")[0],
                    "dividend": clean(row["Dividends"]),
                })
        if splits is not None and not splits.empty:
            splits = splits.reset_index()
            for _, row in splits.iterrows():
                result_splits.append({
                    "date": str(row["Date"]).split(" ")[0],
                    "ratio": clean(row["Stock Splits"]),
                })
        return {"dividends": result_div[-20:], "splits": result_splits}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock/{ticker}/recommendations")
def get_recommendations(ticker: str):
    try:
        t = yf.Ticker(ticker.upper())
        rec = t.recommendations
        upgrades = t.upgrades_downgrades
        result_rec = []
        result_upgrades = []
        if rec is not None and not rec.empty:
            rec = rec.reset_index()
            for _, row in rec.iterrows():
                result_rec.append({
                    "period": str(row.get("period", "")),
                    "strongBuy": clean(row.get("strongBuy")),
                    "buy": clean(row.get("buy")),
                    "hold": clean(row.get("hold")),
                    "sell": clean(row.get("sell")),
                    "strongSell": clean(row.get("strongSell")),
                })
        if upgrades is not None and not upgrades.empty:
            upgrades = upgrades.reset_index()
            for col in upgrades.select_dtypes(include=["datetime64"]).columns:
                upgrades[col] = upgrades[col].astype(str)
            result_upgrades = upgrades.head(20).to_dict(orient="records")
        return {"recommendations": result_rec, "upgrades_downgrades": result_upgrades}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock/{ticker}/news")
def get_news(ticker: str):
    try:
        t = yf.Ticker(ticker.upper())
        news = t.news or []
        result = []
        for item in news[:15]:
            result.append({
                "title": item.get("content", {}).get("title", ""),
                "url": item.get("content", {}).get("canonicalUrl", {}).get("url", ""),
                "publisher": item.get("content", {}).get("provider", {}).get("displayName", ""),
                "publishedAt": item.get("content", {}).get("pubDate", ""),
                "summary": item.get("content", {}).get("summary", ""),
            })
        return {"news": result}
    except Exception as e:
        return {"news": [], "error": str(e)}

@app.get("/api/stock/{ticker}/calendar")
def get_calendar(ticker: str):
    try:
        t = yf.Ticker(ticker.upper())
        cal = t.calendar
        result = {}
        if cal:
            for k, v in cal.items():
                if isinstance(v, (pd.Timestamp,)):
                    result[k] = str(v)
                else:
                    result[k] = clean(v)
        return result
    except Exception as e:
        return {}

@app.get("/api/stock/{ticker}/earnings")
def get_earnings(ticker: str):
    try:
        t = yf.Ticker(ticker.upper())

        hist_earnings = []
        try:
            eh = t.earnings_history
            if eh is not None and not eh.empty:
                eh = eh.reset_index()
                for _, row in eh.iterrows():
                    d = {}
                    for col in eh.columns:
                        val = row[col]
                        if isinstance(val, (pd.Timestamp,)):
                            d[str(col)] = str(val).split(" ")[0]
                        else:
                            d[str(col)] = clean(val)
                    hist_earnings.append(d)
        except:
            pass

        return {"earnings_history": hist_earnings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock/{ticker}/options")
def get_options(ticker: str):
    try:
        t = yf.Ticker(ticker.upper())
        dates = t.options
        return {"expiration_dates": list(dates) if dates else []}
    except Exception as e:
        return {"expiration_dates": [], "error": str(e)}

@app.get("/health")
def health():
    return {"status": "ok"}
