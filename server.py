from flask import Flask,render_template, request
from pandas_datareader import data
import datetime
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import CDN
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from support_func.user_height import send_email


app =Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgre1234@localhost/height_collector'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://yezqpyvxnvdntv:9386ee0cf33369ac70b28c873855a56f473d297f539f15e4b520d62f82950d22@ec2-54-83-61-142.compute-1.amazonaws.com:5432/d1roobj6kravp?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False
db = SQLAlchemy(app)

class Data(db.Model):
    __tablename__ = "data"
    id = db.Column(db.Integer, primary_key = True)
    _email = db.Column(db.String(120), unique=True)
    _height = db.Column(db.Integer)

    def __init__(self, email, height):
        self._email =email
        self._height= height

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

@app.route('/user_height', methods=['GET','POST'])
def user_height():
    if request.method == "POST":
        email = request.form["email"]
        height = request.form["height"]
        if not db.session.query(Data).filter(Data._email==email).count():
            data = Data(email,height)
            db.session.add(data)
            db.session.commit()
            warning=""
        else:
            db.session.query(Data).filter(Data._email==email).update({Data._height: height})
            db.session.commit()
            warning ="Entry with the same email was found. The value was updated."

        average = round(db.session.query(func.avg(Data._height)).scalar(),1)
        count = db.session.query(Data._height).count()
        #send_email(email,height, average, count)
        return render_template('user_height.html', average=average, count = count, warning = warning)
    else:
        return render_template('user_height.html')

if __name__=="__main__":
    app.run(debug=True)

