# vim: set noexpandtab tabstop=2:
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, send_file
from flask import session as login_session

from webSearch import *
from database_helper import *
import httplib2
import json
from flask import make_response
import requests
import datetime
import gviz_api

app = Flask(__name__)


from email_helper import *

@app.route('/')
def home():
	(gene_names, disease_names, tissue_names, DATAs) = getAllData()
	constraints = {}

	genename = request.args.get("genename")
	if genename and genename != "":
		constraints["Gene"] = genename
	diseasename = request.args.get("diseasename")
	if diseasename and diseasename != "":
		constraints["Disease"] = diseasename
	tissuetype = request.args.get("tissuetype")
	if tissuetype and tissuetype != "":
		constraints["Tissue"] = tissuetype

	acc = getAccByConstraints(constraints)
	keyword = request.args.get("keyword")
	if keyword:
		 acc.intersection_update(set(getAccessionID(keyword)))
		 
	DATAs = [entry for entry in DATAs if entry['ID'] in acc]
	return render_template('home.html',gene_names = gene_names, disease_names = disease_names, tissue_names = tissue_names, DATAs = DATAs, login_session = login_session ) 

@app.route('/submission/',   methods=['GET', 'POST'] )
def submission():
	if request.method == 'GET':
		return render_template('submission.html',login_session = login_session) 
	else:
		ArrayExpress = str(request.form.get('AccessionID'))
		PubMed = str(request.form.get('PubMedID'))
		name = str(request.form.get('YourName'))
		email = str(request.form.get('YourEmail'))
		comments = str(request.form.get('Comments'))
		status = saveToInquiry(ArrayExpress, PubMed, name, email, comments)
		if status == 1:
			flash('AccessionID can not be empty. ')
		elif status == 2:
			flash('Name can not be empty. ')
		elif status == 3:
			flash('Email can not be empty. ')
		elif status == 4:
			flash('Sorry, some error happened. ')
		else:
			flash('You have submitted an inquiry successfully. ')
			return redirect(url_for('home'))
		return redirect(url_for('submission'))



##  show the information of the dataset by accessionID
@app.route('/<AccessionID>/')
def datasets(AccessionID):
	dataRow = getAllInfor(AccessionID)
	if not dataRow:
		flash("The data doesn't exist.")
		return redirect(url_for('home'))
	return render_template('datasets.html',dataRow = dataRow,login_session = login_session) # show complete info in datasets.html

@app.route('/contactus/')
def contactus():
	return render_template('contactus.html',login_session = login_session)

@app.route('/login/', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		status = checkUserPassword(email,password)
		if status == 2:
			flash("Account: %s has not been verified. A verification email has been sent to you." % email)
			send_verification_email(email)
			return render_template('login.html',login_session = login_session)
		if status == -1:
			flash("Account: %s doesn't exist." % email)
			return render_template('login.html',login_session = login_session)
		if status == 0:   
			flash('Wrong email or password.')
			return render_template('login.html',login_session = login_session) 
		login_session['email'] = email #record the login
		login_session['login'] = True 
		user = session.query(User).filter_by(email=email).one()
		login_session['user'] = user.name
		login_session['ismanager'] = user.ismanager
		return redirect(url_for('home'))
	else:
		return render_template('login.html',login_session = login_session)

@app.route('/createaccount/', methods=['GET', 'POST'])
def createaccount():
	if request.method == 'POST':
		email = request.form['YourEmail']
		password = request.form['pwd']
		name = request.form['firstname'] +" "+request.form['lastname']
		institution = request.form['institution']
		status = createUser(name, email, password,institution)
		if status == 5:
			flash('New account %s has been successfully created. Please login.' % email)
			return redirect(url_for('login'))
		if status == -1:   #check the input email has been used or not
			flash('Email: %s has been used' % email)
			return render_template('createaccount.html',login_session = login_session) 
		if status == 0:
			flash('The length of password should contain at least 6 characters.')
			return render_template('createaccount.html',login_session = login_session) 
		if status == 1:
			flash('The length of password should contain at most 15 characters.')
			return render_template('createaccount.html',login_session = login_session)
		if status == 2:
			flash('Name is not provided.')
			return render_template('createaccount.html',login_session = login_session)
		if status == 3:
			flash('Institution is not provided.')
			return render_template('createaccount.html',login_session = login_session)
		flash('Something wrong happened.')
		return render_template('createaccount.html',login_session = login_session)
	else:
		return render_template('createaccount.html',login_session = login_session)


@app.route('/logout/')
def logout():
	email = login_session['email']
	del login_session['email']
	del login_session['login']
	del login_session['user']
	del login_session['ismanager']
	flash('Account %s has been logged out.' % email)
	return redirect(url_for('home'))


@app.route('/verify/')
def verifyemail():
	email = request.args.get("email")
	randomcode = request.args.get("randomcode")
	status = verifyUserEmail(email,randomcode)
	if status is 1 or status is 2:
		flash('Account %s has been verified. Please login.' % email)
		return redirect(url_for('login'))
	if status is 0:
		flash('Account %s has not been verified.' % email)
		return redirect(url_for('login'))
	flash("Account %s doesn't exist." % email)
	return redirect(url_for('createaccount'))

@app.route('/inquiry/', methods=['GET', 'POST'])
def inquiry():
	dataRow = getAllInquiry()
	if request.method == 'POST':
		for data in dataRow:
			ID = data.id
			status = request.form[str(ID)]
			if status == "Delete This Item":
				deleteInquiry(ID)
				dataRow.remove(data)
			elif status != "No Change" and status != data.status:
				changeInquiryStatus(ID, status)
	return render_template('inquiry.html', dataRow = dataRow, login_session = login_session)


@app.route('/download/', methods=['GET', 'POST'])
def download():
	if request.method == 'GET' or login_session.get('login') is None:
		return render_template('download.html',login_session = login_session)
	else:
		print "xxxxxxxxxxxxxxxxx"
		file_name = './download/test.txt' 
		return send_file(file_name, as_attachment=True)
		


@app.route('/statistics/')
def statistics():
	statistics =(getStatistics())

	schemaJournal= [('Journal','string'), ('Publications', 'number')] #in list form
	#data must be in list form
	data= statistics["journal"].items()
	 # Loading it into gviz_api.DataTable
	data_table = gviz_api.DataTable(schemaJournal)
	data_table.LoadData(data)
	jsonJournalData = data_table.ToJSon()

	schemaGeo= [('GeoLoation','string'), ('Publications', 'number')] #in list form
	#data must be in list form
	data= statistics["geoArea"].items()
	 # Loading it into gviz_api.DataTable
	data_table = gviz_api.DataTable(schemaGeo)
	data_table.LoadData(data)
	jsonGeolData = data_table.ToJSon()

	schemaYear= [('Year','string'), ('Publications', 'number')] #in list form
	#data must be in list form
	data= statistics["year"].items()
	 # Loading it into gviz_api.DataTable
	data_table = gviz_api.DataTable(schemaYear)
	data_table.LoadData(data)
	jsonYearData = data_table.ToJSon()

	return render_template('statistics.html', statGeo = jsonGeolData,statJournal = jsonJournalData, statYear = jsonYearData, login_session = login_session)


if __name__ == '__main__':
	app.secret_key = 'super secret key'
	app.debug = True
	app.run(host = 'localhost', port = 5000)
