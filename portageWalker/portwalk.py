#! /usr/bin/env python3.6

import sys
assert sys.version_info >= (3,4), "Please use Python3.4 or greater."

import configparser, argparse, logging, logging.config
import os, sqlite3

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
def get_config_values(iDir):

    config = configparser.ConfigParser()
    config.read(iDir+'conf/portwalk.conf')

    return (config['app']['log_level'],config['app']['lang'],config['app']['portDir']\
    ,config['database']['name'],config['database']['location'], config.getboolean('app', 'newDB') )

def get_cli_arguments(lvl,lang,dir1,db,dbDir,newDB):

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
    parser.add_argument('package', nargs='?',
                    help="Specify package name")
    args = parser.parse_args()
    
    return (args.log_level, args.language, args.directory, args.database, args.dbDir, args.generate, args.package)



if __name__ == "__main__":

    # THIS NEEDS TO BE IMPROVED!
    installDir = os.environ['HOME']+"/work/supreme-fiesta/portageWalker/"
    import sys
    sys.path.append(installDir)
    import include.populateDb as dbi, include.portageWalker as PW
    
    # Get some info: CLI arguments override config values
    logLvl, lang, portageDir, db, dbDir, newDB  = get_config_values(installDir)
    if dbDir == "HOME": # Easy way to choose $HOME dir
        dbDir = os.environ['HOME']+"/"
    logLvl, lang, portageDir, dbName, dbDir, newDB, pkg = get_cli_arguments(logLvl, lang, portageDir, db, dbDir, newDB)

    numeric_level = getattr(logging, logLvl.upper(), None)

    # Check the validity of the args
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % logLvl)

    if not os.path.isdir(portageDir):
        raise ValueError("Directory doesn't exists: %s" % portageDir)

    logging.config.fileConfig(installDir+'conf/portwalk.conf')
    logger = logging.getLogger('portwalk')
    logger.setLevel(numeric_level)
    logger.info("Starting up... Using log level: "+ logLvl +", database: " + db + ", target directory: " + portageDir)

    # First check if a new db is required
    if newDB:
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

        stmnt = "SELECT tld.dir_name, name, packages.description FROM packages JOIN tld ON packages.parent = tld.id WHERE name = '"+ pkg +"';"
        cur.execute(stmnt)

        results = cur.fetchall()
        for result in results:
            pretty_result = str(result[0])+"/" + str(result[1]) + ":   " +result[2].rstrip().strip('"')
            print(str(pretty_result))

        

