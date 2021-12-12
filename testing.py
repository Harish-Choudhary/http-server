import unittest
import requests
import sys
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import *


class test (unittest.TestCase):
	
	def test_200_GET_file(self):
		now = datetime.now()
		stamp = mktime(now.timetuple())
		date = str(format_date_time(stamp))
		general_headers = {'Date': date,'User-Agent':'Tester program','Language':'en-US'}
		print("\nTesting GET request 200 OK..")
		url = "http://127.0.0.1:"+'15000' +"/index.html"
		response = requests.get(url,headers=general_headers)
		try:
			self.assertEqual(response.status_code, 200)
			print("GET successfully tested...")
			
		except:
			print("GET test case failed...")
			
	def test_206_GET_rangefile(self):
		now = datetime.now()
		stamp = mktime(now.timetuple())
		date = str(format_date_time(stamp))
		general_headers = {'Date': date,'User-Agent':'Tester program','Language':'en-US','Range':'bytes=0-15'}
		print("\nTesting GET request 206 Ranges..")
		url = "http://127.0.0.1:"+'15000' +"/index.html"
		response = requests.get(url,headers=general_headers)
		try:
			self.assertEqual(response.status_code, 206)
			print("Ranges successfully tested...")
			
		except:
			print("Ranges test case failed...")		
	
	
	def test_416_GET_errorfile(self):
		now = datetime.now()
		stamp = mktime(now.timetuple())
		date = str(format_date_time(stamp))
		general_headers = {'Date': date,'User-Agent':'Tester program','Language':'en-US','Range':'bytes=0-10000'}
		print("\nTesting GET request 416  error Ranges..")
		url = "http://127.0.0.1:"+'15000' +"/index.html"
		response = requests.get(url,headers=general_headers)
		try:
			self.assertEqual(response.status_code, 416)
			print("Ranges error successfully tested...")
			
		except:
			print("Ranges test case failed...")	
	
	    
	def test_404_filenotfound(self):
		now = datetime.now()
		stamp = mktime(now.timetuple())
		date = str(format_date_time(stamp))
		general_headers = {'Date': date,'User-Agent':'Tester program','Language':'en-US'}
		print("\nTesting GET request for file not found..")
		url = "http://127.0.0.1:"+'15000' +"/random.html"
		response = requests.get(url,headers=general_headers)
		try:
			self.assertEqual(response.status_code, 404)
			print("Tested successfully 404 error..")
		except:
			print("This feature is failed in testing...")
    
	def test_414_urltoolong(self):
		now = datetime.now()
		stamp = mktime(now.timetuple())
		date = str(format_date_time(stamp))
		general_headers = {'Date': date,'User-Agent':'Tester program','Language':'en-US'}
		print("\nTesting URL too long feature")
		url = "http://127.0.0.1:"+'15000' +"/indexdfjakdasjdsalkkljdauijijskjdasjkadsa.html"
		response = requests.get(url)
		try:
			self.assertEqual(response.status_code, 414)
			print("Tested successfully URL too long feature...")
		except:
			print("Failed test case for URL too long...")
			
			
			
	#def test_get_406(self):
	#	print("\nTesting GET request for non existing file..")
	#	headers = {'Accept-Language': 'da'}
	#	response = requests.get("http://127.0.0.1:8000/index.html", headers=headers)
	#	try:
	#		self.assertEqual(response.status_code, 406)
	#		print("Working Fine for languages other than English...")
	#	except:
	#		print("Not Working Fine for other Language...")

	def test_post_405(self):
		now = datetime.now()
		stamp = mktime(now.timetuple())
		date = str(format_date_time(stamp))
		general_headers = {'Date': date,'User-Agent':'Tester program','Language':'en-US'}
		print("\nTesting post request for permission not allowed file..")
		url = "http://127.0.0.1:"+'15000' +"/about.html"
		general_headers['Content-Type'] = 'text/html'
		response = requests.post(url,headers=general_headers,data={"Name":"Harish"})
		try:
			self.assertEqual(response.status_code, 405)
			#print(response.status_code)
			print("Permissions not allowed tested successfully")
			#print(response.text)
		except:
			print("Test failed for file permissions...")

	def test_head_200(self):
		now = datetime.now()
		stamp = mktime(now.timetuple())
		date = str(format_date_time(stamp))
		general_headers = {'Date': date,'User-Agent':'Tester program','Language':'en-US'}
		print("\nTesting HEAD request for file..")
		
		url = "http://127.0.0.1:"+'15000' +"/index.html"
		response = requests.head(url,headers=general_headers)
		try:
			self.assertEqual(response.status_code, 200)
			print("Head 200 successfully tested...")
		except:
			print("Test Failed for this feature...\n")


	def test_head_404(self):
		now = datetime.now()
		stamp = mktime(now.timetuple())
		date = str(format_date_time(stamp))
		general_headers = {'Date': date,'User-Agent':'Tester program','Language':'en-US'}
		print("\nTesting HEAD request for not found error..")
		url = "http://127.0.0.1:"+'15000' +"/random.html"
		response = requests.head(url,headers=general_headers)
		try:
			self.assertEqual(response.status_code, 404)
			print("Head 404 successfully tested...\n")
		except:
			print("Test Failed for this feature\n...")

	def test_put_201(self):
		now = datetime.now()
		stamp = mktime(now.timetuple())
		date = str(format_date_time(stamp))
		general_headers = {'Date': date,'User-Agent':'Tester program','Language':'en-US'}
		print("\nTesting PUT request for adding a File ..")
		
		url = "http://127.0.0.1:"+'15000'+"/put1.html"
		general_headers['Content-Type'] = 'text/html'
		
		response = requests.put(url, headers=general_headers, data="This is a put file")
		try:
			self.assertEqual(response.status_code, 201)
			print("Successfully created a file on the server...")
			
		except:
			print("File not created ...")


	def test_delete_200(self):
		now = datetime.now()
		stamp = mktime(now.timetuple())
		date = str(format_date_time(stamp))
		general_headers = {'Date': date,'User-Agent':'Tester program','Language':'en-US'}
		print("\nTesting DELETE request for a file..")
		
		url = "http://127.0.0.1:"+'15000' +"/random.txt"
		response = requests.delete(url)
		
		try:
			self.assertEqual(response.status_code, 200)
			print("Successfully deleted the file on the server...")
			
			
		except:
			print("File not deleted ...")

	def test_post_201(self):
		now = datetime.now()
		stamp = mktime(now.timetuple())
		date = str(format_date_time(stamp))
		general_headers = {'Date': date,'User-Agent':'Tester program','Language':'en-US'}
		
		print("\nTesting POST request for a form..")
		response = requests.post("http://127.0.0.1:15000/form",data={'name':'harish', 'age':'20','college':'COEP','project':'Netwworks'})
		try:
			self.assertEqual(response.status_code, 201)
			print("Successfully saved record on the server...")
		except:
			print("Test failed...")


if __name__ == '__main__':
	#port = sys.argv[1]

	
	#test.port = sys.argv.pop(1)
	
	unittest.main()

