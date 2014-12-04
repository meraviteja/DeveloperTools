import os
import shutil
from os import path
from shutil import make_archive
from shutil import copytree
import zipfile
from zipfile import ZipFile
import sys, getopt
import subprocess
from subprocess import call, STDOUT
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment


#configurable properties, Assuming this is the right location, make sure the .git file exists
gitLocation = ''
serverToDeploy = 'http://localhost:4502'
credentials = "admin:admin"
#End of configurable properties

#not so configurable property, this is for debugging
debug = False


#This is where all the magic beings

#cleans new line charecters from a string if it is toolong
def cleanString(row):
    row = row.replace("\n","")
    return row

currentLocation = os.environ['deploycq']

if currentLocation:
	index = currentLocation.find('build.py')
	#strip off build.py for creating a folder structure
	if  index != -1:
		 currentLocation = cleanString(currentLocation[:index])
else:
	print 'please setup your bash profile or windows environment variable to BUILD_SCRIPT to your /build.py location'
	sys.exit()

# if you dont specify the git location on the top i take your current directory as a git directory
if not gitLocation:
	gitLocation = os.getcwd()

#checking if the current lcocation is a valid git repository
if call(["git", "branch"], stderr=STDOUT, stdout=open(os.devnull, 'w')) != 0:
	print("You are not in a valid git repository")
	sys.exit()

#location of jcr_root
copylocation = cleanString(currentLocation + "buildstructure/jcr_root")
#if jcr_root doesnt exist on the folderstructure
if not os.path.exists(copylocation):
    os.makedirs(copylocation)
#location of filter
filterlocation = cleanString(currentLocation+"/buildstructure/META-INF/vault/filter.xml")

#List of files changes, and filters for those files
filterList = list()

def main(argv):
	os.chdir(gitLocation)
	
	listOfChangedfiles = subprocess.check_output(["git", "diff", "--name-only"])
	listOfUntrackedfiles = subprocess.check_output(["git", "ls-files" , "--exclude-standard", "--others"])
	allChanges = listOfChangedfiles + listOfUntrackedfiles
	listFiles =  allChanges.split()
	if  argv:
		try:
			opts, args = getopt.getopt(argv,"i:s:c:",["ifile=","ofile="])
		except getopt.GetoptError:
			print '-i or -s or -c are the only valid argument, example: python build.py -i pull -s {serverToDeploy} -c {credentials}'
			sys.exit(2)
		for opt, arg in opts:
			if opt == '-i':
				inputArg = arg
				if arg == 'pull':
					listOfChangedfiles = subprocess.check_output(["git", "diff", "--name-only","@{1}.."])
					listFiles =  listOfChangedfiles.split()
				else:
					print 'invalid argugment for -i'
			elif opt == '-s':
				global serverToDeploy
				serverToDeploy = arg
			elif opt == '-c':
				global credentials
				credentials = arg
			else:
				print '-i or -s or -c are the only valid argument, example: python build.py -i pull -s {serverToDeploy} -c {credentials}' 


	#print 'i have a new argument' + argv
	#listOfChangedfiles = subprocess.check_output(["git", "diff", "--name-only","@{1}.."])
	#listFiles =  listOfChangedfiles.split()

	if  listFiles:
		os.chdir(copylocation)
		for path in listFiles:
			makeDirectoryStructure(cleanString(gitLocation+"/"+path))	
		#create filter
		createFilter()
		#zip files and call it deploy.zip	
		zipArchive()
		#deploy it to localhost
		deploy()
		#delete archive form local
		deleteArchive()
	else:
		print 'no changed files detected , exiting process'
		sys.exit()

#make the directory Structure for the changed files
def makeDirectoryStructure(originalPath):
	index = originalPath.find('jcr_root')
	#strip everything after jcr_root 
	if  index != -1:
		 strippedPath = originalPath[index+8:len(originalPath)]
		 #create filter list
		 filterList.append(strippedPath)
		 #create and copy file
		 ensure_dir(originalPath,strippedPath)
	else:
		if debug:
			print "The file structure doesnt have jcr, left for future bundle deploys"
			 

#update filter.xml
def createFilter():
	print "These are the list of files deployed"
	tree = ET.parse(filterlocation)
	parent = tree.getroot()
	comment = Comment('Generated for fitlter list')
	parent.append(comment)
	root = ET.Element("workspaceFilter")
	root.set("version","1.0")	
	for path in filterList:
		print path 
		doc = ET.SubElement(root, "filter")
		#for xml's go one step above and create a filter
		if ".xml" in path:
			doc.set("root",os.path.dirname(path))
			doc.set("mode","update")
		else:
			doc.set("root",path)	
	tree = ET.ElementTree(root)
	tree.write(filterlocation)
	
	
#create folder structure and then copy file over	
def ensure_dir(originalPath,strippedPath):
    newCopiedPath = copylocation+os.path.dirname(strippedPath)
    if not os.path.exists(newCopiedPath):
        os.makedirs(newCopiedPath)
    shutil.copy2(originalPath,newCopiedPath)   

def zipArchive():
	    # now put things into a ZIP archive  
    zipAtLocation = cleanString(currentLocation + "/buildstructure")
    shutil.make_archive("archive", "zip",zipAtLocation)
    if debug:
    	print "here is the zip location ===>" + zipAtLocation

#deploy to local host
def deploy():
	protocal = "curl"
	param1 = "-u"
	force = "-F"
	zipLocation = cleanString("file=@"+copylocation+"/"+"archive.zip")
	param2 = "name=deployScript"
	param3 = "force=true"
	install = "install=true"	
	urlDeploy = cleanString(serverToDeploy + "/crx/packmgr/service.jsp")
	
	deployStatus = subprocess.check_output([protocal,param1,credentials,force,zipLocation,force,param2,force,param3,force,install,urlDeploy])
	if debug:
		print deployStatus
	
#delete archive that was temporarily created
def deleteArchive():
	folder_path = copylocation
	#Remove Archive.zip first
	os.remove(cleanString(copylocation+'/archive.zip'))
	#Remove files if any under jcr_root

	#remove folders
	if not debug:
		for file_object in os.listdir(folder_path):
			file_object_path = os.path.join(folder_path, file_object)
			if os.path.isfile(file_object_path):
				os.remove(file_object_path)
			elif os.path.isdir(file_object_path):
				shutil.rmtree(file_object_path)
			

if __name__ == '__main__':
	main(sys.argv[1:])
