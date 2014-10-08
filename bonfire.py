from __future__ import unicode_literals
import evernote.edam.type.ttypes as Types
import evernote.edam.error.ttypes as ErrorTypes
from evernote.api.client import EvernoteClient
import argparse
import sys
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

def create_note_from_clipping(clipping, notebook_guid):
    note = Types.Note()
    note.content = '<?xml version="1.0" encoding="UTF-8"?>'
    note.content += '<!DOCTYPE en-note SYSTEM ' \
                     '"http://xml.evernote.com/pub/enml2.dtd">'
    note.content += '<en-note>'
    note.content += clipping.text
    note.content += '</en-note>'

    note.title = clipping.get_title()
    note.notebookGuid = notebook_guid

    return note

def setup_notebooks(note_store, nb_target):
    notebook_guid = ''
    notebooks = note_store.listNotebooks()
    if nb_target:
        for n in notebooks:
            if n.name == nb_target:
                notebook_guid = n.guid
                break #todo: change it to a more efficient loop
    if notebook_guid=='': # either there isn't any notebook specified, or none was found in search
        try:
            nb = Types.Notebook()
            nb.name = 'Bonfire Clippings'
            notebook_guid = note_store.createNotebook(nb)
        except ErrorTypes.EDAMUserException as e:
            if e.errorCode == 10:
                #welp, there's already notebook named like this, let's get his guid.
                for n in notebooks:
                    if n.name == nb.name:
                        notebook_guid = n.guid
                        break #todo: change it to a more efficient loop
    return notebook_guid
def duplicate(note, note_sotre):
    return False

if __name__ == '__main__':
    aparser = argparse.ArgumentParser()
    aparser.add_argument("-n", "--notebook", help="Target notebook")
    aparser.add_argument("-f", "--force", help="Force target notebook")
    args = aparser.parse_args()
    # TODO: think of other arguments yoou could implement
    client = connect_to_evernote_account('api_info.json')
    user_store = client.get_user_store()
    note_store = client.get_note_store()
    print("Successfully connected to evernote account!")
    target_guid = setup_notebooks(note_store, args.notebook)
    clps = extract_cliipings("res/My Clippings.txt")
    
    success_counter = 0
    cnt = 1
    for clp in clps:
        #todo: check here if the clipping is already in notes
        #sys.stderr.write("\x1b[2J\x1b[H")
        sys.stderr.write("\rCreating " + str(cnt) + " of " + str(len(clps)) + "...")
        sys.stdout.flush()
        try:
            success_counter += 1
            note = create_note_from_clipping(clp, target_guid)
            if not duplicate(note, note_store):
                note_store.createNote(note)
                cnt += 1
        except ErrorTypes.EDAMUserException as e:
            if e.errorCode == 2:
                success_counter -= 1
                print('--debug: malformed data content')
            elif e.errorCode == 11:
                success_counter -= 1
                print('--debug: wtf')
    print("Finished! " + str(success_counter) + " notes created out of " + str(len(clps)) +  " present")
