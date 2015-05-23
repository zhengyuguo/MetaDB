
DROP DATABASE metaDB;
CREATE DATABASE metaDB;
USE metaDB;


DROP TABLE IF EXISTS main;
DROP TABLE IF EXISTS Gene;
DROP TABLE IF EXISTS Genetype;
DROP TABLE IF EXISTS Disease;
DROP TABLE IF EXISTS Tissue;
DROP TABLE IF EXISTS Publication;
DROP TABLE IF EXISTS Publication_Author;
DROP TABLE IF EXISTS Publication_keyword;



create table Main(
	ArrayExpress VARCHAR(20),
	GEO VARCHAR(20),
	Title text,
	description text,
	OtherFactors VARCHAR(50),
	PI VARCHAR(50),
	email VARCHAR(50),
	Website VARCHAR(511),
	GeoArea VARCHAR(50),
	ResearchArea VARCHAR(50),
	primary key (ArrayExpress)
);


create table Gene(
	ID int not null auto_increment,
	ArrayExpress VARCHAR(20),
	Gene VARCHAR(50),
	GeneMGI VARCHAR(50),
	primary key (ID)
);

create table Genotype(
	ID int not null auto_increment,
	ArrayExpress VARCHAR(20),
	Genotype VARCHAR(50),
	primary key (ID)
);

create table Disease(
	ID int not null auto_increment,
	ArrayExpress VARCHAR(20),
	disease VARCHAR(50),
	diseaseMesh VARCHAR(50),
	primary key (ID)
);

create table Tissue(
	ID int not null auto_increment,
	ArrayExpress VARCHAR(20),
	Tissue VARCHAR(50),
	TissueID VARCHAR(50),
	primary key (ID)
);

create table Publication(
	ID int not null auto_increment,
	ArrayExpress VARCHAR(20),
	PubMed VARCHAR(50),
	Title text,
	Abstract text,
	Journal VARCHAR(50),
	primary key (ID)
);

create table Publication_Author(
	ID int not null auto_increment, 
	ArrayExpress VARCHAR(20),
	PubMed VARCHAR(50),
	Author VARCHAR(50),
	primary key (ID)
); 

create table Publication_Keyword(
	ID int not null auto_increment,
	ArrayExpress VARCHAR(20),
	PubMed VARCHAR(50),
	keyword VARCHAR(50),
	primary key (ID)
);


create table inquery(
	ID int not null auto_increment,
	Accession VARCHAR(50) not null,
	name VARCHAR(50) not null,
	email VARCHAR(50) not null,
	PubMed VARCHAR(50),
	comments text not null,
	primary key (ID)
);


create table accession(
	ID int not null auto_increment,
	randomcode VARCHAR(50),
	name VARCHAR(50) not null,
	email VARCHAR(50) not null,
	institution VARCHAR(50) not null,
	expirationdate date not null, //registration time +4 
	downloadedtimes int default 0 not null,
	primary key (ID)
);

