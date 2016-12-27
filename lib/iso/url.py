import iso.config

class Url():
    @classmethod
    def file_url_generator(cls, full_version, distribution, func):
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

        file_data = func(distro_stds, distro_data)

        file_url = '{image_url}/{file_name}'.format(**file_data)

        return file_url
