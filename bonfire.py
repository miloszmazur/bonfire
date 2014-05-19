DELIMITER = "=========="


class Clipping(object):
    #note: type is currently Highlight, Bookmark or Clipping. Dunno if i should bother with bookmarks
    def __init__(self, source, type_and_loc, date_added, text):
        self.source = source
        self.type_and_loc = type_and_loc
        self.date_added = date_added
        self.text = text

    def __str__(self):
        return "A " + self.type_and_loc + " from " + self.source + ' ' + self.date_added + '\n' + self.text


def extract_cliipings(clippings_file):
    clips = open(clippings_file, 'r').read().split(DELIMITER)
    for clip in clips:
        clip = [item for item in clip.split("\n") if item is not '']
        if clip:
            source = clip[0]  # a book/article/whatever from which clipping is taken
            about = clip[1].split(' | ')  # type [& page] | location | date
            type_and_loc = about[0].strip('- ')
            if len(about) == 3:  # i.e. a clipping is not from a book
                type_and_loc = type_and_loc + ' ' + about[1]
                date_added = about[2]
            else:
                date_added = about[1]
            try:
                text = clip[2]
            except IndexError:  # bookmark - currently not sending these
                continue
            c = Clipping(source, type_and_loc, date_added, text)
            print(c)


if __name__ == '__main__':
    extract_cliipings("res/My Clippings.txt")


