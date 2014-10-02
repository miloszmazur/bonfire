from __future__ import unicode_literals
import evernote.edam.type.ttypes as Types
import evernote.edam.error.ttypes as ErrorTypes
from evernote.api.client import EvernoteClient
DELIMITER = "=========="


class Clipping(object):
    #note: type is currently Highlight, Bookmark or Clipping. Dunno if i should bother with bookmarks
    def __init__(self, source, type_and_loc, date_added, text):
        self.source = source
        self.type_and_loc = type_and_loc
        self.date_added = date_added
        self.text = text

    def __str__(self):
        return "A " + self.type_and_loc + " from " + self.source + ' ' + self.date_added + self.text

    def __repr__(self):
        return "A " + self.type_and_loc + " from " + self.source + ' ' + self.date_added + self.text

    def get_title(self):
        return self.source + ' (' + self.date_added + ')'


def extract_cliipings(source):
    clippings = []
    clips_file = open(source, 'r').read().split(DELIMITER)
    for clip in clips_file:
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
            except IndexError:  # bookmark/whatever,  currently not archiving these
                continue
            clippings.append(Clipping(source, type_and_loc, date_added, text))
    return clippings
def connect_to_evernote_account(api_info_file):
    import json
    info = json.loads(open(api_info_file).read())
    client = EvernoteClient(token=info["token"], sandbox=True)
    return client

def create_note_from_clipping(clipping):
    note = Types.Note()
    note.content = '<?xml version="1.0" encoding="UTF-8"?>'
    note.content += '<!DOCTYPE en-note SYSTEM ' \
                     '"http://xml.evernote.com/pub/enml2.dtd">'
    note.content += '<en-note>'
    note.content += clipping.text
    note.content += '</en-note>'

    note.title = clipping.get_title()

    return note


if __name__ == '__main__':
    client = connect_to_evernote_account('api_info.json')
    user_store = client.get_user_store()
    note_store = client.get_note_store()
    print("Successfully connected to evernote account!")
    notebooks = note_store.listNotebooks()
    for notebook in notebooks:
        print(notebook.name)

    clps = extract_cliipings("res/My Clippings.txt")

    for clp in clps:
        #todo: check here if the clipping is already in notes 
        print ('creating note from ' + str(clp)+ ' ...' )
        try:
            note_store.createNote(create_note_from_clipping(clp))
        except ErrorTypes.EDAMUserException as e:
            if e.errorCode == 2:
                print('--debug: malformed data content')
            elif e.errorCode == 11:
                print('--debug: wtf')
