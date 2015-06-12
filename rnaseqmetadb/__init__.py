from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Main, Gene, Genotype, Disease, Tissue, Publication, Publication_Author, Publication_Keyword, Inquery, Accession
from webSearch import *
from database_helper import *
import random, string
import httplib2
import json
from flask import make_response
import requests
import datetime

app = Flask(__name__)


@app.route('/')
@app.route('/index/')
def home():
	keyword = request.args.get("keyword")
	[gene_names, disease_names, tissue_names, DATAs] = getAllData()
	if keyword:
		AccessionIDS = getAccessionID(keyword)
		DATAs = getInforByID(AccessionIDS)
	return render_template('home.html',gene_names = gene_names, disease_names = disease_names, tissue_names = tissue_names, DATAs = DATAs, login_session = login_session ) 




@app.route('/submission/',   methods=['GET', 'POST'] )
def submission():
	if request.method == 'GET':
		return render_template('submission.html',login_session = login_session) 
	else:
		ArrayExpress = request.form.get('AccessionID')
		PubMed = request.form.get('PubMedID')
		name = request.form.get('YourName')
		email = request.form.get('YourEmail')
		comments = request.form.get('Comments')
		saveToInquery(ArrayExpress, PubMed, name, email, comments)
	flash('You have submitted an inquery successfully. ')
	return redirect(url_for('home'))



##  show the information of the dataset by accessionID
@app.route('/index/<AccessionID>/')
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
		UserPassword = getUserPassword(email)
		if not UserPassword:
			flash("Account: %s doesn't exist." % email)
			return render_template('login.html',login_session = login_session)
		if password != UserPassword:   #check the input email has been used or not
			flash('Wrong email or password.')
			return render_template('login.html',login_session = login_session) 
		login_session['email'] = email #record the login
		login_session['login'] = True 
		user = session.query(Accession).filter_by(email=email).one()
		login_session['user'] = user.name
		return redirect(url_for('home'))
	else:
		return render_template('login.html',login_session = login_session)

@app.route('/createaccount/', methods=['GET', 'POST'])
def createaccount():
	'''Do not verify the input data'''
	if request.method == 'POST':
		email = request.form['YourEmail']
		password = request.form['pwd']
		account = session.query(Accession).filter_by(email=email).all()
		if len(account) != 0:   #check the input email has been used or not
			flash('Email: %s has been used' % email)
			return render_template('createaccount.html',login_session = login_session) 
		if len(password) < 6:
			flash('The length of password should contain at least 6 characters.')
			return render_template('createaccount.html',login_session = login_session) 
		if len(password) > 15:
			flash('The length of password should contain at most 15 characters.')
			return render_template('createaccount.html',login_session = login_session) 
		name = request.form['firstname'] +" "+request.form['lastname']
		institution = request.form['institution']
		saveToAccession(name, email, password,institution)
		flash('New account %s has been successfully created' % email)
		return redirect(url_for('home'))
	else:
		return render_template('createaccount.html',login_session = login_session)


@app.route('/logout/')
def logout():
	email = login_session['email']
	del login_session['email']
	del login_session['login']
	del login_session['user']
	flash('Account %s has been logged out.' % email)
	return redirect(url_for('home'))


@app.route('/inquiry/')
def inquiry():
	dataRow = getAllInquery()
	return render_template('inquiry.html', dataRow = dataRow, login_session = login_session)


@app.route('/download/')
def download():
	return render_template('download.html',login_session = login_session)
	

@app.route('/statistics/')
def statistics():
	statistics = jsonify(getStatistics())
	#return statistics
	return render_template('statistics.html',statistics = statistics,login_session = login_session)





if __name__ == '__main__':
	app.secret_key = 'super secret key'
	app.debug = True
	app.run(host = 'localhost', port = 5000)
