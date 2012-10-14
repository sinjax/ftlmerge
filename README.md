So,

The story is that I have had to travel around fo European projects a bit recently.
This meant that I have been playing "FTL":http://www.ftlgame.com/ a lot on my laptop and while at home playing on my desktop.

Because I didn't think, having been spoilt by Steam's awesome game save sharing goodness, I didn't bother "symlinking the prof.sav file":http://www.ftlgame.com/forum/viewtopic.php?f=7&t=2172 to a shared Dropbox folder.

So, because I was a little ill this morning and because it was Sunday and because I was interested I wrote this python code to let you read/write the prof.sav file format (Thanks mainly "to this guide":http://ftlwiki.com/wiki/Prof.sav). Then I wrote some code to merge multiple prof.sav files.

The merging tries to maintain the order of entries like high score lists, ship high score lists and so on but I think the game's reading code is actually quite rohbust. I say this because the diff of the merged file I create and the same file once the game had loaded it once are, well, different! Which means this library should help you merge FTL save states... but is clearly still making files slightly differently to the game itself.

Anyway, usage:

	ftlmerge_tool.py prof.sav.1 prof.sav.2 ... prof.sav.n prof.sav.output

The code lacks comment and style, but it works so feel free to tidy/have a play

Enjoy!
