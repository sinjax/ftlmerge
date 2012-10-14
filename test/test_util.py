from ftlmerge import util
from ftlmerge import merge
import tempfile

def test_readprofsav():
	loc = "/Users/ss/Library/Application Support/FasterThanLight/prof.sav"
	profsav = util.ProfSav()
	profsav.read(loc)

def test_writeprofsav():
	loc = "/Users/ss/Library/Application Support/FasterThanLight/prof.sav"
	profsav = util.ProfSav()
	profsav.read(loc)
	temp = tempfile.NamedTemporaryFile()
	try:
		profsav.write(temp.name)
		fwritten = file(temp.name)
		forig = file(loc)
		writLines = fwritten.readlines()
		origLines = forig.readlines()
		assert writLines == origLines
		# for i in range(len(writLines)):
		# 	print writLines[i]
		# 	print "VS"
		# 	print origLines[i]
		# 	print writLines[i] == origLines[i]
	finally:
		# Automatically cleans up the file
		temp.close()
	pass

def test_merge():
	loc1 = "test/prof-1.sav"
	loc2 = "test/prof-2.sav"
	merged = merge.merge(util.ProfSav(loc1),util.ProfSav(loc2))
	merged.write("test/prof-1-2-merged.sav")

	pass