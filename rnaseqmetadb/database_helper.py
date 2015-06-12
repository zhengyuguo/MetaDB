from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Main, Gene, Genotype, Disease, Tissue, Publication, Publication_Author, Publication_Keyword, Inquery, Accession
import json

engine =  create_engine('mysql://root:mysql@localhost/metaDB')  #should change the password to the one you use in your local machine
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# User Helper Functions for Database
def saveToInquery(ArrayExpress, PubMed, name, email, comments):
	inquery = Inquery(ArrayExpress = ArrayExpress,
						PubMed = ArrayExpress,
						name = name, 
						email = email, 
						comments = comments )

	session.add(inquery)
	session.commit()


def saveToAccession(name, email, password,institution):
	newUser = Accession(name=name,
							randomcode = "111",
							email = email,
							password = password,
							institution = institution, 
							downloadedtimes = 0)
	session.add(newUser)
	session.commit()


def getAllInquery():
	try:
		query_main = session.query(Inquery).all()
		return query_main
	except:
		return None
		

def getAllData():
	'''Query each table and combine the information together'''
	try:
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
		return [gene_names, disease_names, tissue_names, DATAs]
	except:
		return [None, None, None, None]

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
	return statistics


def getUserPassword(email):
	'''Check the password by email'''
	try:
		user = session.query(Accession).filter_by(email=email).one()
		return user.password
	except:
		return None
