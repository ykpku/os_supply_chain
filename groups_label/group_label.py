import os.path
from pprint import pprint

from utils.json import load_file
from utils.csv import CsvUtility
from utils.xml import XMLParser

from download_file.download_repomd import download_repo_metadata


def __get_descrip(des_list):
    if des_list is None:
        return ["", ""]
    if type(des_list) is str:
        return [des_list, ""]
    if type(des_list) is list:
        engstr = ""
        chstr = ""
        for des_i in des_list:
            if type(des_i) is str:
                engstr += des_i
            elif type(des_i) is dict:
                if des_i["@xml:lang"] == "zh_CN":
                    chstr += des_i["#text"]
            else:
                pprint("=======des_i error=========")
                pprint(des_i)
        return [engstr, chstr]
    pprint("=======des_list error=========")
    pprint(des_list)
    return None


def __get_name(name_list):
    # if name_list is None:
    #     return ["", ""]
    if type(name_list) is str:
        return [name_list, ""]
    if type(name_list) is list:
        engstr = ""
        chstr = ""
        for name_i in name_list:
            if type(name_i) is str:
                engstr += name_i
            elif type(name_i) is dict:
                if name_i["@xml:lang"] == "zh_CN":
                    chstr += name_i["#text"]
            else:
                pprint("=======name_i error=========")
                pprint(name_i)
        return [engstr, chstr]
    pprint("=======name_list error=========")
    pprint(name_list)
    return None


def __get_group_packs(pack_dict):
    if pack_dict is None:
        return {}
    if not(type(pack_dict) is dict and len(pack_dict.keys()) == 1 and "packagereq" in list(pack_dict.keys())):
        pprint("==========packagereq key error==========")
        pprint(pack_dict)
    pack_ret = {}
    if type(pack_dict["packagereq"]) is dict:
        pack_ret[pack_dict["packagereq"]['#text']] = pack_dict["packagereq"]['@type']
        return pack_ret
    if type(pack_dict["packagereq"]) is list:
        for pack_i in pack_dict["packagereq"]:
            pack_ret[pack_i['#text']] = pack_i['@type']
        return pack_ret
    pprint("==========packagereq value error==========")
    pprint(pack_dict["packagereq"])
    return None


def __get_groups(grouplist, group_val, init_groupdict=None):
    if type(grouplist['groupid']) is str:
        if init_groupdict is None:
            return {grouplist['groupid']: group_val}
        else:
            init_groupdict[grouplist['groupid']] = group_val
    elif type(grouplist['groupid']) is list:
        if init_groupdict is None:
            return {g: group_val for g in grouplist['groupid']}
        else:
            for g in grouplist['groupid']:
                if type(g) is str:
                    init_groupdict[g] = group_val
                elif type(g) is dict and '#text' in g.keys():
                    init_groupdict[g['#text']] = group_val
                else:
                    print('========item of group list error=========')
                    print(g)
    else:
        pprint("==========grouplist error==========")
        pprint(grouplist)
    return init_groupdict


def get_groups_info(xml_file):
    xml_root = XMLParser.parsefile(xml_file)
    if xml_root is None:
        return None, None, None, None
    if 'comps' in xml_root and type(xml_root['comps']) is dict:
        print(xml_root['comps'].keys())
        for ks in xml_root['comps'].keys():
            print(ks, ": ", len(xml_root['comps'][ks]))
    else:
        return None, None, None, None

    # pprint(xml_root['comps']['group'][0]['name'])
    # pprint(xml_root['comps']['category'][0])
    # pprint(xml_root['comps']['environment'][0])
    # pprint(xml_root['comps']['langpacks'])

    os_groups, os_cate, os_env, os_langp = None, None, None, None
    if 'group' in xml_root['comps']:
        os_groups = {}
        gslist = []
        if type(xml_root['comps']['group']) is list:
            gslist = xml_root['comps']['group']
        elif type(xml_root['comps']['group']) is dict:
            gslist = [xml_root['comps']['group']]
        else:
            print("==========groups list error=============")
            pprint(xml_root['comps']['group'])
        for i in gslist:
            group_contend = {}
            group_contend['default'] = i['default']
            group_contend['description'] = __get_descrip(i['description'])
            group_contend['name'] = __get_name(i['name'])
            group_contend['packagelist'] = __get_group_packs(i['packagelist'])
            group_contend['uservisible'] = i['uservisible']
            os_groups[group_contend['name'][0]] = group_contend
    if 'category' in xml_root['comps']:
        os_cate = {}
        for i in xml_root['comps']['category']:
            cate_contend = {}
            cate_contend['description'] = __get_descrip(i['description'])
            cate_contend['name'] = __get_name(i['name'])
            cate_contend['grouplist'] = __get_groups(i['grouplist'], 'grouplist')
            if 'optionlist' in i:
                cate_contend['grouplist'] = __get_groups(i['optionlist'], 'optionlist', cate_contend['grouplist'])
            os_cate[cate_contend['name'][0]] = cate_contend
    if 'environment' in xml_root['comps']:
        os_env = {}
        for i in xml_root['comps']['environment']:
            env_contend = {}
            if 'description' in i:
                env_contend['description'] = __get_descrip(i['description'])
            env_contend['name'] = __get_name(i['name'])
            if 'grouplist' in i:
                env_contend['grouplist'] = __get_groups(i['grouplist'], 'grouplist')
            if 'optionlist' in i:
                env_contend['grouplist'] = __get_groups(i['optionlist'], 'optionlist', env_contend['grouplist'])
            os_env[env_contend['name'][0]] = env_contend

    return os_groups, os_cate, os_env, os_langp


def __repomd_get_group_file(os_path, repomd_path='repodata/repomd.xml'):
    repo_cont = XMLParser.parsefile(os.path.join(os_path, repomd_path).replace("\\", "/"))
    for i in repo_cont['repomd']['data']:
        if i['@type'] == 'group':
            return i['location']['@href']
    return None


def __groupinfo_packageinfo(os_groups):
    os_grouped_packages = {}
    for (gk, gkc) in os_groups.items():
        for (pkg, pkg_opt) in gkc['packagelist'].items():
            if pkg in os_grouped_packages:
                if gk not in os_grouped_packages[pkg]:
                    os_grouped_packages[pkg][gk] = pkg_opt
                else:
                    print("========package info error=============")
                    print(pkg, gk, pkg_opt, os_grouped_packages[pkg][gk])
            else:
                os_grouped_packages[pkg] = {gk: pkg_opt}
    return os_grouped_packages


def __merge_package_info(ori_pkgs, new_pkgs):
    for pkg, gs_info in new_pkgs.items():
        if pkg not in ori_pkgs:
            ori_pkgs[pkg] = gs_info
        else:
            for g, opt in gs_info.items():
                if g not in ori_pkgs[pkg]:
                    ori_pkgs[pkg][g] = opt
                elif ori_pkgs[pkg][g] != opt:
                    print("========option error=========")
                    print(pkg, g, ori_pkgs[pkg][g], opt)
                else:
                    pass
    return ori_pkgs


def get_os_groups(os_arch_ver, override=False):
    metas = load_file('../os_urls.json')
    for os_name, os_arch, os_ver in os_arch_ver:
        for os_k, os_url in metas[os_name].items():
            os_path, os_files = download_repo_metadata(os_url.format(arch=os_arch, ver=os_ver), "../data/CACHEDIR/", override)
            group_file = __repomd_get_group_file(os_path)
            if group_file:
                print(os.path.basename(os_path), "=======YES========")
                os_groups, os_cate, os_env, os_langp = get_groups_info(os.path.join(os_path, group_file).replace('\\', '/'))
            else:
                print(os.path.basename(os_path), "=======NO========")


if __name__ == '__main__':

    # fl = ["openEuler_groups", "fedora_groups", "centos_groups", "openCloudOS_groups", "anolis_groups"]
    # for f in fl:
    #     print(f)
    #     get_groups_info(f)

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
    get_os_groups(os_versions, False)
    pass
