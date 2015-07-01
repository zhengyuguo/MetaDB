# vim: set noexpandtab tabstop=2: 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import *
from email_helper import *
from werkzeug.security import generate_password_hash, check_password_hash
import random, string
import sys
import json

reload(sys)
sys.setdefaultencoding('cp1252')

DBSession = sessionmaker(bind=engine)
session = DBSession()


# User Helper Functions for Database
def saveToInquiry(ArrayExpress, PubMed, name, email, comments):
	'''saveToInquiry: output:
					1 means AccessionID is null;
					2 means name is null;
					3 means email is null
					4 means other errors
					5 means success	'''
	if ArrayExpress is None or ArrayExpress is "":
		return 1
	if name is None or name is "":
		return 2
	if email is None or email is "":
		return 3
	try:
		inquiry = Inquiry(ArrayExpress = ArrayExpress,
							PubMed = ArrayExpress,
							name = name, 
							email = email, 
							comments = comments )

		session.add(inquiry)
		session.commit()
		return 5
	except:
		return 4

def changeInquiryStatus(ID, status):
	try:
		inquiry = session.query(Inquiry).filter_by(id = ID).one()
		inquiry.status = status
		session.add(inquiry)
		session.commit()
	except:
		return 0
	return 5
	
def deleteInquiry(ID):
	try:
		inquiry = session.query(Inquiry).filter_by(id = ID).one()
		session.delete(inquiry)
		session.commit()
	except:
		return 0
	return 5

def getAllInquiry():
	query_main = session.query(Inquiry).all()
	return query_main

		

def getAllData():
	'''Query each table and combine the information together'''
	gene_names = list(set([x.Gene for x in session.query(Gene).all()]))
	gene_names = sorted(gene_names, key=lambda x: x.lower())
	if "" in gene_names:
		gene_names.remove("")

	disease_names = list(set([x.disease for x in session.query(Disease).all()]))
	disease_names = sorted(disease_names, key=lambda x: x.lower())
	if "" in disease_names:
		disease_names.remove("")

	tissue_names = list(set([x.Tissue for x in session.query(Tissue).all()]))
	tissue_names = sorted(tissue_names, key=lambda x: x.lower())
	if "" in tissue_names:
		tissue_names.remove("")

	query_main = session.query(Main).all()
	DATAs = []
	for query in query_main:
		data  = {}                           # a dictionary containing data will be transmitted
		title = query.Title 
		ID = query.ArrayExpress
		data["ID"] = ID
		#title.encode("UTF-8").decode("Shift-JIS")
		data["title"] = title
		data["gene"] = ", ".join([ g.Gene for g in session.query(Gene).filter_by(ArrayExpress = ID).all()])
		data["disease"] = ", ".join([ g.disease for g in session.query(Disease).filter_by(ArrayExpress = ID).all()])
		data["tissue"] = ", ".join([ g.Tissue for g in session.query(Tissue).filter_by(ArrayExpress = ID).all()])
		DATAs.append(data)
	return [gene_names, disease_names, tissue_names, DATAs]

def getAccByConstraints(constraints):
	acc = set([])
	if 'Gene' in constraints.keys():
		acc.update([ query.ArrayExpress for query in session.query(Gene).filter_by(Gene = constraints["Gene"]).all()])
	if 'Disease' in constraints.keys():
		acc.update([ query.ArrayExpress for query in session.query(Disease).filter_by(disease = constraints["Disease"]).all()])
	if 'Tissue' in constraints.keys():
		acc.update([ query.ArrayExpress for query in session.query(Tissue).filter_by(Tissue = constraints["Tissue"]).all()])
	if len(constraints) == 0:
		acc.update([ query.ArrayExpress for query in session.query(Main.ArrayExpress).all()])
	return acc		




def getAllInfor(AccessionID):
	'''Query all the tables and combine all the information by AccessionID'''
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
		data['Gene'] = [ x.Gene for x in query ]
		data['GeneMGI'] = [ x.GeneMGI for x in query ]

		query = session.query(Genotype).filter_by(ArrayExpress = AccessionID).all()
		data['Genotype'] =  [ x.Genotype for x in query ] 

		query = session.query(Disease).filter_by(ArrayExpress = AccessionID).all()
		data['disease'] = query 

		query = session.query(Tissue).filter_by(ArrayExpress = AccessionID).all()
		data['Tissue'] = query

		query = session.query(Publication).filter_by(ArrayExpress = AccessionID).all()
		data['PubMed'] = [ x.PubMed for x in query ] 
		data['Publication'] =  [ x.Title for x in query ] 
		data['Abstract'] =  [ x.Abstract for x in query ] 
		data['Journal'] =  [ x.Journal for x in query ] 
		data['Year'] =  [ x.Year for x in query ] 

		query = session.query(Publication_Author).filter_by(ArrayExpress = AccessionID).order_by(Publication_Author.AuthorOrder).all()
		data['Author'] = [ x.Author for x in query ] 
		
		query = session.query(Publication_Keyword).filter_by(ArrayExpress = AccessionID).all()
		data['keyword'] = [ x.keyword for x in query ] 

		return data
	except:
		return None

from sqlalchemy import func
from sqlalchemy import distinct
def getStatistics():
	'''Get statistical data from the tables'''
	statistics={}
	journal_query = session.query(distinct(Publication.PubMed),func.count(Publication.Journal),Publication.Journal).group_by(Publication.Journal).all()
	statistics["journal"] = {key : count for id, count, key in journal_query}

	year_query = session.query(distinct(Publication.PubMed),func.count(Publication.Year),Publication.Year).group_by(Publication.Year).all()
	statistics["year"] = {key : count for id, count, key in year_query}

	geoArea_query = session.query(distinct(Main.ArrayExpress),func.count(Main.GeoArea),Main.GeoArea).group_by(Main.GeoArea).all()
	statistics["geoArea"] = {key : count for id, count, key in geoArea_query}
	return statistics

   
def createUser(name, email, password,institution):
	'''Create user: -1 means email has been used; 
					0 means password is too short; 
					1 means password is too long;
					2 means insititute is not provided
					3 means name is not provided.
					4 means other errors;
					5 means successfully create user '''
	account = session.query(User).filter_by(email=email).all()
	if len(account) != 0:   #check the input email has been used or not
		return -1
	if len(password) < 6:
		return 0 
	if len(password) > 15:
		return 1 
	if institution is None:
		return 2 
	if name is None:
		return 3 

	pwhash =  generate_password_hash(password)
	randomcode = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	newUser = User(name=name,
					   email = email,
					   pwhash = pwhash,
					   institution = institution, 
						 randomcode = randomcode,
					   downloadedtimes = 0)
	session.add(newUser)
	session.commit()
	#send_email_test()
	send_notification_email(newUser)
	return 5

def send_verification_email(email):
		user = session.query(User).filter_by(email=email).one()
		send_notification_email(user)

def checkUserPassword(email,password):
	'''Check the password by email: -1 means no user; 0 means wrong password; 1 means correct; 
	2 means account has not been verfied.'''
	try:
		user = session.query(User).filter_by(email=email).one()
		print check_password_hash(user.pwhash, password)
		if check_password_hash(user.pwhash , password):
			if not user.verified:
				return 2			
			return 1
		return 0
	except:
		return -1    


def verifyUserEmail(email,randomcode):
	'''verify the user email by randomcode. 
		-1 means no such a user. 0 means fail verification; 1 means success. 2 means verified before.
		'''
	try:
		user = session.query(User).filter_by(email=email).one()
		if user.verified:
			return 2
		if user.randomcode == randomcode:
			user.verified = True
			session.add(user)
			session.commit()
			return 1;
		else:
			return 0
	except:
		return -1 
#def extractInfor(queries, constraints, filter_f):
#	'''Given queries, extract information.
#		queries are all the queires to be extracted information from;
#		constraints is the constriants filled on home.html.
#		filter_f is a flag. filter_f == True means the results will be filtered using the constraints;
#												filter_f == False means the results wil not be filtered;
#	'''
#	
#	DATAs = []
#	try:		
#		for query in queries:
#			data  = {}                           # a dictionary containing data will be transmitted
#			title = query.Title 
#			ID = query.ArrayExpress
#			data["ID"] = ID
#			data["title"] = title  # or:
#			####################### gene queried by ID ##########
#			query_gene = session.query(Gene).filter_by(ArrayExpress = ID).all()
#			gene = ""
#			for g in query_gene:
#				gene = gene+ " " + g.Gene
#			data["gene"] = gene
#			if filter_f is True and constraints["genename"] != "All" and constraints["genename"] not in data["gene"]:
#				continue
#			####################### Disease queried by ID ##########
#			query_disease = session.query(Disease).filter_by(ArrayExpress = ID).all()
#			disease = ""
#			for g in query_disease:
#				disease = disease+ " " + g.disease
#			data["disease"] = disease
#			if filter_f is True and constraints["diseasename"] != "All" and constraints["diseasename"] not in data["disease"]:
#				continue
#			####################### tissue queried by ID ##########
#			query_tissue = session.query(Tissue).filter_by(ArrayExpress = ID).all()
#			tissue = ""
#			for g in query_tissue:
#				tissue = tissue+ " " + g.Tissue
#			data["Tissue"] = tissue
#			if filter_f is True and constraints["tissuetype"] != "All" and constraints["tissuetype"] not in data["Tissue"]:
#				continue
#			DATAs.append(data)
#		return DATAs
#	except:
#		return []
#
#def getInforCombined(IDs, constraints):
#	queries = []
#	if constraints["genename"] != "All":
#		print IDs
#		print [ query.ArrayExpress for query in session.query(Gene).filter_by(Gene = constraints["genename"]).all()]
#		IDs = IDs + [ query.ArrayExpress for query in session.query(Gene).filter_by(Gene = constraints["genename"]).all()]
#		print IDs
#	if constraints["diseasename"] != "All":
#		IDs = IDs + [ query.ArrayExpress for query in session.query(Disease).filter_by(disease = constraints["diseasename"]).all()]
#	if constraints["tissuetype"] != "All":
#		IDs = IDs + [ query.ArrayExpress for query in session.query(Tissue).filter_by(Tissue = constraints["tissuetype"]).all()]
#	#IDs = list(set(IDs))
#	for ID in IDs:
#		try:
#			query = session.query(Main).filter_by(ArrayExpress = ID).one()				
#		except:
#			continue
#		queries.append(query)
#	print len(queries)	
#	return extractInfor(queries, constraints, False)
	

#def getInforByIDFilteredByConstraints(IDs, constraints):
#	'''Query the main table for AccessionIDs'''
#	queries = []
#	print IDs
#	if IDs is None:
#		queries = session.query(Main).all()	
#	else:
#		for ID in IDs:
#			try:
#				query = session.query(Main).filter_by(ArrayExpress = ID).one()				
#			except:
#				continue
#			queries.append(query)	
#	return extractInfor(queries, constraints, True) 
