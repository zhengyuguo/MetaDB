from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Main, Gene, Genotype, Disease, Tissue, Publication, Publication_Author, Publication_Keyword, Inquery, Accession

import random, string
import httplib2
import json
from flask import make_response
import requests
import datetime

app = Flask(__name__)


engine =  create_engine('mysql://root:yulab@localhost:3306/metaDB')  #should change the password to the one you use in your local machine
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/index/')
def home():
	query_gene = session.query(Gene).all()
	#return query_gene[0].Gene
	gene_names = [x.Gene for x in query_gene]
	gene_names = list(set(gene_names))
	gene_names.sort()


	query_disease = session.query(Disease).all()
	disease_names = [x.disease for x in query_disease]
	disease_names = list(set(disease_names))
	disease_names.sort()

	query_tissue = session.query(Tissue).all()
	tissue_names = [x.Tissue for x in query_tissue]
	tissue_names = list(set(tissue_names))
	tissue_names.sort()

	query_main = session.query(Main).all()
	DATAs = []
	for query in query_main:
		data  = {}                           # a dictionary containing data will be transmitted
		title = query.Title 
		ID = query.ArrayExpress
		data["ID"] = ID
		data["title"] = title
		####################### gene queried by ID ##########
		query_gene = session.query(Gene).filter_by(ArrayExpress = ID).all()
		gene = ""
		for g in query_gene:
			gene = gene+ " " + g.Gene
		data["gene"] = title
		####################### Disease queried by ID ##########
		query_disease = session.query(Disease).filter_by(ArrayExpress = ID).all()
		disease = ""
		for g in query_disease:
			disease = disease+ " " + g.disease
		data["disease"] = disease
		####################### tissue queried by ID ##########
		query_tissue = session.query(Tissue).filter_by(ArrayExpress = ID).all()
		tissue = ""
		for g in query_tissue:
			tissue = tissue+ " " + g.Tissue
		data["Tissue"] = tissue
		DATAs.append(data)
	'''
	query_publication = session.query(Publication).all()
	publications = []
	html = ""
	for x in query_publication:
		ID = x.ArrayExpress
		html = html + "<h>" + ID+"</h>"
		query_ID = session.query(Main).filter_by(ArrayExpress = ID).one()
		data = [ x.Title, query_ID.PI, x.Journal, x.Year ]	
		html = html +"<p>"+ x.Title+import datetime" "+query_ID.PI+" "+x.Journal+" " + str(x.Year) + "</p>"	
		publications = publications.append(data)
	'''
	return render_template('home.html',gene_names = gene_names, disease_names = disease_names, tissue_names = tissue_names, DATAs = DATAs, login_session = login_session ) 



@app.route('/submission/',   methods=['GET', 'POST'] )
def submission():
	if request.method == 'GET':
		return render_template('submission.html',login_session = login_session) 
	else:
		inquery = Inquery(ArrayExpress = request.form.get('AccessionID'),
						PubMed = request.form.get('PubMedID'),
						name = request.form.get('YourName'), 
						email = request.form.get('YourEmail'), 
						comments = request.form.get('Comments') )
		print 'You have submitted an inquery successfully. '
		session.add(inquery)
		session.commit()
	#flash('You have submitted an inquery successfully. ')
	return redirect(url_for('home'))



##  show the information of the dataset by accessionID
@app.route('/index/<AccessionID>/')
def datasets(AccessionID):
	dataRow = getAllInfor(AccessionID)
	return render_template('datasets.html',dataRow = dataRow,login_session = login_session) # show complete info in datasets.html

@app.route('/contactus/')
def contactus():
	return render_template('contactus.html',login_session = login_session)

@app.route('/login/', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		print email
		UserPassword = getUserPassword(email)
		if not UserPassword:
			flash("Account: %s doesn't exist." % email)
			return render_template('login.html',login_session = login_session)
		if password == UserPassword:   #check the input email has been used or not
			flash('Wrong email or password: %s' %password)
			return render_template('login.html',login_session = login_session) 
		login_session['email'] = email #record the login
		login_session['login'] = True 
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
		'''
		currentdatetime  = datetime.datetime.utcnow
		fourday=datetime.timedelta(days=4)   
   		expirationdate = currentdatetime +  fourday    
		'''
		name = request.form['firstname'] +" "+request.form['lastname']
		newShop = Accession(name=name,
							randomcode = "111",
							email = email,
							password = password,
							institution = request.form['lastname'], 
							downloadedtimes = 0)
		session.add(newShop)
		flash('New account %s has been successfully created' % email)
		session.commit()
		return redirect(url_for('home'))
	else:
		return render_template('createaccount.html',login_session = login_session)


@app.route('/logout/')
def logout():
	email = login_session['email']
	del login_session['email']
	del login_session['login']
	flash('Account %s has been logged out.' % email)
	return redirect(url_for('home'))


@app.route('/inquiry/')
def inquiry():
	return render_template('inquiry.html',login_session = login_session)


@app.route('/download/')
def download():
	return render_template('download.html',login_session = login_session)
	

@app.route('/statistics/')
def statistics():
	return render_template('statistics.html',login_session = login_session)

# User Helper Functions
def getAllInfor(AccessionID):
    try:
		data = {}
		query = session.query(Main).filter_by(ArrayExpress = AccessionID).one()
		data["ArrayExpress"] = AccessionID
		data['GEO'] = query.GEO
		data['Title']  = query.Title
		data['OtherFactors'] = query.OtherFactors
		data['description'] = query.description
		data['PI'] = query.PI
		data['email'] = query.email
		data['Website'] = query.Website 
		data['GeoArea'] = query.GeoArea
		data['ResearchArea'] = query.ResearchArea

		query = session.query(Gene).filter_by(ArrayExpress = AccessionID).all()
		print "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
		
		data['Gene'] = [ x.Gene for x in query ]
		print len(query)
		data['GeneMGI'] = [ x.GeneMGI for x in query ]

		query = session.query(Genotype).filter_by(ArrayExpress = AccessionID).all()
		data['Genotype'] =  [ x.Genotype for x in query ] 

		query = session.query(Disease).filter_by(ArrayExpress = AccessionID).all()
		data['disease'] = [ x.disease for x in query ] 
		data['diseaseMesh'] =  [ x.diseaseMesh for x in query ]

		query = session.query(Tissue).filter_by(ArrayExpress = AccessionID).all()
		data['Tissue'] = [ x.Tissue for x in query ] 
		data['TissueID'] = [ x.TissueID for x in query ] 

		query = session.query(Publication).filter_by(ArrayExpress = AccessionID).all()
		data['PubMed'] = [ x.PubMed for x in query ] 
		data['Publication'] =  [ x.Title for x in query ] 

		query = session.query(Publication_Author).filter_by(ArrayExpress = AccessionID).all()
		data['Author'] = [ x.Author for x in query ] 
		
		query = session.query(Publication_Keyword).filter_by(ArrayExpress = AccessionID).all()
		data['keyword'] = [ x.keyword for x in query ] 


		return data
    except:
        return None


def getUserPassword(email):
    try:
        user = session.query(Accession).filter_by(email=email).one()
        return user.password
    except:
        return None

if __name__ == '__main__':
	app.secret_key = 'super secret key'
	app.debug = True
	app.run()
