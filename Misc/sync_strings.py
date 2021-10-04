import os
import xml.etree.ElementTree as ET
import xml.dom.minidom as MD


def register_all_namespaces(filename):
    namespaces = dict(
        [node for _, node in ET.iterparse(filename, events=['start-ns'])])
    for ns in namespaces:
        ET.register_namespace(ns, namespaces[ns])


def file_to_dict(filename):
    with open(filename, "r", encoding='utf8') as f:
        src_etree = ET.parse(f)
    return {child.get('{http://schemas.microsoft.com/winfx/2006/xaml}Key'): child.text for child in src_etree.getroot()[:]}


def dict_to_file(filename, dict):
    with open(filename, "w", encoding='utf8') as f:
        f.write('<ResourceDictionary xmlns="https://github.com/avaloniaui"\n')
        f.write(
            '                    xmlns:system="clr-namespace:System;assembly=mscorlib"\n')
        f.write(
            '                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">\n')
        last_section = None
        for key in sorted(dict.keys()):
            try:
                section = key[:key.index('.')]
            except ValueError:
                section = key
            if last_section != section:
                f.write('\n')
            last_section = section
            line = '  <system:String x:Key="%s">%s</system:String>\n' % (
                key, dict[key])
            f.write(line)
        f.write('</ResourceDictionary>\n')


if __name__ == "__main__":
    dir = os.path.dirname(os.path.abspath(__file__))
    dir = os.path.join(dir, "../OpenUtau.App/Strings/")
    lang_files = os.listdir(dir)
    src_file = next(filter(lambda f: f.endswith("Strings.axaml"), lang_files))
    src_file = os.path.join(dir, src_file)
    dst_files = filter(lambda f: not f.endswith("Strings.axaml"), lang_files)
    dst_files = map(lambda f: os.path.join(dir, f), dst_files)

    register_all_namespaces(src_file)
    dict = file_to_dict(src_file)
    dict_to_file(src_file, dict)

    for dst_file in dst_files:
        dst_dict = file_to_dict(dst_file)
        to_remove = set(dst_dict.keys()) - set(dict.keys())
        to_add = set(dict.keys()) - set(dst_dict.keys())
        [dst_dict.pop(k) for k in to_remove]
        [dst_dict.update({k: dict[k]}) for k in to_add]
        dict_to_file(dst_file, dst_dict)
