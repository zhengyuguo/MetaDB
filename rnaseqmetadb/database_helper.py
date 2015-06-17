from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import *
from werkzeug.security import generate_password_hash, check_password_hash
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
	


def getAllInquiry():
	query_main = session.query(Inquiry).all()
	return query_main

		

def getAllData():
	'''Query each table and combine the information together'''
	#try:
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
		#title.encode("UTF-8").decode("Shift-JIS")
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
	return [gene_names, disease_names, tissue_names, DATAs]
	#except:
		#return [None, None, None, None]

def getInforByID(IDs):
	'''Query the main table for AccessionIDs'''
	DATAs = []
	for ID in IDs:
		try:
			query = session.query(Main).filter_by(ArrayExpress = ID).one()
		except:
			continue
		data  = {}                           # a dictionary containing data will be transmitted
		title = query.Title 
		ID = query.ArrayExpress
		data["ID"] = ID
		data["title"] = unicode(title.decode('utf-8'),'utf-8')  # or:
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
	return DATAs

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

def getStatistics():
	'''Get statistical data from the tables'''
	query_pubs = session.query(Publication).all()
	statistics = {}
	statistics["disease"] = {}
	statistics["journal"] = {}
	statistics["researchArea"] = {}
	statistics["GeoArea"] = {}
	for query in  query_pubs:
		journal = query.Journal
		if not statistics["journal"].get(journal):
			statistics["journal"][journal] = 1
		else:
			statistics["journal"][journal] = statistics["journal"][journal] + 1
		AccessionID = query.ArrayExpress
		query_diseases = session.query(Disease).filter_by(ArrayExpress = AccessionID).all()
		for query_dis in query_diseases:
			disease = query_dis.disease
			if not statistics["disease"].get(disease):
				statistics["disease"][disease] = 1
			else:
				statistics["disease"][disease] = statistics["disease"][disease] + 1
	query_mains = session.query(Main).all()
	for query in  query_mains:
		researchArea = query.ResearchArea
		if not statistics["researchArea"].get(researchArea):
			statistics["researchArea"][researchArea] = 1
		else:
			statistics["researchArea"][researchArea] = statistics["researchArea"][researchArea] + 1
		GeoArea = query.GeoArea
		if not statistics["GeoArea"].get(GeoArea):
			statistics["GeoArea"][GeoArea] = 1
		else:
			statistics["GeoArea"][GeoArea] = statistics["GeoArea"][GeoArea] + 1
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
	try:
		pwhash =  generate_password_hash(password)
		print password
		newUser = User(name=name,
					   email = email,
					   pwhash = pwhash,
					   institution = institution, 
					   downloadedtimes = 0)
		session.add(newUser)
		session.commit()
		return 5
	except:
		return 4 


def checkUserPassword(email,password):
	'''Check the password by email: -1 means no user; 0 means wrong password; 1 means correct'''
	try:
		user = session.query(User).filter_by(email=email).one()
		print check_password_hash(user.pwhash, password)
		if check_password_hash(user.pwhash , password):
			return 1;
		else:
			return 0
	except:
		return -1    
