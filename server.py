from flask import Flask,render_template, request
from pandas_datareader import data
import datetime
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import CDN
from flask import request


app =Flask(__name__)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/finance_graph', methods=['GET', 'POST'])
def finance_graph():
    browser = request.user_agent.browser
    if browser=="safari":
        request_str="YY-MM-DD <br>"
    else:
        request_str=""
    if request.method == "POST":
        date = request.form
        date = dict(date)['date'].replace("-", " ").split()
        start = datetime.datetime(int(date[0]),int(date[1]),int(date[2]))
    else:
        start = datetime.datetime(2019, 3, 1)
    end = datetime.datetime.now()
    df = data.DataReader(name="AAPL", data_source="yahoo", start=start, end=end)
    p = figure(x_axis_type='datetime', width=1000, height=300, title="Apple finance chart")
    p.grid.grid_line_alpha = 0.3

    def Inc_Decr(cl, op):
        if cl > op:
            return "Increase"
        elif cl < op:
            return "Decrease"
        else:
            return "Equal"

    df["Status"] = [Inc_Decr(cl, op) for cl, op in zip(df.Close, df.Open)]
    df["Middle"] = (df.Open + df.Close) / 2
    df["Height"] = abs(df.Open - df.Close)
    p.segment(df.index, df.High, df.index, df.Low, color="black")
    p.rect(df.index[df["Status"] == "Increase"], df.Middle[df["Status"] == "Increase"], 12 * 60 * 60 * 1000,
           df.Height[df["Status"] == "Increase"], fill_color="green", line_color="black")
    p.rect(df.index[df["Status"] == "Decrease"], df.Middle[df["Status"] == "Decrease"], 12 * 60 * 60 * 1000,
           df.Height[df["Status"] == "Decrease"], fill_color="red", line_color="black")
    script1, div1 = components(p)
    cdn_js = CDN.js_files[0]
    cdn_css = CDN.css_files[0]
    return render_template("finance_graph.html", script1= script1, div1=div1, cdn_css=cdn_css, cdn_js=cdn_js, request_str=request_str)

if __name__=="__main__":
    app.run(debug=True)

