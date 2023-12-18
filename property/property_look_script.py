from utils.xml import XMLParser


def look_primary_file(xml_file):
    xml_root = XMLParser.parsefile(xml_file)
    if xml_root is None:
        return None, None, None, None


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
    look_primary_file()
    pass