import sys
assert sys.version_info >= (3,4), "Please use Python3.4 or greater."

import configparser, argparse, logging, logging.config
import os, sqlite3

def get_config_values():

    config = configparser.ConfigParser()
    config.read('conf/portwalk.conf')

    return (config['app']['log_level'],config['app']['lang'],config['app']['portDir'],config['database']['name'],config['database']['location'])

def get_cli_arguments(lvl,lang,dir1,db,dbDir):

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
    parser.add_argument('-g', '--generate', action='store_true',
                    help="Generate a new database.")
    args = parser.parse_args()
    
    return (args.log_level, args.language, args.directory, args.database, args.dbDir, args.generate)



if __name__ == "__main__":

    import include.populateDb as dbi, include.portageWalker as PW
    
    # Get some info CLI arguments override config values
    logLvl, lang, portageDir, db, dbDir  = get_config_values()
    if dbDir == "HOME": # Easy way to choose $HOME dir
        dbDir = os.environ['HOME']+"/"
    logLvl, lang, portageDir, db, dbDir, newDB = get_cli_arguments(logLvl, lang, portageDir, db, dbDir)
    numeric_level = getattr(logging, logLvl.upper(), None)

    # Check the validity of the args
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % logLvl)

    if not os.path.isdir(portageDir):
        raise ValueError("Directory doesn't exists: %s" % portageDir)

    logging.config.fileConfig('conf/portwalk.conf')
    logger = logging.getLogger('generateDB')
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
        con = sqlite3.connect(dbDir + 'portwalk.db')
        cur = con.cursor()

        # First - get the package groups
        # and the descriptions
        print("Populating package groups table...")
        dbi.populateTLD(con, cur, packageGroupDict) 

        # Now populate the packages table
        print("Populatong packages table...")
        dbi.populatePackages(con, cur, portageDir)

        con.close()


        

