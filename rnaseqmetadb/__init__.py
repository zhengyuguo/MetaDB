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
from exception import *

@app.route('/experiments/')
@app.route('/')
def home():
	gene_names = get_distinct_gene()
	disease_names = get_distinct_disease()
	tissue_names = get_distinct_tissue()
	summary_table = get_summary_info_for_each_entry()
	constraints = {}

	genename = request.args.get("genename")
	diseasename = request.args.get("diseasename")
	tissuetype = request.args.get("tissuetype")

	if genename and genename != "":
		constraints["Gene"] = genename
	if diseasename and diseasename != "":
		constraints["Disease"] = diseasename
	if tissuetype and tissuetype != "":
		constraints["Tissue"] = tissuetype

	acc = getAccByConstraints(constraints)

	keyword = request.args.get("keyword")
	if keyword:
		 acc.intersection_update(set(getAccessionID(keyword)))
		 
	res = [entry for entry in summary_table if entry['ID'] in acc]
	return render_template('home.html',gene_names = gene_names, disease_names = disease_names, tissue_names = tissue_names, DATAs = res, login_session = login_session ) 

@app.route('/experiments/<AccessionID>/')
def datasets(AccessionID):
	try:
		data = getAllInfor(AccessionID)
	except:
		return render_template('404.html',accession = AccessionID,login_session = login_session)
	else:
		return render_template('datasets.html',data = data,login_session = login_session) # show complete info in datasets.html

@app.route('/statistics/')
def statistics():
	statistics =getStatistics()
	
	if statistics is None:
		return render_template('404.html',accession = 'Statistics',login_session = login_session)
	else:
		schemaJournal= [('Journal','string'), ('Publications', 'number')] #in list form
		data=sorted(statistics["journal"].items(),key=lambda vec: vec[1],reverse=True)

		data_table = gviz_api.DataTable(schemaJournal)
		data_table.LoadData(data)
		jsonJournalData = data_table.ToJSon()

		schemaGeo= [('GeoLoation','string'), ('Publications', 'number')] #in list form
		data=sorted(statistics["geoArea"].items(),key=lambda vec: vec[1],reverse=True)
		data_table = gviz_api.DataTable(schemaGeo)
		data_table.LoadData(data)
		jsonGeolData = data_table.ToJSon()

		schemaYear= [('Year','string'), ('Publications', 'number')] #in list form
		data=sorted(statistics["year"].items(),key=lambda vec: vec[1],reverse=True)
		data_table = gviz_api.DataTable(schemaYear)
		data_table.LoadData(data)
		jsonYearData = data_table.ToJSon()

		return render_template('statistics.html', statGeo = jsonGeolData,statJournal = jsonJournalData, statYear = jsonYearData, login_session = login_session)

@app.route('/createaccount/', methods=['GET', 'POST'])
def createaccount():
	if request.method == 'POST':
		email = request.form['YourEmail']
		password = request.form['pwd']
		name = request.form['firstname'] +" "+request.form['lastname']
		institution = request.form['institution']
		try:
			status = createUser(name, email, password,institution)
		except (UserCreate_SHORT, UserCreate_LONG, UserCreate_NOINST, UserCreate_NONAME, UserCreate_REPEMAIL) as e:
			flash(e.msg)
			return render_template('createaccount.html',login_session = login_session) 
		except:
			flash('Unknown Error Occured. Please try again or contact the administrator')
			return render_template('createaccount.html',login_session = login_session) 
		else:
			flash('New account %s has been successfully created. Please login.' % email)
			return redirect(url_for('login'))
	else:
		return render_template('createaccount.html',login_session = login_session)

@app.route('/contactus/')
def contactus():
	return render_template('contactus.html',login_session = login_session)

@app.route('/login/', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		try:
			checkUserPassword(email,password)
		except (Login_NOUSER,Login_WRONGPW) as e:
			flash(e.msg)
			return render_template('login.html',login_session = login_session)
		except Login_NOTVERIFIED as e:
			flash(e.msg)
			return render_template('login.html',login_session = login_session)
		except:
			flash("Internal Error. Please try again or contact the administrator.")
			return render_template('login.html',login_session = login_session)
		else: 
			login_session['email'] = email #record the login
			login_session['login'] = True 
			local_session = db_session()
			user = local_session.query(User).filter_by(email=email).one()
			login_session['user'] = user.name
			login_session['ismanager'] = user.ismanager
			local_session.close()
			return redirect(url_for('home'))
	else:
		return render_template('login.html',login_session = login_session)

@app.route('/verify/')
def verifyemail():
	email = request.args.get("email")
	randomcode = request.args.get("randomcode")
	try:
		verifyUserEmail(email,randomcode)
	except (VerifyEmail_NOUSER,VerifyEmail_FAILDED) as e:
		return render_template('404.html',accession = "The requested page" ,login_session = login_session)
	except VerifyEmail_EXPIRED:
		return redirect(url_for('login'))
	else:
		flash('Account %s has been verified.' % email)
		return redirect(url_for('login'))

@app.route('/submission/',   methods=['GET', 'POST'] )
def submission():
	if request.method == 'GET':
		return render_template('submission.html',login_session = login_session) 
	else:
		ArrayExpress = str(request.form.get('AccessionID')).strip()
		PubMed = str(request.form.get('PubMedID')).strip()
		name = str(request.form.get('YourName')).strip()
		email = str(request.form.get('YourEmail')).strip()
		comments = str(request.form.get('Comments')).strip()
		if ArrayExpress == "":
			flash('AccessionID can not be empty.')
		elif PubMedID == "":
			flash('PubMedID can not be empty.')
		elif name == "":
			flash('Name can not be empty.')
		elif email == "":
			flash('E-mail, can not be empty.')
		else:
			try:
				saveToInquiry(ArrayExpress, PubMed, name, email, comments)
			except:
				flash('Submission failed. Please try again or contact the administrator.')
			else:
				flash('You have submitted an inquiry successfully. ')
		return redirect(url_for('submission'))

@app.route('/logout/')
def logout():
	del login_session['email']
	del login_session['login']
	del login_session['user']
	del login_session['ismanager']
	flash('Account has been logged out.' )
	return redirect(url_for('home'))

@app.route('/download/', methods=['GET', 'POST'])
def download():
	if request.method == 'GET' or login_session.get('login') is None:
		return render_template('download.html',login_session = login_session)
	else:
		file_name = './test.txt' 
		return send_file(file_name, as_attachment=True)

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


@app.route('/publication/')
def publication():
	return render_template('publication.html',login_session = login_session)
	
if __name__ == '__main__':
	app.secret_key = 'super secret key'
	app.debug = True
	app.run(host = 'localhost', port = 5000)
