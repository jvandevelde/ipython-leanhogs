import datetime as dt
import random
import io
from flask import Flask, render_template, make_response, jsonify
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import utility as util

#http://noshut.ru/2016/04/building-web-front-end-for-python-scripts-with-flask/
# https://www.codementor.io/znation/3-steps-to-scalable-data-visualization-in-react-js-d3-js-8t7kjxnk5
# https://colindcarroll.com/

app = Flask(__name__)

@app.route("/")
def index():
    d = {}
    year_list = []
    for year in range(1998, dt.datetime.today().year + 1):
        d['id'] = year
        d['display_text'] = str(year)
        year_list.append(d.copy())
    
    return render_template('basic.html', years=year_list)

@app.route("/months/far/<string:near_month_letter>")
def get_far_months(near_month_letter):
    new_far_contracts = util.regularMonthSets[near_month_letter]
    return jsonify(new_far_contracts)

@app.route("/simple.png")
def simple():
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)

    xs = range(100)
    ys = [random.randint(1, 50) for x in xs]

    axis.plot(xs, ys)
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response


if __name__ == '__main__':
    app.run(debug=True)