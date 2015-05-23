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


engine =  create_engine('mysql://root:yulab@localhost:3306/rnaseqmetadb')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/index/')
def showMainPage():
	query_gene = session.query(Gene).all()
	genes = [x.Gene for x in query_gene]
	query_disease = session.query(Disease).all()
	diseases = [x.disease for x in query_disease]
	query_main = session.query(Main).all()
	accessionIDs = [x.ArrayExpress for x in query_main]
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
	#return render_template('main.html',dataForSearch = [genes,diseases,accessionIDs], publications = publications) #main.html undefined
	
	return html



@app.route('/index/<AccessionID>/')
def showDetail(AccessionID):
	dataRow = getAllInfor(AccessionID)
	return render_template('show.html',dataRow = dataRow) # show.html undefined


@app.route('/index/submit/',   methods=['GET', 'POST'] )
def submit():
	if request.method == 'GET':
		return render_template('submit.html') # submit.html undefined
	else:
		randomcode = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
		dateTimeNow = datetime.datetime.now()
		expirationdate = dateTimeNow + datetime.timedelta(days =7)  ###random code is valid in 7 days
		accession1 = Accession(
    			name = request.args.get('state'),
   				email = request.args.get('email'),
				institution = request.args.get('institution'),
				expirationdate = expirationdate,   ######date should be modified##############
				randomcode = randomcode,
				downloadedtimes = 0)
		session.add(accession1)
		session.commit()
	######################## mailer here  #######
	flash('Please ckeck your email to get the downloading link.')
	return redirect(url_for('showMainPage'))


@app.route('/index/inquery/',   methods=['GET', 'POST'] )
def inquery():
	if request.method == 'GET':
		return render_template('inquery.html') # inquery.html undefined
	else:
		inquery = Inquery(
    			ArrayExpress = request.args.get('ArrayExpress'),
   				PubMed = request.args.get('PubMed'),
				Accession = request.args.get('Accession'),
				name = name,   
				comments = comments)
		session.add(inquery)
		session.commit()
	flash('You have submitted an inquery successfully. ')
	return redirect(url_for('showMainPage'))


# User Helper Functions
def getAllInfor(AccessionID):
    try:
	data = {}
       	query = session.query(Main).filter_by(ArrayExpress = AccessionID).one()
	data["AccessionID"] = AccessionID
	data['GEO'] = query['GEO']
	data['Title']  = query['Title']
	data['OtherFactors'] = query['OtherFactors']
	data['description'] = query['description']
	data['PI'] = query['PI']
	data['email'] = query['email']
	data['Website'] = query['Website'] 
	data['GeoArea'] = query['GeoArea']
	data['ResearchArea'] = query['ResearchArea']

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
	app.run(host = '0.0.0.0', port = 5000)
