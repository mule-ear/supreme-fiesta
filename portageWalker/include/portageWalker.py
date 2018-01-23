class portageWalker:
    import os
    def __init__(self):
        self.portageDir = "/usr/portage/"
        self.language = "en"
        self.exclude = ("distfiles", "eclass", "licenses", "metadata", "profiles", "scripts")
        self.categories = {}

    def getTopLevel(self,directory):

        topLevel = []
        for entry in self.os.listdir(directory):
            if (self.os.path.isdir(self.os.path.join(directory, entry)) and (entry not in self.exclude)):
                topLevel.append(entry)

        topLevel.sort()
        return topLevel

    def getMetadata(self,portage, topLevelDir, lang):
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
            

    def getSubdirs(self,directory):
        pass
    #    for entry in os.listdir(directory):
        

    def tldDict(self,lang,portDir="/usr/portage/"):
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
