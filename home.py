from flask import Flask
app = Flask(__name__)

from flask import render_template

@app.route('/home/')
@app.route('/home/<name>')

def home(name="Tareq"):
    return render_template('home.html', name=name)
@app.route('/submission/')
def submission():
	return render_template('submission.html')
@app.route('/statistics/')
def statistics():
	return render_template('statistics.html')
@app.route('/datasets/')
def datasets():
	return render_template('datasets.html')
@app.route('/contactus/')
def contactus():
	return render_template('contactus.html')
@app.route('/jsondata/')
def jsondata():
 return render_template('jsondata.html')

if __name__ == "__main__":
  app.run(debug=True)
