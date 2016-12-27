
import re
import logging

class Filter():
    @classmethod
    def filter_version(cls, version_list, version):
        versions = []

        if version in version_list:
            versions.append(version)

        return versions

    @classmethod
    def filter_major_version(cls, version_list, version):
        versions = []

        version_pattern = '^({})\.{{1}}(\d+)\.?(\d?)'.format(version)
        pattern = re.compile(version_pattern)

        for entry in version_list:
            if pattern.match(entry):
                versions.append(entry)

        return versions

    @classmethod
    def filter_latest(cls, version_list):
        version_pattern = '^(\d+)\.{1}(\d+)\.?(\d?)'
        pattern = re.compile(version_pattern)
        versions = []

        for entry in version_list:
            if pattern.match(entry):
                versions.append(entry)

        highest_version = sorted(versions)[-1]

        return [highest_version]

    @classmethod
    def filter_intersection(cls, input_versions, filtered_versions):
        intersect_versions = []

        for major_version in filtered_versions:
            version_pattern = '^({})\.{{1}}(\d+)\.?(\d?)'.format(major_version)
            pattern = re.compile(version_pattern)

            for full_version in input_versions:
                if pattern.match(full_version):
                    intersect_versions.append(full_version)

        return intersect_versions
