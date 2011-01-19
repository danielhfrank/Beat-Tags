'''
Created on Jan 15, 2011

@author: dan
'''

import sys
import getopt
import os
import eyeD3


TEST = False

        
class BeatnessExtractor:         
            
    def after_slash(self, input):
        ''' Tennis / Marathon --> Marathon'''
        return self._afterSep(input, "/")
    
    def before_slash(self, input):
        ''' Tennis / Marathon --> Tennis'''
        return self._beforeSep(input, "/")
    
    def before_dash(self, input):
        ''' Tennis - Marathon --> Tennis'''
        return self._beforeSep(input, "-")
    
    def after_dash(self, input):
        ''' Tennis - Marathon --> Marathon'''
        return self._afterSep(input, "-")
    
    def just_fix_it(self, input):
        ''' Used if you just want to get rid of leading 02. or something like that'''
        return input
            
    
    def _beforeSep(self, input, sep):
        splitted = input.split(sep)
        if (len(splitted) < 2):
            print "There must be a problem, that separator ain't there"
            sys.exit(2)
        return splitted[0]
    
    def _afterSep(self, input, sep):
        splitted = input.split(sep)
        if (len(splitted) < 2):
            print "There must be a problem, that separator ain't there"
            sys.exit(2)
        return splitted[1]

class Main:

    artistFxn = None
    albumFxn = None
    titleFxn = None        
    offsetAmnt = 0
    capitalize = False
    numbers = False
    
    def getTagFromSong(self, song):
        de_bug("Going to work on song: " + song)
        audioFile = eyeD3.Mp3AudioFile(song)
        tag = audioFile.getTag()
                
        #Deal with one bug we encountered - eyeD3 evidently incapable of handling v2.2, so just switch to v2.3
        if tag.getVersion() == 33:
            tag.setVersion(34)
        return tag
    
    def getATitle(self, tag, song):
        title = str(tag.getTitle())
        de_bug("In song " + song + " got this title from tag: " + title)
        return title if (title not in ("", " ", None)) else song
    
    def firstAlpha(self, input):
        for x in range(len(input)):
            if input[x].isalpha(): return x
        return -1
        
    def doTrackNumbers(self, tags, titles):
        '''Assumes that titles start with track numbers, and that the tags match up with the titles'''
        for tag, title in zip(tags, titles):
            tag.setTrackNum((title[:self.firstAlpha(title)], str(len(titles))))
        
    
    def main(self, argv):

        
        eyeD3Map = {"artistFxn":"setArtist", "albumFxn":"setAlbum", "titleFxn":"setTitle"}

        try:
            opts, args = getopt.getopt(argv, "a:A:t:o:hnC", ["artist=", "album=", "title=", "offset=", "help"]) 
        except getopt.GetoptError:
            usage()
            sys.exit(2)
            
        for opt, arg in opts:
            if(opt in ("-a", "--artist")):
                self.artistFxn = arg
            if(opt in ("-A", "--album")):
                self.albumFxn = arg
            if(opt in ("-t", "--title")):
                self.titleFxn = arg
            if(opt in ("-o", "--offset")):
                self.offsetAmnt = int(arg)
            if(opt == "-n"):
                self.numbers = True
            if(opt == "-C"):
                self.capitalize = True
            if(opt in ("-h", "--help")):
                usage()
                sys.exit(1)
    
        dir = "." if (len(args) == 0) else args[0] #mm is it size()?
        songs = filter(eyeD3.isMp3File, map(lambda x: dir + os.sep + x, os.listdir(dir)))
        tags = map(self.getTagFromSong, songs)
        songs = map(lambda song: song[len(dir) + 1:-4], songs)#remove dir and extension, way easier to do here
        de_bug("These are our songs: " + str(songs))
        
        titles = map(self.getATitle, tags, songs)
        
        de_bug("OK these are our titles: " + str(titles))
        
        #First, try to deal with weird case where we have something like [01] Ten Cent Pistol
        if all(not (title[0].isalpha() or title[0].isdigit()) for title in titles):
            titles = map(lambda x: x[1:], titles)
            
        
        if (len(filter(lambda x: x[0].isdigit(), titles)) * 1.25) >= len(titles) :
            #most of the songs appear to start with a number, so try to remove leading numbers and, for that matter, all the other shit
            #WARNING- This will lop off legitimate leading numbers in tracks if they are preceeded by track number. Sorry I'm not sorry
            #Also, executive decision: if we find these numbers, they're right, and we're using em
            self.doTrackNumbers(tags, titles)
            titles = map(lambda x: x[self.firstAlpha(x):], titles)
        
        for title, tag in zip(titles, tags):

                
#            origTitle = str(tag.getTitle())
#            if(origTitle in (None, "", " ")):
#                # beat title, switch to name of file. (As in VU)
#                de_bug("Beat title, switching to filename")
#                origTitle = song[len(dir) + 1:-4]#remove the dir and the extension
#                
#                
#            #Handle track numbers before doing offset
#            if self.numbers: 
#                tag.setTrackNum((origTitle[:2], str(len(tagsAndSongs))))
#                #hopefully this will deal with exceptions the way we want if for some reason numbers aren't present
#            
#            origTitle = origTitle[self.offsetAmnt:]
            
            de_bug("In big loop, this is the title we're working with: " + title)
            
            if(self.capitalize):
                title = " ".join(map(lambda x: x.capitalize(), title.split(" ")))
                
            #now apply the functions -- this is going to require me to learn introspection
            
            be = BeatnessExtractor()
            for fxnName in eyeD3Map.keys() :
                fxn = getattr(self, fxnName)
                if fxn != None:
                    if callable(getattr(be, fxn)):
                        de_bug("Ready to fix shit, we've got fxn = " + str(fxn) + " and I don't know what else we can say...")
                        eyeD3fxn = getattr(tag, eyeD3Map[fxnName])
                        eyeD3fxn(getattr(be, fxn)(title))
                    else:
                        print fxn + "isn't a valid function, sry"
                        sys.exit(2)
            
            tag.update()
            
            print "Beatness resolved!"
        
        


def usage():
    '''This is going to print directions, like what command line arguments to use'''
    print " \
    Here are the command line flags you can use. Also supply directory as final argument, or else current will be assumed\n \
    -a or --artist ... function to get artist \n \
    -A or --album ... function to get album\n \
    -t or --title ... you get it\n\
    -C captialize.. the song names. and the artists?\n \
    \nThese are the functions that you can use for artist, track etc: documented by example\n \
    "
    be = BeatnessExtractor()
    methodList = [method for method in dir(be) if callable(getattr(be, method))]
    for method in filter(lambda x: str(x)[0] != "_", methodList):
        print str(method) + " " + str(getattr(be, method).__doc__) + "\n"
    
#        -o ... offset. This is the total number of chars to skip at the beginning for crap like 02 - ...\n \
#    -n Numbers -- takes the first two chars and tries to read as the track number\n \

def de_bug(msg):
    if TEST:
        print msg
    else:
        pass


if __name__ == '__main__':
    m = Main()
    m.main(sys.argv[1:])