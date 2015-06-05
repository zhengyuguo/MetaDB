from database import Base, Main, Gene, Genotype, Disease, Tissue, Publication, Publication_Author, Publication_Keyword, Inquery, Accession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine =  create_engine('mysql://root:mysql@localhost:3306/metaDB')  #should change the password to the one you use in your local machine
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


inquery = Inquery(ArrayExpress = "1",PubMed = "222",name = "222", email = "223", comments = "da")

session.add(inquery)
session.commit()
