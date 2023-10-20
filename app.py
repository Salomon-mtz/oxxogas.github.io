from flask import Flask, render_template

app = Flask(__name__)
app.static_folder = 'static'
app.debug = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compra')
def compra():
    return render_template('compra.html')

if __name__ == '__main__':
    app.run()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compra')
def compra():
    return render_template('compra.html')

if __name__ == '__main__':
    app.run()
