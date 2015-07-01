import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.mysql import TEXT,DATETIME, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Main(Base):
	__tablename__ = 'main'

	ArrayExpress = Column(String(20), primary_key=True)
	GEO = Column(String(20))
	Title = Column(TEXT)
	description = Column(TEXT)
	OtherFactors = Column(String(50))
	PI = Column(String(50))
	email = Column(String(50))
	Website = Column(String(511))
	GeoArea = Column(String(50))
	ResearchArea = Column(String(50))


	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'ArrayExpress': self.ArrayExpress,
			'GEO':self.GEO,
			'Title':self.Title,
			'description':self.description,
			'OtherFactors':self.OtherFactors,
			'PI':self.PI,
			'email':self.email,
			'Website':self.Website,
			'GeoArea':self.GeoArea,
			'ResearchArea':self.ResearchArea,
		}


class Gene(Base):
	__tablename__ = 'gene'
	
	id = Column(Integer, primary_key=True)
	ArrayExpress = Column(String(20))
	Gene = Column(String(50))
	GeneMGI = Column(String(50))


	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'ArrayExpress': self.ArrayExpress,
			'Gene':self.Gene,
			'GeneMGI':self.GeneMGI,
		}

class Genotype(Base):
	__tablename__ = 'genotype'

	id = Column(Integer, primary_key=True)
	ArrayExpress = Column(String(20))
	Genotype = Column(String(50))


	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'ArrayExpress': self.ArrayExpress,
			'Genotype':self.Genotype,
		}


class Disease(Base):
	__tablename__ = 'disease'

	id = Column(Integer, primary_key=True)
	ArrayExpress = Column(String(20))
	disease = Column(String(50))
	diseaseMesh = Column(String(50))


	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'ArrayExpress': self.ArrayExpress,
			'disease':self.disease,
			'diseaseMesh':self.diseaseMesh,
		}

class Tissue(Base):
	__tablename__ = 'tissue'

	id = Column(Integer, primary_key=True)
	ArrayExpress = Column(String(20))
	Tissue = Column(String(50))
	TissueID = Column(String(50))


	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'ArrayExpress': self.ArrayExpress,
			'Tissue':self.Tissue,
			'TissueID':self.TissueID,
		}

class Publication(Base):
	__tablename__ = 'publication'

	id = Column(Integer, primary_key=True)
	ArrayExpress = Column(String(20))
	PubMed = Column(String(50))
	Title = Column(TEXT)
	Abstract  = Column(TEXT)
	Journal = Column(String(50))
	Year = Column(Integer)


	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'ArrayExpress': self.ArrayExpress,
			'PubMed':self.PubMed,
			'Title':self.Title,
			'Abstract':self.Abstract,
			'Journal':self.Journal,
			'Year':self.Year,
		}

class Publication_Author(Base):
	__tablename__ = 'publication_Author'

	id = Column(Integer, primary_key=True)
	ArrayExpress = Column(String(20))
	PubMed = Column(String(50))
	Author = Column(String(50))
	AuthorOrder = Column(Integer)


	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'ArrayExpress': self.ArrayExpress,
			'PubMed':self.PubMed,
			'Author':self.Author,
			'AuthorOrder':self.AuthorOrder,
		}

class Publication_Keyword(Base):
	__tablename__ = 'publication_Keyword'

	id = Column(Integer, primary_key=True)
	ArrayExpress = Column(String(20))
	PubMed = Column(String(50))
	keyword = Column(String(50))


	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'ArrayExpress': self.ArrayExpress,
			'PubMed':self.PubMed,
			'keyword':self.keyword,
		}

class Inquiry(Base):
	__tablename__ = 'inquiry'

	id = Column(Integer, primary_key=True)
	ArrayExpress = Column(String(50), nullable=False)
	name = Column(String(50), nullable=False)
	email = Column(String(50), nullable=False)
	PubMed = Column(String(50))
	comments = Column(TEXT, nullable=False, default = "")
	status = Column(String(50), nullable=False,default="unprocessed")


	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'id': self.id,
			'ArrayExpress': self.ArrayExpress,
			'PubMed':self.PubMed,
			'name':self.name,
			'email':self.email,
			'comments':self.comments,
			'status':self.status,
		}

class User(Base):
	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)
	name = Column(String(50), nullable=False)
	email = Column(String(50), nullable=False)
	institution = Column(String(50), nullable=False)
	pwhash = Column(String(200), nullable=False)
	downloadedtimes = Column(Integer, nullable=False,default = 0)
	randomcode = Column(String(50), nullable=False)
	ismanager = Column(BOOLEAN,nullable=False,default = False )
	verified = Column(BOOLEAN,nullable=False,default = False )

	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'pwhash': self.pwhash,
			'name':self.name,
			'email':self.email,
			'institution':self.institution,
			'downloadedtimes':self.downloadedtimes,
			'randomcode':self.randomcode,
			'ismanager':self.ismanager,
			'verified':self.verified,
		}

engine =  create_engine('mysql://root:mysql@localhost/metaDB')


Base.metadata.create_all(engine)
