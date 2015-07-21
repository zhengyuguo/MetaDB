# vim: set noexpandtab tabstop=2: 
from database import *
from email_helper import *
from werkzeug.security import generate_password_hash, check_password_hash
import random, string
import sys
import json
from sqlalchemy import func
from sqlalchemy import distinct
from exception import *

reload(sys)
sys.setdefaultencoding('cp1252')

def get_distinct_gene():
	local_session = db_session()
	q = local_session.query(Gene.Gene).distinct().filter(Gene.Gene != '').filter(Gene.Gene != None)
	res = sorted([ i.Gene for i in q.all()] , key=lambda x: x.lower())
	local_session.close()
	return res

def get_distinct_disease():
	local_session = db_session()
	q = local_session.query(Disease.disease).distinct().filter(Disease.disease != '').filter(Disease.disease != None)
	res = sorted([ i.disease for i in q.all()] , key=lambda x: x.lower())
	local_session.close()
	return res

def get_distinct_tissue():
	local_session = db_session()
	q = local_session.query(Tissue.Tissue).distinct().filter(Tissue.Tissue != '').filter(Tissue.Tissue != None)
	res = sorted([ i.Tissue for i in q.all()] , key=lambda x: x.lower())
	local_session.close()
	return res

def get_summary_info_for_each_entry():
	local_session = db_session()
	q = local_session.query(Main.ArrayExpress, Main.Title, func.group_concat(Gene.Gene.distinct().op('SEPARATOR')(", ")), func.group_concat(Tissue.Tissue.distinct().op('SEPARATOR')(", ")), func.group_concat(Disease.disease.distinct().op('SEPARATOR')(", "))).outerjoin(Gene, Main.ArrayExpress == Gene.ArrayExpress).outerjoin(Disease, Main.ArrayExpress == Disease.ArrayExpress).outerjoin(Tissue, Main.ArrayExpress == Tissue.ArrayExpress).group_by(Main.ArrayExpress)
	colnames = [ 'ID','title','gene','tissue','disease']
	res = [ dict(zip(colnames,i)) for i in q.all()]
	local_session.close()
	return res

def getAccByConstraints(constraints):
	local_session = db_session()
	acc = set([])
	if 'Gene' in constraints.keys():
		acc.update([ query.ArrayExpress for query in local_session.query(Gene).filter_by(Gene = constraints["Gene"]).all()])
	if 'Disease' in constraints.keys():
		acc.update([ query.ArrayExpress for query in local_session.query(Disease).filter_by(disease = constraints["Disease"]).all()])
	if 'Tissue' in constraints.keys():
		acc.update([ query.ArrayExpress for query in local_session.query(Tissue).filter_by(Tissue = constraints["Tissue"]).all()])
	if len(constraints) == 0:
		acc.update([ query.ArrayExpress for query in local_session.query(Main).all()])
	local_session.close()
	return acc		

def getAllInfor(AccessionID):
	local_session = db_session()
	data = {}
	query =local_session.query(Main).filter_by(ArrayExpress = AccessionID).one()
	data.update(query.__dict__)
	query = local_session.query(Gene).filter_by(ArrayExpress = AccessionID).all()
	data['Gene'] = [ x.__dict__ for x in query ]
	query = local_session.query(Genotype).filter_by(ArrayExpress = AccessionID).all()
	data['Genotype'] =  [ x.__dict__ for x in query ] 
	query = local_session.query(Disease).filter_by(ArrayExpress = AccessionID).all()
	data['disease'] = [ x.__dict__ for x in query ] 
	query = local_session.query(Tissue).filter_by(ArrayExpress = AccessionID).all()
	data['Tissue'] = [ x.__dict__ for x in query ]
	query = local_session.query(Publication).filter_by(ArrayExpress = AccessionID).all()
	data['Publication'] = [ x.__dict__ for x in query ]
	query = local_session.query(Publication_Author).filter_by(ArrayExpress = AccessionID).order_by(Publication_Author.AuthorOrder).all()
	data['Author'] = ", ".join([ x.Author for x in query ])
	query = local_session.query(Publication_Keyword).filter_by(ArrayExpress = AccessionID).all()
	data['keyword'] = ", ".join([ x.keyword for x in query ])
	query = local_session.query(Age).filter_by(ArrayExpress = AccessionID).all()
	data['Age'] = [ x.__dict__ for x in query ]
	local_session.close()

	return data

def getStatistics():
	try:
		local_session = db_session()
		statistics={}
		journal_query = local_session.query(distinct(Publication.PubMed),func.count(Publication.Journal),Publication.Journal).group_by(Publication.Journal).all()
		statistics["journal"] = {key : count for id, count, key in journal_query}
		year_query = local_session.query(distinct(Publication.PubMed),func.count(Publication.Year),Publication.Year).group_by(Publication.Year).all()
		statistics["year"] = {key : count for id, count, key in year_query} 
		geoArea_query = local_session.query(distinct(Main.PI),func.count(distinct(Main.PI)),Main.GeoArea).group_by(Main.GeoArea).all()
		statistics["geoArea"] = {key : count for id, count, key in geoArea_query}
		local_session.close()
	except:
		statistics = None
	finally:
		return statistics

def createUser(name, email, password,institution):
	local_session = db_session()
	account = local_session.query(User).filter_by(email=email).all()
	if len(account) != 0:   #check the input email has been used or not
		raise UserCreate_REPEMAIL
	if len(password) < 6:
		raise UserCreate_SHORT
	if len(password) > 15:
		raise UserCreate_LONG
	if institution is None:
		raise UserCreate_NOINST
	if name is None:
		raise UserCreate_NONAME
	pwhash =  generate_password_hash(password)
	randomcode = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	newUser = User(name=name,
					   email = email,
					   pwhash = pwhash,
					   institution = institution, 
						 randomcode = randomcode,
					   downloadedtimes = 0)
	local_session.add(newUser)
	local_session.commit()
	send_notification_email(newUser.name, newUser.email, newUser.randomcode)
	local_session.close()
	return 0

def checkUserPassword(email,password):
	try:
		local_session = db_session()
		user = local_session.query(User).filter_by(email=email).one()
	except:
		raise Login_NOUSER
	else:
		if check_password_hash(user.pwhash , password):
			if user.verified:
				return 1
			else: 
				raise Login_NOTVERIFIED			
		else:
			raise Login_WRONGPW 

def verifyUserEmail(email,randomcode):
	try:
		local_session = db_session()
		user = local_session.query(User).filter_by(email=email).one()
	except:
		raise VerifyEmail_NOUSER
	else:
		if user.verified:
			raise VerifyEmail_EXPIRED
		elif user.randomcode == randomcode:
			user.verified = True
			local_session = db_session()
			local_session.add(user)
			local_session.commit()
			local_session.close()
			return 
		else:
			raise VerifyEmail_FAILDED

def saveToInquiry(ArrayExpress, PubMed, name, email, comments):
	inquiry = Inquiry(ArrayExpress = ArrayExpress,
						PubMed = ArrayExpress,
						name = name, 
						email = email, 
						comments = comments )
	local_session = db_session()
	local_session.add(inquiry)
	local_session.commit()
	local_session.close()
	return

def changeInquiryStatus(ID, status):
	try:
		inquiry = Inquiry.query.filter_by(id = ID).one()
		inquiry.status = status
		local_session = db_session()
		local_session.add(inquiry)
		local_session.commit()
		local_session.close()
	except:
		return 0
	return 5
	
def deleteInquiry(ID):
	try:
		inquiry = Inquiry.query.filter_by(id = ID).one()
		local_session = db_session()
		local_session.delete(inquiry)
		local_session.commit()
		local_session.close()
	except:
		return 0
	return 5

def getAllInquiry():
	query_main = Inquiry.query.all()
	return query_main

		

   



