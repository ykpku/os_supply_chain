import os.path
import gzip
from pprint import pprint

from utils.json import load_file
from utils.csv import CsvUtility
from utils.xml import XMLParser

from download_file.download_repomd import download_repo_metadata


def look_pkg_prop_info(xml_file, column):
    xml_root = XMLParser.gz_parsefile(xml_file, 0)
    if xml_root is None:
        return

    print(len(xml_root['metadata']['package']), type(xml_root['metadata']['package']), xml_root['metadata'].keys(), xml_root['metadata']['package'][0])

    column_set = set([])
    for i in xml_root['metadata']['package']:
        if column in i:
            if isinstance(i[column], str):
                column_set.add(i[column])
            elif isinstance(i[column], dict):
                for j in i[column].keys():
                    column_set.add(j)
    return column_set


def __repomd_get_primary_file(os_path, repomd_path='repodata/repomd.xml'):
    repo_cont = XMLParser.parsefile(os.path.join(os_path, repomd_path).replace("\\", "/"))
    for i in repo_cont['repomd']['data']:
        if i['@type'] == 'primary':
            return i['location']['@href']
    return None


def get_os_pkgprop(os_arch_ver, override=False):
    metas = load_file('../os_urls.json')
    column_contend = set([])
    for os_name, os_arch, os_ver in os_arch_ver:
        for os_k, os_url in metas[os_name].items():
            os_path, os_files = download_repo_metadata(os_url.format(arch=os_arch, ver=os_ver), "../data/CACHEDIR/", override)
            primary_file = __repomd_get_primary_file(os_path)
            if primary_file:
                print(os.path.basename(os_path), "=======YES========")
                ## property init ##
                column_contend.update(look_pkg_prop_info(os.path.join(os_path, primary_file).replace('\\', '/'), 'format'))
            else:
                print(os.path.basename(os_path), "=======NO========")
    print(column_contend)


if __name__ == '__main__':
    os_versions = [
        ("openEuler", "x86_64", "openEuler-22.03-LTS-SP1"),
        # ("openEuler", "aarch64", "openEuler-22.03-LTS-SP1"),
        # ("openEuler", "x86_64", "openEuler-23.03"),
        # ("openEuler", "aarch64", "openEuler-23.03"),
        # ("fedora", "x86_64", "38"),
        # ('fedora', 'aarch64', '38'),
        # ('anolis', 'x86_64', '8.8'),
        # ('anolis', 'aarch64', '8.8'),
        # # ('anolis', 'loongarch64', '8.8'),
        # ('centos', 'x86_64', '7'),
        # ('openCloudOS', 'x86_64', '8'),
        # ('openCloudOS', 'aarch64', '8')
    ]
    get_os_pkgprop(os_versions, False)
    pass