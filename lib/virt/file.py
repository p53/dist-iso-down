import logging
import os
import iso.config

class File():
    @classmethod
    def get_virt_image_name(cls, full_version, distribution, virt_type):
        logger = logging.getLogger('logger')
        version_info = full_version.split('.')
        conf = iso.config.Config()
        distro_stds = conf.config['iso_naming_stds'][distribution]

        distro_data = {
            'full_version': full_version,
            'distribution': distribution,
            'version': version_info[0],
            'arch': distro_stds[version_info[0]]['arch'],
            'update': version_info[1],
            'virt_type': virt_type
        }

        if len(version_info) == 3:
            distro_data['stamp_version'] = version_info[2]
            distro_data['dot'] = '.'
        else:
            distro_data['stamp_version'] = ""
            distro_data['dot'] = ""

        virt_image_format = conf.config['virtualizations'][virt_type]['format']
        virt_image_name = distro_stds[distro_data['version']]['virt_image_name'].format(**distro_data)

        logger.debug('Virtual image name %s', virt_image_name)

        return virt_image_name

    @classmethod
    def virt_image_exists(cls, full_version, distribution, virt_type):
        logger = logging.getLogger('logger')
        version_info = full_version.split('.')
        conf = iso.config.Config()
        distro_stds = conf.config['iso_naming_stds'][distribution]

        virt_image_name = cls.get_virt_image_name(full_version, distribution, virt_type)

        virt_image_format = conf.config['virtualizations'][virt_type]['format']
        virt_type_packer_dir = conf.config['virtualizations'][virt_type]['folder']

        packer_directory = '{}/{}'.format(virt_type_packer_dir, virt_image_name)
        virt_full_image_name = "{}.{}".format(virt_image_name, virt_image_format)

        logger.debug('Created image name: %s', virt_full_image_name)

        file_data = {
            'dest': distro_stds[version_info[0]]['dest'],
            'virt_full_image_name': virt_full_image_name,
            'packer_directory': packer_directory
        }

        file_url = '{dest}/{packer_directory}/{virt_full_image_name}'.format(**file_data)

        logger.debug('Full file path: %s', file_url)

        file_exists = os.path.isfile(file_url)

        logger.debug('File exists result: %s', file_exists)

        return file_exists

    @classmethod
    def get_generate_dest(cls, full_version, distribution):
        version_info = full_version.split('.')
        conf = iso.config.Config()
        distro_stds = conf.config['iso_naming_stds'][distribution]

        distro_data = {
            'full_version': full_version,
            'distribution': distribution,
            'version': version_info[0],
            'arch': distro_stds[version_info[0]]['arch'],
            'update': version_info[1]
        }

        if len(version_info) == 3:
            distro_data['stamp_version'] = version_info[2]
            distro_data['dot'] = '.'
        else:
            distro_data['stamp_version'] = ""
            distro_data['dot'] = ""

        file_url = distro_stds[distro_data['version']]['dest'].format(**distro_data)

        return file_url
