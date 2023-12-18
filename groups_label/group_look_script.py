import os
from pprint import pprint

from utils.json import load_file
from utils.csv import CsvUtility
from utils.xml import XMLParser

from group_label import download_repo_metadata, get_groups_info, __repomd_get_group_file, __groupinfo_packageinfo, __merge_package_info


def look_euler_groups():
    group_package = load_file("C:/Users/smile/Desktop/workspace/os-supplychain/out_data/GroupPackages.json")
    print(len(group_package))
    for i in group_package:
        print(i['name'])
    package_set = set([])
    for i in group_package:
        package_set.update(set(i['dependencies']))
    print(len(package_set))


def look_RPM_group(props_file):
    pkg_pros = CsvUtility.read_norm_array_csv("C:/Users/smile/Desktop/workspace/os-supplychain/out_data/" + props_file + ".csv")
    pkg_names_set = set([])
    for i in pkg_pros[1:]:
        if len(i) > 4:
            pkg_names_set.add(i[4])
        elif len(i) > 0:
            pkg_l = i[0].split("-")
            pkg_names_set.add("-".join(pkg_l[:-2]))
            # print(i[0], ":", "-".join(pkg_l[:-2]))
    print("package number: ", len(pkg_names_set))

    pkg_pros = CsvUtility.read_norm_array_csv("C:/Users/smile/Desktop/workspace/os-supplychain/out_data/" + props_file + ".csv")
    pkg_rpmgroup_set = set([])
    for i in pkg_pros[1:]:
        if len(i) == len(pkg_pros[0]):
            pkg_rpmgroup_set.add(i[16])
    if 'Unspecified' in pkg_rpmgroup_set:
        pkg_rpmgroup_set.remove('Unspecified')
    if 'BSD' in pkg_rpmgroup_set:
        pkg_rpmgroup_set.remove('BSD')
    if 'GPLv3' in pkg_rpmgroup_set:
        pkg_rpmgroup_set.remove('GPLv3')
    print("RPM group num : ", len(pkg_rpmgroup_set))
    for i in pkg_rpmgroup_set:
        print(i)
    count = 0
    for i in pkg_pros:
        if len(i) > 15:
            if i[16] in pkg_rpmgroup_set:
                count += 1
    print("package with RPM group: ", count)


def look_custom_group(group_file):
    group_package = CsvUtility.read_norm_array_csv(
        "C:/Users/smile/Desktop/workspace/os-supplychain/out_data/" + group_file + ".csv")
    gs, cs, es = set([]), set([]), set([])
    pkgs = set([])
    flag = -1
    for i in group_package:
        if i[0].startswith("<group>"):
            flag = 0
        elif i[0].startswith("<category>"):
            flag = 1
        elif i[0].startswith("<environment>"):
            flag = 2
        if i[0].startswith('<name xml:lang="zh_CN">'):
            if flag == 0:
                gs.add(i[0][23:-7])
            elif flag == 1:
                cs.add(i[0][23:-7])
            elif flag == 2:
                es.add(i[0][23:-7])
        if i[0].startswith("<packagereq type=") and flag == 0:
            isp = i[0].split(">")[1]
            pkgs.add(isp.split("<")[0])

    print("group, category, environment, package with group: ", len(gs), len(cs), len(es), len(pkgs))
    print("-----Group------")
    print(gs)
    print("-----Category------")
    print(cs)
    print("-----Environment-----")
    print(es)
    return gs, cs, es, pkgs


def common_custom_group(file_list):
    group_dict = {}
    for group_file in file_list:
        gs, cs, es, pkgs = look_custom_group(group_file)
        for g in gs:
            if g in group_dict:
                group_dict[g].append(group_file)
            else:
                group_dict[g] = [group_file]
    # common group
    g_count = [[], [], [], [], []]
    for g in group_dict:
        g_count[len(group_dict[g]) - 1].append(g)
    print(group_dict.keys())
    print(len(group_dict))
    for i in range(1, len(g_count)):
        print(len(g_count[i]))
        print(g_count[i])


def look_oskg_pros(filename, column_num):
    pkg_pros = CsvUtility.read_norm_array_csv(
        "C:/Users/smile/Desktop/workspace/os-supplychain/out_data/" + filename + ".csv")
    ret_set = {}
    for item in pkg_pros[1:]:
        if len(item) == len(pkg_pros[0]):
            if item[column_num] in ret_set:
                ret_set[item[column_num]] += 1
            else:
                ret_set[item[column_num]] = 1
    sort_ret = sorted(ret_set.items(), key=lambda x: x[1], reverse=True)
    pprint(sort_ret if len(sort_ret) < 10 else sort_ret[:10])
    print(len(sort_ret))


def __compare_dict(d1, d2):
    print("查看字典d1和字典d2相同的键:", len(d1.keys() & d2.keys()))
    # pprint(d1.keys() & d2.keys())
    print("查看字典d1 - 字典d2的键:")
    pprint(d1.keys() - d2.keys())
    print("查看字典d2 - 字典d1的键:")
    pprint(d2.keys() - d1.keys())

    for ck in d1.keys() & d2.keys():
        print("=======comparing common ",  ck, "=======")
        if d1[ck]['default'] != d2[ck]['default']:
            print("default diff: ", d1[ck]['default'], d2[ck]['default'])
        if " ".join(d1[ck]['description']) != " ".join(d2[ck]['description']):
            print("description diff: ", " ".join(d1[ck]['description']), " ".join(d2[ck]['description']))
        if " ".join(d1[ck]['name']) != " ".join(d2[ck]['name']):
            print("name diff: ", " ".join(d1[ck]['name']), " ".join(d2[ck]['name']))
        if d1[ck]['uservisible'] != d2[ck]['uservisible']:
            print("uservisible diff: ", d1[ck]['uservisible'], d2[ck]['uservisible'])

        if len(set(d1[ck]['packagelist']) ^ set(d2[ck]['packagelist'])) > 0:
            print("packagelist diff: ")
            pprint(set(d1[ck]['packagelist']) - set(d2[ck]['packagelist']))
            pprint(set(d2[ck]['packagelist']) - set(d1[ck]['packagelist']))


def compare_os_intern_groups(os_arch_ver, override=False):
    metas = load_file('../os_urls.json')
    base_gs = None
    for os_name, os_arch, os_ver in os_arch_ver:
        for os_k, os_url in metas[os_name].items():
            os_path, os_files = download_repo_metadata(os_url.format(arch=os_arch, ver=os_ver), "../data/CACHEDIR/", override)
            group_file = __repomd_get_group_file(os_path)
            if group_file:
                print(os.path.basename(os_path), "=======YES========")
                os_gs, os_cate, os_env, os_langp = get_groups_info(os.path.join(os_path, group_file).replace('\\', '/'))
                if os_gs is not None:
                    if base_gs is None:
                        base_gs = os_gs
                    else:
                        __compare_dict(base_gs, os_gs)
                        # if len(os_gs) > len(base_gs):
                        #     base_gs = os_gs
            else:
                print(os.path.basename(os_path), "=======NO========")


def __look_package_info(pkg_info):
    if pkg_info is None:
        print("========pkg info none error======")
        return
    print("pkg num : ", len(pkg_info))
    pkg_sort = sorted(pkg_info.items(), key=lambda x: len(x[1].keys()), reverse=True)
    print("group top 10 packages:")
    pprint(pkg_sort[:10])
    pkg_gs_count = {}
    for pkg, gs in pkg_info.items():
        gs_count = len(gs)
        if gs_count not in pkg_gs_count:
            pkg_gs_count[gs_count] = 1
        else:
            pkg_gs_count[gs_count] += 1
    print("groups count:")
    pprint(pkg_gs_count)


def __compare_package_info(pkgs_1, pkgs_2):
    pkgs_1_gs, pkgs_2_gs = set([]), set([])
    for _, gsinfo in pkgs_1.items():
        for gk in gsinfo.keys():
            pkgs_1_gs.add(gk)
    for _, gsinfo in pkgs_2.items():
        for gk in gsinfo.keys():
            pkgs_2_gs.add(gk)

    common_pkgs = set(pkgs_1.keys()) & set(pkgs_2.keys())
    if len(common_pkgs) == 0:
        print("no common packages.")
        print("===========================")
        return
    print("common package num: ", len(common_pkgs))
    for cpkg in common_pkgs:
        groups1 = set(pkgs_1[cpkg].keys())
        groups2 = set(pkgs_2[cpkg].keys())

        if len(groups1 & groups2) != len(groups1):
            print("common package groups diff: ", cpkg)
            print("g1 - g2 : ", groups1 - groups2)
            if len(groups1 - groups2) > 0:
                for g1minusg2 in (groups1 - groups2):
                    if g1minusg2 in pkgs_2_gs:
                        print("####", cpkg, groups1, groups2, g1minusg2)
            print("g2 - g1 : ", groups2 - groups1)
            if len(groups2 - groups1) > 0:
                for g2minusg1 in (groups2 - groups1):
                    if g2minusg1 in pkgs_1_gs:
                        print("####", cpkg, groups1, groups2, g2minusg1)
            print("---------------------------")
    print("==========================")


def compare_os_intern_packages(os_arch_ver, override=False):
    metas = load_file('../os_urls.json')
    base_os_ver_pkgs = None
    for os_name, os_arch, os_ver in os_arch_ver:
        os_ver_pkgs = None
        for os_k, os_url in metas[os_name].items():
            os_path, os_files = download_repo_metadata(os_url.format(arch=os_arch, ver=os_ver), "../data/CACHEDIR/", override)
            group_file = __repomd_get_group_file(os_path)
            if group_file:
                print(os.path.basename(os_path), "=======YES========")
                os_gs, os_cate, os_env, os_langp = get_groups_info(os.path.join(os_path, group_file).replace('\\', '/'))
                if os_gs is not None:
                    os_url_pkgs = __groupinfo_packageinfo(os_gs)
                    if os_ver_pkgs is None:
                        os_ver_pkgs = os_url_pkgs
                    else:
                        os_ver_pkgs = __merge_package_info(os_ver_pkgs, os_url_pkgs)
            else:
                print(os.path.basename(os_path), "=======NO========")
        __look_package_info(os_ver_pkgs)
        if base_os_ver_pkgs is None:
            base_os_ver_pkgs = os_ver_pkgs
        else:
            __compare_package_info(base_os_ver_pkgs, os_ver_pkgs)


if __name__ == '__main__':

    # look_RPM_group("oskg_pros_20231027112449")
    # look_custom_group("anolis_groups")
    #
    # fl = ["openEuler_groups", "fedora_groups", "centos_groups", "openCloudOS_groups", "anolis_groups"]
    # common_custom_group(fl)

    os_versions = [
        ("openEuler", "x86_64", "openEuler-22.03-LTS-SP1"),
        # ("openEuler", "aarch64", "openEuler-22.03-LTS-SP1"),
        # ("openEuler", "x86_64", "openEuler-23.03"),
        # ("openEuler", "aarch64", "openEuler-23.03"),
        ("fedora", "x86_64", "38"),
        # ('fedora', 'aarch64', '38'),
        # ('anolis', 'x86_64', '8.8'),
        # ('anolis', 'aarch64', '8.8'),
        # ('anolis', 'loongarch64', '8.8'),
        # ('centos', 'x86_64', '7'),
        # ('openCloudOS', 'x86_64', '8'),
        # ('openCloudOS', 'aarch64', '8')
    ]

    # compare_os_intern_groups(os_versions, False)
    # look_oskg_pros("oskg_pros_20231027112449", 29)
    compare_os_intern_packages(os_versions, False)
    pass
