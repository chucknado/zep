import os

from zep.zendesk import Zendesk
from zep.helpers import write_to_json

path = '/api/v2/help_center/incremental/articles.json?start_time={start_time}'

folder_path = os.path.join("..", "cache", "guide", "source")
handoff_path = os.path.join("..", "cache", "guide", "handoff")
file_paths = glob.glob(os.path.join(folder_path, '*.html'))

files = []
for file_path in file_paths:
    files.append(os.path.basename(file_path)[:-5])

ditamap = read_from_yml(os.path.join("..", "cache", "_ditamap", "ditamap.yml"))
for item in ditamap:
    if item['dita'] in files:
        src = os.path.join(folder_path, item['dita'] + '.html')
        dst = os.path.join(handoff_path, str(item['id']) + '.html')
        shutil.copyfile(src, dst)
        files.remove(item['dita'])

# copy any leftover files with the dita filename
for file in files:
    src = os.path.join(folder_path, file + '.html')
    dst = os.path.join(handoff_path, file + '.html')
    shutil.copyfile(src, dst)
