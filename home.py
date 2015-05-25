from flask import Flask
app = Flask(__name__)

from flask import render_template

@app.route('/home/')
@app.route('/home/<name>')
def home(name="Tareq"):
    return render_template('home.html', name=name)
if __name__ == "__main__":
  app.run(debug=True)
