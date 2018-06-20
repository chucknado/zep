import os
import glob

from zep.helpers import create_tree, get_id_from_filename, rewrite_file


def strip_classic(handoff, write=True):
    handoff.verify_handoff_exists()

    print('\n')
    file_path = os.path.join(handoff.handoff_folder, 'articles')
    files = glob.glob(os.path.join(file_path, '*.html'))
    for file in files:
        if get_id_from_filename(file) == 203661526:        # voice pricing article - don't modify this file
            continue

        tree = create_tree(file)
        count = 0
        # delete notes enclosed in <div class='p'> tag
        p_divs = tree.find_all('div', 'p')
        for p_div in p_divs:
            if p_div.span and p_div.span.string is not None and 'Classic:' in p_div.span.string:
                notes = p_div.find_all('div', 'note note')
                for note in notes:
                    if note.span and 'Classic:' in note.span.string:
                        note.decompose()
                        count += 1
        # delete notes not enclosed in <div class='p'> tag (if any missed)
        notes = tree.find_all('div', 'note note')
        for note in notes:
            if note.span and note.span.string is not None and 'Classic:' in note.span.string:
                note.decompose()
                count += 1
        # after deleting span-tag notes, delete notes one level higher than span tags
        note_divs = tree.find_all('div', 'note note')
        for note in note_divs:
            if note.string and 'Zendesk Classic:' in note.string:
                note.decompose()
                count += 1
        # clean up empty p divs
        pdiv_count = 0
        for p_div in p_divs:
            if p_div.string is None and p_div.find(True) is None:
                p_div.decompose()
                pdiv_count += 1

        if count == 0:      # no changes made
            continue
        if write:
            rewrite_file(file, tree)

        print('Removed {} Classic notes in {}'.format(count, os.path.basename(file)))
