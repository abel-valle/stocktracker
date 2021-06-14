from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def main():
    return render_template('index.html')


@app.route("/userview")
def user_view():
    return render_template('userview.html')

@app.route("/selectstock")
def select_stock():
    return render_template('selectstock.html')


if __name__ == "__main__":
    app.run(debug=True)
