import urllib2
import urllib
import re

class PageClass:
	def __init__(self,url):
		self.url = url
	def read_page(self):
		self.content = urllib2.urlopen(self.url).read()
		return self.content
	def save_to_html(self,name):
		fileHandle = open (name, 'w' )
		fileHandle.write(content)
		fileHandle.close() 


def getAccessionID(keyword):
	#url = "http://www.ebi.ac.uk/arrayexpress/xml/v2/experiments?query=exptype%3ARNA-seq+organism%3A\"Mus+musculus\"" + keyword
	url = 'http://www.ebi.ac.uk/arrayexpress/xml/v2/experiments?'+urllib.urlencode({'query':keyword})+'&organism=Mus+musculus&exptype%5B%5D="RNA-seq"&exptype%5B%5D="sequencing+assay"&array='
	print url
	html = PageClass(url).read_page()

	find_re = re.compile(r'<accession>(.*?)</accession>')
	AccessionIDs= [x for x in find_re.findall(html)]  

	AccessionIDs = filter( lambda x: re.match(".-.*-.*" ,x), AccessionIDs)
	return AccessionIDs

