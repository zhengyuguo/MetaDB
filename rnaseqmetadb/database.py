import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.mysql import TEXT,DATETIME
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


	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'ArrayExpress': self.ArrayExpress,
			'PubMed':self.PubMed,
			'Author':self.Author,
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

class Inquery(Base):
	__tablename__ = 'inquery'

	id = Column(Integer, primary_key=True)
	ArrayExpress = Column(String(50), nullable=False)
	name = Column(String(50), nullable=False)
	email = Column(String(50), nullable=False)
	PubMed = Column(String(50))
	comments = Column(TEXT, nullable=False)


	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'ArrayExpress': self.ArrayExpress,
			'PubMed':self.PubMed,
			'name':self.name,
			'email':self.email,
			'comments':self.comments,
		}

class Accession(Base):
	__tablename__ = 'accession'

	id = Column(Integer, primary_key=True)
	randomcode = Column(String(50), nullable=False)
	name = Column(String(50), nullable=False)
	email = Column(String(50), nullable=False)
	institution = Column(String(50), nullable=False)
	expirationdate = Column(DATETIME, nullable=False)
	downloadedtimes = Column(Integer, nullable=False,default = 0)


	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'randomcode': self.randomcode,
			'name':self.name,
			'email':self.email,
			'institution':self.institution,
			'expirationdate':self.expirationdate,
			'downloadedtimes':self.downloadedtimes,
		}

engine =  create_engine('mysql://root:mysql@localhost:3306/metaDB')


Base.metadata.create_all(engine)