
import MySQLdb

class data:
	def __init__(ArrayExpress,GEO,Title,description,OtherFactors,PI,email,Website,GeoArea,ResearchArea)

		

def importData(data):
	conn=MySQLdb.connect(host='localhost',user='root',passwd='root',db='test',port=3306)
	cur=conn.cursor()
	cur.execute('select * from user')
	cur.close()
	conn.close() 
