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

if __name__ == "__main__":
    pw = PW.portageWalker()
    HOME = os.environ['HOME']+"/"
    pwDict1 = pw.tldDict('en')
    conn = sqlite3.connect(HOME + 'portwalk.db')
    cur = conn.cursor()
    populateTLD(cur, pwDict1)





conn.close()
