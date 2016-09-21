import os
import web
import sys
import json
import time
import getopt
import urllib
import urllib2
import threading
import subprocess
import ConfigParser
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException 
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class SeleniumHelper:
	driver = None
	WAIT = 99999

	def loadPage(self, page):
		try:
			self.driver.get(page)
			return True
			
		except:
			return False

	def submitForm(self, element):
		try:
			element.submit()
			return True
		except TimeoutException:
			return False

	def waitShowElement(self, selector, wait=99999):
		try:
			wait = WebDriverWait(self.driver, wait)
			element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
			return element
		except:
			return None

	def waitHideElement(self, selector, wait):
		try:
			wait = WebDriverWait(self.driver, wait)
			element = wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, selector)))
			return element
		except:
			return None

	def getElementFrom(self, fromObject, selector):
		try:
			return fromObject.find_element_by_css_selector(selector)
		except NoSuchElementException:
			return None

	def getElementsFrom(self, fromObject, selector):
		try:
			return fromObject.find_elements_by_css_selector(selector)
		except NoSuchElementException:
			return None		

	def getElement(self, selector):
		return self.getElementFrom(self.driver, selector)

	def getElements(self, selector):
		return self.getElementsFrom(self.driver, selector)

	def getElementFromValue(self, fromObject, selector):
		element = self.getElementFrom(fromObject, selector)
		if element:
			return element.text
		return None

	def getElementValue(self, selector):
		element = self.getElement(selector)
		if element:
			return element.text
		return None

	def getElementFromAttribute(self, fromObject, selector, attribute):
		element = self.getElementFrom(fromObject, selector)
		if element:
			return element.get_attribute(attribute)
		return None

	def getElementAttribute(self, selector, attribute):
		element = self.getElement(selector)
		if element:
			return element.get_attribute(attribute)
		return None

	def getParentLevels(self, node, levels):
		path = '..'
		if levels > 1:
			for i in range(1, levels):
				path = path + '/..'
		return node.find_element_by_xpath(path)

	def getParentNode(self, node):
		return node.find_element_by_xpath('..')

	def getChildNodes(self, node):
		return node.find_elements_by_xpath('./*')

	def selectAndWrite(self, field, value):
		fieldObject = self.getElement(field)
		fieldObject.send_keys(value)
		return fieldObject

	def waitAndWrite(self, field, value):
		fieldObject = self.waitShowElement(field, self.WAIT)
		fieldObject.send_keys(value)
		return fieldObject

	def pressEnter(self, fieldObject):
		fieldObject.send_keys(Keys.RETURN)
		return fieldObject

	def click(self, element):
		actions = webdriver.ActionChains(self.driver)
		actions.move_to_element(element)
		actions.click(element)
		actions.perform()

	def moveToElement(self, element):
		self.driver.execute_script("return arguments[0].scrollIntoView();", element)
		actions = webdriver.ActionChains(self.driver)
		actions.move_to_element(element)
		actions.perform()

	def saveScreenshot(self, path="screenshot.png"):
		self.driver.save_screenshot(path) 

class LinkedinChat(SeleniumHelper):
	LOGIN_USER_VALUE = 'USERNAME'
	LOGIN_PASS_VALUE = 'PASSWORD'
	TIMEOUT = 20
	READ_URL = 'https://www.linkedin.com/cap/comm/inbox'
	CHAT_URL = 'https://www.linkedin.com/messaging/compose?connId='
	# INITIAL_URL = 'https://www.linkedin.com/cap/dashboard/home'
	INITIAL_URL = 'https://www.linkedin.com'
	PROFILE_URL = 'https://www.linkedin.com/profile/view?id='
	LINKEDIN_URL = 'https://www.linkedin.com'
	POSTS_URL = 'https://www.linkedin.com/vsearch/ic?type=content&keywords='
	SEARCH_BAR_PATH = '#main-search-box'
	# LOGIN_USER_PATH = '#session_key-login'
	LOGIN_USER_PATH = '#login-email'
	# LOGIN_PASS_PATH = '#session_password-login'
	LOGIN_PASS_PATH = '#login-password'
	LOGIN_SUBMIT_PATH = '#loginbutton > input[type="submit"]'
	BUTTON_SEND_MESSAGE = '#tc-actions-send-message'
	TEXTBOX_MESSAGE = '#compose-message'
	TEXTBOX_SUBJECT = '#subject-msgForm'
	TEXTBOX_GO_SUBJECT = '.compose-subject'
	TEXTBOX_BODY = '#body-msgForm'
	TEXTBOX_GO_BODY = '.compose-txtarea'
	TEXTBOX_FORM = '.commentbox-form'
	TEXTBOX_CONTAINER = '.mentions-container'
	TEXTBOX_COMMENT = 'textarea.commentbox-entry'
	BUTTON_RECRUITER_ONE = '#tc-actions-send-message'
	BUTTON_RECRUITER_TWO = '.button-secondary'
	BUTTON_GO_INMAIL = '#tc-actions-send-inmail'
	BUTTON_SEND_INMAIL = '#compose-dialog-submit'
	BUTTON_INMAIL = '.send-inmail'
	BUTTON_GO_SEND_INMAIL = '.inmail-send-btn'
	BUTTON_COMMENT = '.commentbox-btn'
	TABLE_ROWS = '#capTable > tbody tr'
	ROW_URL = 'td:nth-child(2) > div:nth-child(1) > div:nth-child(2) > span:nth-child(1) > a:nth-child(1)'
	ROW_BODY = 'td:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(5)'
	ROW_DATE = 'td:nth-child(2) > div:nth-child(1) > div:nth-child(2) > span:nth-child(3)'
	ROW_SUBJECT = 'td:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(4) > a:nth-child(1)'
	POST_ARTICLE = '.article-content'
	POST_MESSAGES = '.comment-item'
	POST_COMMENTS = '.comments'
	POST_ITEM_TEXT = '.comment-text'
	POST_ITEM_FROM = '.commenter'

	ITEMS_CONTAINER = '#results'
	ITEMS_RESULTS = '.result'
	ITEM_TITLE = '.main-headline'
	ITEM_DESCRIPTION = '.description'
	COMMENT_CONTAINER = '.mentions-container'

	data = {}
	baseUrl = ''

	def bot_exec(self, section, action, params):
		exit = {'status': 'OK', 'data': 'test'}
		if section == 'msg':
			if action == 'send':
				if 'body' in params and 'to' in params:
					exit['data'] = self.send_message(params['body'], params['to'])
				else:
					exit['data'] = json.dumps(params)
			elif action == 'read':
				if 'to' in params:
					exit['data'] = self.read_messages(params['to'])
				else:
					exit['data'] = self.read_all_messages()
		elif section == 'search':
			if action == 'posts':
				if 'q' in params:
					exit['data'] = self.search_posts(params['q'])
				else:
					exit['data'] = json.dumps(params)
		elif section == 'post':
			if action == 'send':
				if 'body' in params and 'to' in params:
					exit['data'] = self.post_message(params['to'], params['body'])
				else:
					exit['data'] = json.dumps(params)
			elif action == 'read':
				if 'to' in params:
					exit['data'] = self.post_read_messages(params['to'])
				else:
					exit['data'] = json.dumps(params)
		exit['timestamp'] = str(time.time())
		return exit

	def login(self):
		print 'Opening login page'
		self.loadPage(self.INITIAL_URL)
		print 'Login page loaded'
		self.saveScreenshot('LNS00.png')
		print 'Writing credentials'
		self.waitAndWrite(self.LOGIN_USER_PATH, self.LOGIN_USER_VALUE)
		self.submitForm(self.selectAndWrite(self.LOGIN_PASS_PATH, self.LOGIN_PASS_VALUE))
		print 'Form submited'
		self.saveScreenshot('LNS01.png')
		# time.sleep(2)
		# self.saveScreenshot('LNS02.png')
		# print 'Loading intro page'
		# bar = self.waitShowElement(self.SEARCH_BAR_PATH)
		# print 'Intro page loaded'
		# self.saveScreenshot('LNS02.png')

	def close(self):
		self.driver.quit()

	def start(self):
		print 'Logging in'
		self.login()

	def getInfo(self, url):
		command = 'linkedin-scraper ' + url
		try:
			output = subprocess.check_output(command.split())
			userInfo = json.loads(output)
		except:
			userInfo = {}
		return userInfo

	def post_read_messages(self, to):
		exit = []
		self.loadPage(to)
		print 1
		comments = self.waitShowElement(self.POST_MESSAGES)
		print 2
		time.sleep(2)
		items = self.getElements(self.POST_MESSAGES)
		print 3
		for item in items:
			print 4
			commenter = self.getElementFromValue(item, self.POST_ITEM_FROM)
			print 5
			text = self.getElementFromValue(item, self.POST_ITEM_TEXT)
			print 6
			exit.append({'from': commenter, 'text': text})
		return exit

	def post_message(self, to, body):
		self.loadPage(to)
		textbox = self.waitShowElement(self.TEXTBOX_COMMENT)
		self.moveToElement(textbox)
		time.sleep(1)
		textbox.send_keys(body)
		time.sleep(2)
		button = self.getElement(self.BUTTON_COMMENT)
		time.sleep(1)
		self.click(button)
		return 'OK'

	def search_posts(self, query):
		exit = []
		self.loadPage(self.POSTS_URL + query)
		container = self.waitShowElement(self.ITEMS_CONTAINER)
		items = self.getElements(self.ITEMS_RESULTS)
		print len(items)
		for item in items:
			print 'FOUND'
			idValue = item.get_attribute('data-li-entity-id')
			url = self.getElementFromAttribute(item, self.ITEM_TITLE, 'href')
			url = url.split('?')[0]
			title = self.getElementFromValue(item, self.ITEM_TITLE)
			text = self.getElementFromValue(item, self.ITEM_DESCRIPTION)
			exit.append({'id': idValue, 'url': url, 'title': title, 'text': text})
		return exit

	def send_message(self, body, to):
		print 'Opening profile ' + to
		self.saveScreenshot('LNS03.png')
		print 'Loading'
		self.loadPage(to)
		print 'Loaded'
		self.saveScreenshot('LNS04.png')
		html = self.driver.page_source
		arr1 = html.split('connId=')
		if len(arr1) > 1:
			arr2 = arr1[1].split('&')
			connId = arr2[0]
			msgUrl = self.CHAT_URL + connId
			self.loadPage(msgUrl)
			self.saveScreenshot('LNS05.png')
			textarea = self.waitShowElement(self.TEXTBOX_MESSAGE)
			# checkbox = self.getElement('#enter-to-send-checkbox')
			# self.click(checkbox)
			textarea.send_keys(body)
			textarea.send_keys('\n\r')
			textarea.send_keys('\n\r')
			# button = self.getElement('.message-submit')
			# self.click(button)
			self.saveScreenshot('LNS06.png')
			print 'Message sent to: ' + to
			return body + ' ' + to
		else:
			print 'Message was not sent to: ' + to
			self.saveScreenshot('LNS07.png')
			return 'User not found'

	def read_all_messages(self):
		self.loadPage(self.READ_URL)
		time.sleep(1)
		rows = self.getElements(self.TABLE_ROWS)
		msgs = {}
		for row in rows:
			url = self.getElementFromAttribute(row, self.ROW_URL, 'href')
			idVal = url.split('show/')[1].split('?auth')[0]
			print idVal
			subject = self.getElementFromValue(row, self.ROW_SUBJECT)
			body = self.getElementFromValue(row, self.ROW_BODY)
			dateVal = self.getElementFromValue(row, self.ROW_DATE)
			if not idVal in msgs:
				msgs[idVal] = []
			msgs[idVal].append({'date':dateVal, 'subject':subject, 'body':body})
		return msgs

	def read_messages(self, to):
		exit = []
		idVal = self.get_user_id(to)
		print idVal
		msgs = self.read_all_messages()
		if idVal in msgs:
			exit = msgs[idVal]
		return exit

	def get_user_id(self, url):
		self.loadPage(url)
		html = self.driver.page_source
		idVal = html.split('memberId="')[1].split('";});')[0]
		return idVal

	def saveToFile(self, fileName):
		file_ = open(fileName, 'w')
		content = json.dumps(self.data, sort_keys=True, indent=4, separators=(',', ': '))
		file_.write(content)
		file_.close()

	def __init__(self, filename):
		config = ConfigParser.ConfigParser()
		config.read(filename)
		self.LOGIN_USER_VALUE = config.get('credentials', 'login_user_value')
		self.LOGIN_PASS_VALUE = config.get('credentials', 'login_pass_value')
		self.driver = webdriver.Firefox()
		# self.driver = webdriver.PhantomJS()
		# self.driver = webdriver.Chrome('./chromedriver')
		self.driver.set_page_load_timeout(self.TIMEOUT)

class ChatBot:
	port = 8080
	argv = None
	urls = (
	    '/', 'bot',
	    '/bot', 'bot_status_all',
	    '/bot/(.*)', 'bot_commands'
	)
	instances = {}

	class bot:        
	    def GET(self):
	        raise web.seeother('/static/index.html')

	class bot_status_all:        
	    def GET(self):
	        output = {"data":"null"}
	        exit = json.dumps(output)
	        return exit

	class bot_commands:
		instances = {}

		def GET(self, data):
			exit = {'status':'error', 'data':'Invalid arguments'}
			arrData = data.split('/')
			if len(arrData) >= 4:
				platform = arrData[0]
				instance = arrData[1]
				section = arrData[2]
				action = arrData[3]
				exit = {'status':'error', 'data': 'Invalid platform'}
				link = None
				if platform == 'twitter':
					if not instance in self.instances:
						self.instances[instance] = TwitterChat(instance)
						self.instances[instance].start()
				elif platform == 'facebook':
					if not instance in self.instances:
						self.instances[instance] = FacebookChat(instance)
						self.instances[instance].start()
				elif platform == 'linkedin':
					if not instance in self.instances:
						self.instances[instance] = LinkedinChat(instance)
						self.instances[instance].start()
				if instance in self.instances:
					exit = self.instances[instance].bot_exec(section, action, web.input())
			return json.dumps(exit)

	def start(self):
		thread = threading.Thread(target=self.run)
		thread.setDaemon(True)
		thread.start()

	def run(self):
		port = 8080
		app = web.application(self.urls, {
			'bot':self.bot, 
			'bot_commands':self.bot_commands, 
			'bot_status_all':self.bot_status_all})
		web.httpserver.runsimple(app.wsgifunc(), ("0.0.0.0", self.port))

	def __init__(self, argv):
		self.argv = argv
		opts, args = getopt.getopt(self.argv, "c:p:")
		if opts:
			for o, a in opts:
				if o == "-p":
					self.port = int(a)

def main(argv):
	chatbot = ChatBot(argv)
	chatbot.start()
	input('Press any key to exit.')

if __name__ == "__main__":
	argv = sys.argv[1:]
	main(argv)
