import logging
import os
import iso.config
import iso.url
import sys
import hashlib
import re

class File():
    @classmethod
    def iso_exists(cls, full_version, distribution):
        logger = logging.getLogger('logger')
        file_url = iso.url.Url.file_url_generator(full_version, distribution, cls.get_download_dest)

        logger.debug('Full file path: %s', file_url)

        file_exists = os.path.isfile(file_url)

        logger.debug('File exists result: %s', file_exists)

        return file_exists

    @classmethod
    def get_download_dest(cls, stds_data, dist_data):
        file_name = stds_data[dist_data['version']]['image_name'].format(**dist_data)

        file_data = {
            'image_url': stds_data[dist_data['version']]['dest'],
            'file_name': file_name
        }

        return file_data

    @classmethod
    def get_checksum_dest(cls, stds_data, dist_data):
        file_name = stds_data[dist_data['version']]['checksum_file']

        file_data = {
            'image_url': stds_data[dist_data['version']]['dest'],
            'file_name': file_name
        }

        return file_data

    @classmethod
    def add_iso_checksum(cls, full_version, distribution, image_url):
        logger = logging.getLogger('logger')
        version_info = full_version.split('.')
        conf = iso.config.Config()
        distro_stds = conf.config['iso_naming_stds'][distribution]
        checksum_type = distro_stds[version_info[0]]['checksum_type']

        file_url = iso.url.Url.file_url_generator(full_version, distribution, cls.get_checksum_dest)

        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY

        try:
            file_handle = os.open(file_url, flags)
            os.close(file_handle)
        except FileExistsError as e:
            pass

        try:
            hash_generator = hashlib.new(checksum_type)

            with open(image_url, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_generator.update(chunk)

            hash_sum = hash_generator.hexdigest()
            image_name = os.path.basename(image_url)

            output = []
            hash_regex = '^.*{}$'.format(image_name)
            hash_matcher = re.compile(hash_regex)
            line_separator = os.linesep

            logger.debug("Checksum: %s", hash_sum)
            logger.debug("Checksum file %s of size %s", file_url, os.stat(file_url).st_size)

            with open(file_url, "r+") as f:
                add_new_line = True

                for line in f:
                    line = line.rstrip()
                    if hash_matcher.match(line):
                        add_new_line = False
                        new_hash_line = '{} *{}'.format(hash_sum, image_name)
                        output.append(new_hash_line)
                    else:
                        output.append(line)

                if add_new_line:
                    new_hash_line = '{} *{}'.format(hash_sum, image_name)
                    output.append(new_hash_line)

                f.seek(0)
                f.write(line_separator.join(output))
        except Exception as e:
            logger.error(str(e))
            sys.exit(3)
