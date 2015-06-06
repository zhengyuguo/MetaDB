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


engine =  create_engine('mysql://root@localhost/metadb')  #should change the password to the one you use in your local machine
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
		html = html +"<p>"+ x.Title+" "+query_ID.PI+" "+x.Journal+" " + str(x.Year) + "</p>"	
		publications = publications.append(data)
	'''
	return render_template('home.html',gene_names = gene_names, disease_names = disease_names, tissue_names = tissue_names, DATAs = DATAs ) 



@app.route('/submission/',   methods=['GET', 'POST'] )
def submission():
	if request.method == 'GET':
		return render_template('submission.html') # inquery.html undefined
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
#@app.route('/index/<AccessionID>/')
#def datasets(AccessionID):
#	dataRow = getAllInfor(AccessionID)
#	return render_template('show.html',dataRow = dataRow) # show.html undefined





@app.route('/statistics/')
def statistics():
	return render_template('statistics.html')
@app.route('/datasets/')
def datasets():
	return render_template('datasets.html')
@app.route('/contactus/')
def contactus():
	return render_template('contactus.html')
@app.route('/login/')
def login():
	return render_template('login.html')
@app.route('/createaccount/')
def createaccount():
	return render_template('createaccount.html')
@app.route('/logout/')
def logout():
	return redirect('/index/')
	


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
		data['Gene'] = [ x['Gene'] for x in query ]
		data['GeneMGI'] = [ x['GeneMGI'] for x in query ]

		query = session.query(Genotype).filter_by(ArrayExpress = AccessionID).all()
		data['Genotype'] =  [ x['Genotype'] for x in query ] 

		query = session.query(Disease).filter_by(ArrayExpress = AccessionID).all()
		data['disease'] = [ x['disease'] for x in query ] 
		data['diseaseMesh'] =  [ x['diseaseMesh'] for x in query ]

		query = session.query(Tissue).filter_by(ArrayExpress = AccessionID).all()
		data['Tissue'] = [ x['Tissue'] for x in query ] 
		data['TissueID'] = [ x['TissueID'] for x in query ] 

		query = session.query(Publication).filter_by(ArrayExpress = AccessionID).all()
		data['PubMed'] = [ x['PubMed'] for x in query ] 
		data['Publication'] =  [ x['Title'] for x in query ] 

		return data
    except:
        return None

def get_All_Items_From(table):
	query = session.query(table).all()


if __name__ == '__main__':
	app.debug = True
	app.run()
