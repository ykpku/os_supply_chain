import os
from pprint import pprint

from utils.xml import XMLParser


def type_or_error(c, t, e):
    if c is None:
        return None
    if isinstance(c, t):
        return c
    print(f"====={e} error====")
    pprint(c)
    return None


class PkgProps(object):
    def __init__(self, os_name, os_arch, os_ver, os_k, os_url, os_path, primary_file):
        self.prop_info = None
        self.pkg_num = None
        self.os_name = os_name
        self.os_arch = os_arch
        self.os_ver = os_ver
        self.os_k = os_k
        self.os_url = os_url
        self.os_path = os_path
        self.primary_file_name = primary_file
        self.prop_header = ['index_id', 'type', 'pkgId', 'name', 'arch', 'version', 'epoch', 'release', 'summary', 'description', 'url', 'time_file', 'time_build', 'rpm_license', 'rpm_vendor', 'rpm_group', 'rpm_buildhost', 'rpm_sourcerpm', 'rpm_header_start', 'rpm_header_end', 'rpm_packager', 'size_package', 'size_installed', 'size_archive', 'location_href', 'checksum_type']

        self.get_pkg_prop_info()

    def get_pkg_prop_info(self):
        xml_file = os.path.join(self.os_path, self.primary_file_name).replace('\\', '/')
        xml_root = XMLParser.gz_parsefile(xml_file, 0)
        if xml_root is None or 'metadata' not in xml_root or '@packages' not in xml_root['metadata'] or 'package' not in xml_root['metadata']:
            print("====xml data key error====")
            return
        self.pkg_num = xml_root['metadata']['@packages']
        if self.pkg_num <= 0:
            print("====xml data pkg num error====")
            return
        self.prop_info = {}
        for p in xml_root['metadata']['package']:
            p_contend = {}
            p_contend['type'] = self.__get_prop_type(p)
            p_contend['name'] = self.__get_prop_name(p)
            p_contend['arch'] = self.__get_prop_arch(p)
            e, v, r = self.__get_prop_version(p)
            p_contend['version'] = v
            p_contend['epoch'] = e
            p_contend['release'] = r
            checksum, pkgid = self.__get_prop_checksum(p)
            p_contend['checksum_type'] = checksum
            p_contend['pkgId'] = pkgid
            p_contend['summary'] = self.__get_prop_summary(p)
            p_contend['description'] = self.__get_prop_description(p)
            p_contend['rpm_packager'] = self.__get_prop_packager(p)
            p_contend['url'] = self.__get_prop_url(p)
            tf, tb = self.__get_prop_time(p)
            p_contend['time_file'] = tf
            p_contend['time_build'] = tb
            si, sa, sp = self.__get_prop_size(p)
            p_contend['size_installed'] = si
            p_contend['size_archive'] = sa
            p_contend['size_package'] = sp
            p_contend['location_href'] = self.__get_location(p)
            rpm_license, rpm_vendor, rpm_group, rpm_buildhost, rpm_sourcerpm, rpm_headerstart, rpm_headerend = self.__get_format(p)
            p_contend['rpm_license'] = rpm_license
            p_contend['rpm_vendor'] = rpm_vendor
            p_contend['rpm_group'] = rpm_group
            p_contend['rpm_buildhost'] = rpm_buildhost
            p_contend['rpm_sourcerpm'] = rpm_sourcerpm
            p_contend['rpm_header_start'] = rpm_headerstart
            p_contend['rpm_header_end'] = rpm_headerend
            self.prop_info[self._pkg_id_generator(p_contend)] = p_contend
        pass

    @staticmethod
    def _pkg_id_generator(p_contend):
        if p_contend['epoch'] != "0":
            pkg_id = p_contend['name'] + "-" + p_contend['epoch'] + ":" + p_contend['version'] + "-" + p_contend[
                'release'] + "." + p_contend['arch']
            return pkg_id
        pkg_id = p_contend['name'] + "-" + p_contend['version'] + "-" + p_contend['release'] + "." + p_contend['arch']
        return pkg_id

    @staticmethod
    def __get_prop_type(contend):
        return type_or_error(contend['@type'], str, "prop type")

    @staticmethod
    def __get_prop_name(contend):
        return type_or_error(contend['name'], str, "prop name")

    @staticmethod
    def __get_prop_arch(contend):
        return type_or_error(contend['arch'], str, "prop arch")

    @staticmethod
    def __get_prop_version(contend):
        epoch = type_or_error(contend['version']['@epoch'], str, "prop version epoch")
        version = type_or_error(contend['verison']['@ver'], str, "prop version ver")
        release = type_or_error(contend['version']['@rel'], str, "prop version release")
        return epoch, version, release

    @staticmethod
    def __get_prop_checksum(contend):
        checksum_type = type_or_error(contend['checksum']['@type'], str, "prop checksum type")
        pkgId = type_or_error(contend['checksum']['#text'], str, "prop checksum pkgid")
        return checksum_type, pkgId

    @staticmethod
    def __get_prop_summary(contend):
        return type_or_error(contend['summary'], str, "prop summary")

    @staticmethod
    def __get_prop_description(contend):
        return type_or_error(contend['description'], str, "prop description")

    @staticmethod
    def __get_prop_packager(contend):
        return type_or_error(contend['packager'], str, "prop packager")

    @staticmethod
    def __get_prop_url(contend):
        return type_or_error(contend['url'], str, "prop url")

    @staticmethod
    def __get_prop_time(contend):
        time_file = type_or_error(contend['time']['@file'], str, "prop time file")
        time_build = type_or_error(contend['time']['@build'], str, "prop time build")
        return time_file, time_build

    @staticmethod
    def __get_prop_size(contend):
        size_installed = type_or_error(contend['size']['@installed'], str, "prop size install")
        size_archive = type_or_error(contend['size']['@archive'], str, "prop size archive")
        size_package = type_or_error(contend['size']['@package'], str, "prop size package")
        return size_installed, size_archive, size_package

    @staticmethod
    def __get_location(contend):
        return type_or_error(contend['location']['href'], str, "prop location")

    @staticmethod
    def __get_format(contend):
        rpm_license = type_or_error(contend['format']['rpm:license'], str, "prop format license")
        rpm_vendor = type_or_error(contend['format']['rpm:vendor'], str, "prop format vendor")
        rpm_group = type_or_error(contend['format']['rpm:group'], str, "prop format rpmgroup")
        rpm_buildhost = type_or_error(contend['format']['rpm:buildhost'], str, "prop format rpmbuildhost")
        rpm_sourcerpm = type_or_error(contend['format']['rpm:sourcerpm'], str, "prop format rpmsourcerpm")
        rpm_headerstart = type_or_error(contend['format']['rpm:header-range']['@start'], str, "prop format header start")
        rpm_headerend = type_or_error(contend['format']['rpm:header-range']['@end'], str, "prop format header end")
        return rpm_license, rpm_vendor, rpm_group, rpm_buildhost, rpm_sourcerpm, rpm_headerstart, rpm_headerend







