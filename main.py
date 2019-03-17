import os
import shutil
import schedule
import requests
import tarfile
import time
import subprocess
import argparse

parser = argparse.ArgumentParser(description='npm-scan on a server.', prog='npm-scan-server')
parser.add_argument('-l', '--log', help='Log scans', default=False, action='store_true')
args = parser.parse_args()

updated = str(int(time.time() * 1000))
SKIMDB_URL = 'https://skimdb.npmjs.com/registry/_design/app/_list/index/modified'
REGISTRY_URL = 'https://registry.npmjs.org/'

def extract(updated, package_name, package_version, file_path):
    dest = os.path.join('packages', updated, '{}-{}'.format(package_name, package_version))
    tar = tarfile.open(file_path)
    tar.extractall(dest)
    tar.close()
    files_list = os.listdir(os.path.join(dest, 'package'))
    for files in files_list:
        src = os.path.join(dest, 'package', files)
        shutil.move(src, dest)
    os.rmdir(os.path.join(dest, 'package'))
    os.remove(file_path)

def download(package_name, package_version, file_path):
    r = requests.get('{}{}/-/{}-{}.tgz'.format(REGISTRY_URL, package_name, package_name, package_version))
    open(file_path, 'wb').write(r.content)

def scan():
    global updated
    print(updated)
    r = requests.get(SKIMDB_URL, params={'startkey': updated})
    data = r.json()

    if len(data) > 1:
        for key, value in data.items():
            if key != '_updated':
                print(key)
                print(updated)
                if not os.path.isdir(os.path.join('packages', updated)):
                    os.makedirs(os.path.join('packages', updated))
                file_path = os.path.join('packages', updated, '{}-{}.tgz'.format(key, value['dist-tags']['latest']))
                download(key, value['dist-tags']['latest'], file_path)
                extract(updated, key, value['dist-tags']['latest'], file_path)
        if not os.path.isdir('output'):
            os.mkdir('output')
        subprocess.run(['node', 'npm-scan/bin/scan', '-p', os.path.join('packages', updated), '-o', os.path.join('output', '{}.json'.format(updated))])
        shutil.rmtree(os.path.join('packages', updated))

        if args.log:
            for key, value in data.items():
                if key != '_updated':
                    open('log.txt', 'a+').write('{}@{}\n'.format(key, value['dist-tags']['latest']))

    updated = str(data['_updated'])

if __name__ == '__main__':
    schedule.every(10).seconds.do(scan)

    while True:
        schedule.run_pending()
        time.sleep(1)
