# tradingview-ta-demo
# Author: deathlyface
from flask import Flask, request, render_template, jsonify
from tradingview_ta import TA_Handler, Interval
from datetime import timezone
import tradingview_ta, requests, os

app = Flask(__name__)

# Load hCaptcha sitekey & secret from environmental variables
hcaptcha_sitekey = os.environ.get("h-captcha-sitekey")
hcaptcha_secret = os.environ.get("h-captcha-secret")

@app.route("/", methods=["GET", "POST"])
def root():
    if request.method == "GET":
        return render_template("index.html", version=tradingview_ta.__version__, captcha_sitekey=hcaptcha_sitekey)
    elif request.method == "POST":
        try:
            # hCaptcha
            hcaptcha_response = request.form["h-captcha-response"]
            captchaReq = requests.post("https://hcaptcha.com/siteverify", data={"secret": hcaptcha_secret, "response": hcaptcha_response})
            if captchaReq.json()["success"] == False:
                return render_template("error.html", version=tradingview_ta.__version__, error="Error: Invalid captcha", captcha_sitekey=hcaptcha_sitekey)

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
                    captcha_sitekey=hcaptcha_sitekey)
        except Exception as e:
            return render_template("error.html", version=tradingview_ta.__version__, error=e, captcha_sitekey=hcaptcha_sitekey)