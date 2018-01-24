import sqlite3, os
import include.portageWalker as PW

def populateTLD(c, pwDict):
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

def getDescription(pDir, pName):
    path = pDir + pName + '/'
    
    # search in path for a file called pname*ebuild
    for entry in os.listdir(path):
        #print(entry)
        print(os.path.join(path, entry),pName)
        if (os.path.isfile(os.path.join(path, entry)) and (pName in entry) and ('ebuild' in entry)) :
            f = open(path+ '/' + entry, "r")
            g = f.read()
            print(g)
            if "DESCRIPTION" in g:
                print (g)
                return g.split("DESCRIPTION: ")[1]
    

def populatePackages(c, portDir):
    listOfPackages = []

    # Create the packages table
    c.execute("DROP TABLE IF EXISTS packages;")
    c.execute("CREATE TABLE packages(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, name VARCHAR, parent INTEGER, description VARCHAR);")

    # put package groups into a list
    c.execute("SELECT id,dir_name FROM tld;")
    listOfCategories= c.fetchall() # gives a list of tuples

    for category in listOfCategories:
        
        parentId = category[0] # first entry in tuple is id]
        groupName = category[1] # last enttry is dir name

        path = portDir + category[1] +'/'
        
        for entry in os.listdir(path):
            if (os.path.isdir(os.path.join(path, entry))):
                #listOfPackages.append(entry)
                print("INSERT INTO packages(name, parent) VALUES(" + entry + ","+ str(parentId) + ");")
                c.execute("INSERT INTO packages(name, parent) VALUES('" + entry + "',"+ str(parentId) + ");")
            # 
        conn.commit()

    print(listOfPackages)

if __name__ == "__main__":
    pw = PW.portageWalker()
    HOME = os.environ['HOME']+"/"
    portageDirectory = "/usr/portage/"
    packageGroupDict = pw.tldDict('en')
    conn = sqlite3.connect(HOME + 'portwalk.db')
    cur = conn.cursor()

    # First - get the package groups
    # and the descriptions
    populateTLD(cur, packageGroupDict) 

    # Now populate the packages table
    populatePackages(cur,portageDirectory)





conn.close()
