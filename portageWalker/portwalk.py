#! /usr/bin/env python3

import sys
assert sys.version_info >= (3,4), "Please use Python3.4 or greater."

import configparser, argparse, logging, logging.config
import os, sqlite3
import curses, math

'''
	portwalk - a portage directory walker that pulls the description from the ebuild file.

	OPTIONS:
		All of these can be set in the config file as well
		--log-level
		--language - to change from the defaule 'en'
		--directory - in the unlikely event that the portage directory is not in /usr/portage
		--database - the name of the database to use
		--dbDir - location of the database
		--generate - defaults to False - regenrate the database



'''

def draw_window(stdscr):

	keypress = 0
	dbDir = os.environ['HOME'] + "/" + "portwalk.db"

	# Clear and refresh the screen for a blank canvas
	stdscr.clear()
	stdscr.refresh()

	# Start colors in curses
	curses.start_color()
	curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
	curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
	curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

	minx = 5
	miny = 5
	cursor_x = 5
	cursor_y = 5
	height, width = stdscr.getmaxyx()
	
	con = sqlite3.connect("/home/markw/portwalk.db")
	cur = con.cursor()
	#Get max length of 
	cur.execute("SELECT max(length(dir_name)), COUNT(*) FROM tld;")
	tld_max_length, tld_count = cur.fetchone()
	cols = int(width/(tld_max_length + 5)) # +2 for a buffer
	cur.execute("SELECT dir_name FROM tld ORDER BY dir_name;")
	categories = cur.fetchall()
	stdscr.addstr(0,0,"Navugate to selection and hit <Enter>, Ctrl-x to Exit.", curses.color_pair(3))
		
	while (keypress != 24): # Ctrl-x exits
		
		col = 0
		row = 5
		maxx = 5 + (cols * (tld_max_length + 2))
		tablename = "tld" 
		for category in categories:
			#print(category, type(category))
			stdscr.addstr( row, 5 + col*(tld_max_length +2)   , str(category[0]), curses.color_pair(1))
			if col == cols:
				col = 0
				row += 1
			else:
				col += 1
		maxy = row
		stdscr.refresh()

		if keypress== curses.KEY_DOWN and (((cursor_y -4)* (cols + 1) + ((cursor_x -5)/(tld_max_length +2)) +1) <= tld_count):
			cursor_y = min(cursor_y + 1, maxy)
		elif keypress== curses.KEY_UP:
			cursor_y = max(cursor_y - 1, miny)
		elif keypress== curses.KEY_RIGHT and (((cursor_y -5)* (cols + 1) + ((cursor_x -4)/(tld_max_length +2)) +1) < tld_count):
			cursor_x = min(cursor_x + tld_max_length + 2, maxx)
		elif keypress== curses.KEY_LEFT:
			cursor_x = max(cursor_x - (tld_max_length + 2), minx)
		 
		
		selection = (cursor_y -5)* (cols + 1) + ((cursor_x -5)/(tld_max_length +2)) +1
		stmnt = "SELECT description FROM " + tablename + " WHERE id = " + str(selection)
		cur.execute(stmnt)
		desc = cur.fetchone()
		desc = desc[0].encode('ascii','ignore')
		stdscr.addstr( height -1, 1, str(desc)[:width -2] + " " * (width - len(str(desc)[:width -2]) -2) , curses.color_pair(3))
		stdscr.move(cursor_y, cursor_x)
		# Wait for next input
		keypress = stdscr.getch()

def gui_main():
	curses.wrapper(draw_window)

	
def get_config_values(iDir):

	config = configparser.ConfigParser()
	config.read(iDir+'conf/portwalk.conf')

	return (config['app']['log_level'],config['app']['lang'],config['app']['portDir'], config.getboolean('app','homepage'),\
	 config['database']['name'],config['database']['location'], config.getboolean('app', 'newDB'))

def get_cli_arguments(lvl,lang,dir1,db,dbDir,newDB, hp):

	parser = argparse.ArgumentParser(description='A command line portage browser')
	parser.add_argument("-L", "--log-level", default=lvl,
					help="Set log level (CRITICAL, ERROR, WARNING, INFO, DEBUG)")
	parser.add_argument("-l", "--language", default=lang,
					help="Choose the language you want to use")
	parser.add_argument("-d", "--directory", default=dir1,
					help="Set base directory to search")
	parser.add_argument("-n", "--database", default=db,
					help="Set the name of the database")
	parser.add_argument("-t", "--dbDir", default=dbDir,
					help="Set the target location of the database")
	parser.add_argument('-g', '--generate', default=newDB, action='store_true',
					help="Generate a new database.")
	parser.add_argument('-H', '--homepage', default=hp, action='store_true',
					help="Show homepage in results.")
	parser.add_argument('package', nargs='?',
					help="Specify package name")
	args = parser.parse_args()
	
	return (args.log_level, args.language, args.directory, args.database, args.dbDir, args.generate, args.package, args.homepage)



if __name__ == "__main__":

	# THIS NEEDS TO BE IMPROVED!
	installDir = os.environ['HOME']+"/work/supreme-fiesta/portageWalker/"
	import sys
	sys.path.append(installDir)
	import include.populateDb as dbi, include.portageWalker as PW
	
	# Get some info: CLI arguments override config values
	logLvl, lang, portageDir,hp, db, dbDir, newDB  = get_config_values(installDir)
	if dbDir == "HOME": # Easy way to choose $HOME dir
		dbDir = os.environ['HOME']+"/"
	logLvl, lang, portageDir, dbName, dbDir, newDB, pkg , hp= get_cli_arguments(logLvl, lang, portageDir, db, dbDir, newDB, hp)

	numeric_level = getattr(logging, logLvl.upper(), None)

	# Check the validity of the args
	if not isinstance(numeric_level, int):
		raise ValueError('Invalid log level: %s' % logLvl)


	logging.config.fileConfig(installDir+'conf/portwalk.conf')
	logger = logging.getLogger('portwalk')
	logger.setLevel(numeric_level)
	logger.info("Starting up... Using log level: "+ logLvl +", database: " + db + ", target directory: " + portageDir)

	# First check if a new db is required
	if newDB:
		if not os.path.isdir(portageDir):
			raise ValueError("Directory doesn't exists: %s" % portageDir)

		#db = PW.populateDb
		pw = PW.portageWalker()
		dbi = dbi.dbPopulate()
	
		#HOME = os.environ['HOME']+"/"
		#portageDirectory = "/usr/portage/"
		packageGroupDict = pw.tldDict(lang)
		con = sqlite3.connect(dbDir + dbName)
		cur = con.cursor()

		# First - get the package groups
		# and the descriptions
		print("Populating package groups table...")
		dbi.populateTLD(con, cur, packageGroupDict) 

		# Now populate the packages table
		print("Populatong packages table...")
		dbi.populatePackages(con, cur, portageDir)

		con.close()

	if pkg is not None:
		# I use tab completion, which, if manually browsing through portage dirs
		# leaves a trailing '/'
		# so, for me - I'm going to delete it if it's there
		pkg = pkg.rstrip('/')
		con = sqlite3.connect(dbDir + dbName)
		cur = con.cursor()

		if hp:
			stmnt = "SELECT tld.dir_name, name, packages.description, packages.homepage FROM packages JOIN tld ON packages.parent = tld.id WHERE name = '"+ pkg +"';"
		else:
			stmnt = "SELECT tld.dir_name, name, packages.description FROM packages JOIN tld ON packages.parent = tld.id WHERE name = '"+ pkg +"';"
		cur.execute(stmnt)

		results = cur.fetchall()

		for result in results:
			pretty_result = str(result[0])+"/" + str(result[1]) + ":   " +result[2].rstrip().strip('"')
			print(str(pretty_result))
			if hp :
				print(result[3].rstrip().strip('"'))

		if not results:
			print("Nothing appropriate found for " + pkg)
			print("Please check your spelling, or re-run portwalk with '-g' option to rescan the portage directory")

	else:
		gui_main()	

