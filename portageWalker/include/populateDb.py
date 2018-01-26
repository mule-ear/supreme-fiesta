class dbPopulate():
	'''
	populates a database specifically for portage

	'''
	import sqlite3, os

	# Print iterations progress
	def printProgressBar (self, iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
		## https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
		"""
		B{Credit where it's due: https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console}
		Call in a loop to create terminal progress bar
		@params:
			iteration   - Required  : current iteration (Int)
			total       - Required  : total iterations (Int)
			prefix      - Optional  : prefix string (Str)
			suffix      - Optional  : suffix string (Str)
			decimals    - Optional  : positive number of decimals in percent complete (Int)
			length      - Optional  : character length of bar (Int)
			fill        - Optional  : bar fill character (Str)
		"""
		percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
		filledLength = int(length * iteration // total)
		bar = fill * filledLength + '-' * (length - filledLength)
		print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
		# Print New Line on Complete
		if iteration == total:
			print()

	def populateTLD(self,conn, c, pwDict):
		'''
		populates the top level directory table: basically all the directories in /usr/portage
		
		@params conn: The sqlite3 connection
		@params c: The sqlite3 cursor
		@params pwDict: A dictionary containing directory name and the description from the metadata inside
		@return: Nothing

		'''
		c.execute("DROP TABLE IF EXISTS tld;")
		c.execute("CREATE TABLE tld(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, dir_name VARCHAR , description STRING);")

		for key in pwDict:
			desc = pwDict[key]
			if "'" in desc:
				desc = desc.split("'")[0] + chr(8217) + desc.split("'")[1]
			stmnt = "INSERT INTO tld(dir_name, description) VALUES('"+ key +"', '"+ desc+"');"
			# debug print(stmnt)
			c.execute(stmnt)

		conn.commit()

	def getData(self, packageDir, packageName):
		'''
		getData - gets the data for the packages. Needed by populatePackages
		
		@param packageDir: The top level (category) directory e.g.: /usr/portage/app-admin
		@param packageName: The name of the package directory e.g.: /usr/portage/app-admin/qtpass
		@return desc: The description from the ebuild file
		@return hp: The hompage from the ebuild file

		'''

		# want to return description and hompage
		path = packageDir + packageName + '/'
	
		# search in path for a file called pname*ebuild
		for entry in self.os.listdir(path):
			if (self.os.path.isfile(self.os.path.join(path, entry)) and (packageName in entry) and ('ebuild' in entry)) :
				#print(os.path.join(path,entry), packageName, entry)
				with open(path + entry, "r") as f:
					# There's gotto be a cleaner way to do this
					desc = ""
					hp = ""
					g = f.readlines()
					for line in g:
						if "DESCRIPTION=" in line:
							desc =  line.split("DESCRIPTION=")[1]
							desc = desc.rstrip().strip('"')
						elif "HOMEPAGE=" in line:
							hp = line.split("HOMEPAGE=")[1]
							hp = hp.replace("'","")
							hp = hp.rstrip().strip('"')
						
					f.close()
					return desc, hp
	

	def populatePackages(self,conn, c, portDir):
		'''
		populate the packages table
		@param conn: The sqlite3 connection
		@param c: The sqlite3 cursor
		@param portDir: The portage directory (usually /usr/portage
		'''
		listOfPackages = []

		# Create the packages table
		c.execute("DROP TABLE IF EXISTS packages;")
		c.execute("CREATE TABLE packages(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, name VARCHAR, parent INTEGER, description VARCHAR, homepage VARCHAR);")
	
		c.execute("SELECT COUNT(*) FROM tld")
		count=int(c.fetchone()[0]) # Number of entries in the portage dir (/usr/portage)
		i = 0; # iterator for the progress bar
		self.printProgressBar(0, count, prefix = 'Progress:', suffix = 'Complete', length = 50)

		# put package groups into a list
		c.execute("SELECT id,dir_name FROM tld;")
		listOfCategories= c.fetchall() # gives a list of tuples

		for category in listOfCategories:
		
			parentId = category[0] # first entry in tuple is id]
			groupName = category[1] # last enttry is dir name

			path = portDir + category[1] +'/'
		
			for entry in self.os.listdir(path):
				if (self.os.path.isdir(self.os.path.join(path, entry))):
					description, homepage = self.getData(path,entry)

					if description is not None and "'" in description:
						description = description.replace("'",chr(8217))
					elif description is None:
						description = "None"

					if homepage is None:
						description = "None"
				
					c.execute("INSERT INTO packages(name,  parent, description, homepage) VALUES('" + entry + "',"+ str(parentId) + ", '"+description+"', '"+ homepage + "' );")

					
			# 
			conn.commit()
			i+=1
			self.printProgressBar( i , count, prefix = 'Progress:', suffix = 'Complete', length = 50)


if __name__ == "__main__":

	import sqlite3, os
	import portageWalker as PW

	pw = PW.portageWalker()
	dbi = dbPopulate()
	
	HOME = os.environ['HOME']+"/"
	portageDirectory = "/usr/portage/"
	packageGroupDict = pw.tldDict('en')
	con = sqlite3.connect(HOME + 'portwalk.db')
	cur = con.cursor()

	# First - get the package groups
	# and the descriptions
	print("Populating package groups table...")
	dbi.populateTLD(con, cur, packageGroupDict) 

	# Now populate the packages table
	print("Populatong packages table...")
	dbi.populatePackages(con, cur, portageDirectory)

	con.close()
