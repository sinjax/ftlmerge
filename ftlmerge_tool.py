#!/usr/bin/env python
from ftlmerge import merge
from ftlmerge import util
import sys
def main():
	if len(sys.argv) < 3:
		print "Usage: python ftlmerge input-prof1.sav input-prof1.sav ... output.sav"
		return
	merged = merge.merge(*[util.ProfSav(inp) for inp in sys.argv[1:-1]])
	merged.write(sys.argv[-1])
if __name__ == '__main__':
	main()