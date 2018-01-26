class portageWalker:
	import os
	'''
	portageWalker - gets all the directory names (package categories) from the portage directory

	@params: The class itself requires no params
	@return: The class returns nothing
	'''

	def __init__(self):

		self.portageDir = "/usr/portage/"
		self.language = "en"
		self.exclude = ("distfiles", "eclass", "licenses", "metadata", "profiles", "scripts")
		self.categories = {}


	def getTopLevel(self,directory):

		'''
		getTopLevel - Creates a list of the portage category directories

		@params directory: The portage directory to search
		@return topLevel:  A list of all of the directories in /usr/portage 

		'''
		topLevel = []
		for entry in self.os.listdir(directory):
			if (self.os.path.isdir(self.os.path.join(directory, entry)) and (entry not in self.exclude)):
				topLevel.append(entry)

		topLevel.sort()
		return topLevel


	def getMetadata(self,portage, topLevelDir, lang):
		'''
		getMetadata parses the metadat.xml inside each category directoy

		@params portage: The portage directory (usually /usr/portage)
		@params topLevelDir: The category directory e.g. app-admin
		@params lang: The language to search for
		@return text: The text of the category description

		'''
		# This will only be used for the TLD. 
		# I'll extract the DESCRIPTION from ebuild files
		# for each of the packages

		import xml.etree.ElementTree as ET
	
		cat = {} # dictionary to hold the descriptions
		tree = ET.parse(portage+topLevelDir+'/'+"metadata.xml")
		root = tree.getroot()
	
		for child in root:
			# walk through the metadata.xml file looking for our language element
			if child.attrib['lang'] == lang:
				# get the text of the element 
				text = " ".join(child.text.split())
				# debug print(topLevelDir)
				# debug print(text)
				return text
			

	def tldDict(self,lang,portDir="/usr/portage/"):
		'''
		tldDict - Creates a dictionary of directory_name:metadata_description

		@params lang: The language to search for
		@params portDir: The portage directory - defaults to /usr/portage
		@return categories: returns a dictionary of directory_name:metadata_description  

		'''
		portageDir=portDir
		language=lang
		categories = {}
		topLevelDirs = (self.getTopLevel(portageDir))
		for tld in topLevelDirs:
			categories[tld] = self.getMetadata(portageDir,tld, language)
		return categories
		
if __name__ == "__main__":
	portageDir="/usr/portage/"
	language='en'
	categories = {}
	pw = portageWalker()
	topLevelDirs = (pw.getTopLevel(portageDir))
	for tld in topLevelDirs:
		categories[tld] = pw.getMetadata(portageDir,tld, language)

	print(categories)
	for element in categories:
		print(element, ":",  categories[element])
