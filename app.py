# tradingview-ta-demo
# Author: deathlyface
from flask import Flask, request, render_template, jsonify
from tradingview_ta import TA_Handler, Interval
from datetime import timezone
import tradingview_ta, requests, os

app = Flask(__name__)

# Turnstile keys
turnstile_sitekey = os.environ.get("TURNSTILE_SITEKEY")
turnstile_secret = os.environ.get("TURNSTILE_SECRET")

@app.route("/", methods=["GET", "POST"])
def root():
    if request.method == "GET":
        return render_template("index.html", version=tradingview_ta.__version__, sitekey=turnstile_sitekey)
    elif request.method == "POST":
        try:
            # Turnstile
            turnstile_resp = request.form["cf-turnstile-response"]
            validate = requests.post("https://challenges.cloudflare.com/turnstile/v0/siteverify", data={"secret": turnstile_secret, "response": turnstile_resp})
            if validate.json()["success"] == False:
                return render_template("error.html", version=tradingview_ta.__version__, error="Error: Invalid Turnstile token", sitekey=turnstile_sitekey)

            # TradingView Technical Analysis
            handler = TA_Handler()
            handler.set_symbol_as(request.form["symbol"])
            handler.set_exchange_as_crypto_or_stock(request.form["exchange"])
            handler.set_screener_as_stock(request.form["screener"])
            handler.set_interval_as(request.form["interval"])
            analysis = handler.get_analysis()
            return render_template("success.html", 
                    version=tradingview_ta.__version__, 
                    symbol=analysis.symbol, 
                    exchange=analysis.exchange, 
                    screener=analysis.screener, 
                    interval=analysis.interval,
                    time=analysis.time.astimezone(timezone.utc), 
                    summary=analysis.summary,
                    oscillators=analysis.oscillators,
                    moving_averages=analysis.moving_averages,
                    indicators=analysis.indicators,
                    sitekey=turnstile_sitekey)
        except Exception as e:
            return render_template("error.html", version=tradingview_ta.__version__, error=e, sitekey=turnstile_sitekey)
            
if __name__ == '__main__':
	app.run(debug=False, host='0.0.0.0')
