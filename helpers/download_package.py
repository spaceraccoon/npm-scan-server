import os
import requests
import shutil
import sys
import tarfile

REGISTRY_URL = 'https://registry.npmjs.org/'

def download(package_name, package_version, file_path):
    r = requests.get('{}{}/-/{}-{}.tgz'.format(REGISTRY_URL, package_name, package_name, package_version))
    open(file_path, 'wb').write(r.content)

def extract(package_name, package_version, file_path):
    dest = '{}-{}'.format(package_name, package_version)
    tar = tarfile.open(file_path)
    tar.extractall(dest)
    tar.close()
    files_list = os.listdir(os.path.join(dest, 'package'))
    for files in files_list:
        src = os.path.join(dest, 'package', files)
        shutil.move(src, dest)
    os.rmdir(os.path.join(dest, 'package'))
    os.remove(file_path)

if __name__ == '__main__':
    file_path = '{}-{}.tgz'.format(sys.argv[1], sys.argv[2])
    download(sys.argv[1], sys.argv[2], file_path)
    extract(sys.argv[1], sys.argv[2], file_path)