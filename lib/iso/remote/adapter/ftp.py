import ftplib
import re
import logging
import os
import sys
import iso.file
import virt.file
import subprocess
import shlex
from pattern.singleton import Singleton
import iso.config
import iso.url
import socket
import time

class FTP(metaclass=Singleton):
    ftp = ""

    def __init__(self, ftp_host):
        ftp = ftplib.FTP()
        ftp.connect(ftp_host)
        ftp.login()
        self.ftp_host = ftp_host
        self.ftp = ftp

    def __del__(self):
        logger = logging.getLogger('logger')
        try:
            self.ftp.quit()
        except ftplib.error_temp as exc:
            logger.debug(str(exc))

    def relogin(self):
        self.__init__(self.ftp_host)

    def get_filename(self, stds_data, dist_data):
        image_url = stds_data.get(dist_data['version'])['iso_url'].format(**dist_data)
        file_name = stds_data.get(dist_data['version'])['image_name'].format(**dist_data)

        file_data = {
            'image_url': image_url,
            'file_name': file_name
        }

        return file_data

    def get_checksum_filename(self, stds_data, dist_data):
        image_url = stds_data.get(dist_data['version'])['iso_url'].format(**dist_data)
        file_name = stds_data.get(dist_data['version'])['checksum_file']

        file_data = {
            'image_url': image_url,
            'file_name': file_name
        }

        return file_data

    def set_releases_location(self, release_folder):
        self.ftp.cwd(release_folder)
        self.release_folder = release_folder

    def get_files(self):
        ls = []
        self.ftp.retrlines('LIST', ls.append)

        return ls

    def get_versions(self, entry_list):
        versions = []

        version_pattern = '^(\d+)\.{1}(\d+)\.?(\d?)'
        pattern = re.compile(version_pattern)
        split_pattern = re.compile('\s+')

        for entry in entry_list:
            entry_info = split_pattern.split(entry)

            if pattern.match(entry_info[8]):
                versions.append(entry_info[8])

        return versions

    def iso_exists(self, full_version, distribution):
        logger = logging.getLogger('logger')

        file_url = iso.url.Url.file_url_generator(full_version, distribution, self.get_filename)

        logger.debug('FTP file path: %s', file_url)

        try:
            logger.debug('Checking if we are logged to FTP by PWD command')
            self.ftp.pwd()
        except ftplib.error_temp as exc:
            logger.debug('Trying relogin')
            self.relogin()
            self.set_releases_location(self.release_folder)

        try:
            logger.debug('FTP current working dir: %s', self.ftp.pwd())
            logger.debug('FTP file url: %s', file_url)
            self.ftp.size(file_url)
            logger.debug('File exists on ftp: %s', 'True')

            return True
        except Exception as exc:
            logger.debug("Some exception occured: %s", str(exc))
            logger.debug('File exists on ftp: %s', 'False')

            return False

    def get_iso_http_url(self, full_version, distribution):
        version_info = full_version.split('.')

        file_url = iso.url.Url.file_url_generator(full_version, distribution, self.get_filename)

        file_data = {
            'schema': 'http://',
            'host': self.ftp.host,
            'release_folder': self.ftp.pwd(),
            'file_url': file_url
        }

        http_url = '{schema}{host}{release_folder}/{file_url}'.format(**file_data)

        return http_url

    def get_checksum_http_url(self, full_version, distribution):
        version_info = full_version.split('.')

        file_url = iso.url.Url.file_url_generator(full_version, distribution, self.get_checksum_filename)

        file_data = {
            'schema': 'http://',
            'host': self.ftp.host,
            'release_folder': self.ftp.pwd(),
            'file_url': file_url
        }

        http_url = '{schema}{host}{release_folder}/{file_url}'.format(**file_data)

        return http_url

    def download_on(self, check_function, check_versions, distribution):
        logger = logging.getLogger('logger')

        for full_version in check_versions:
            check_result = check_function(full_version, distribution)
            ftp_file_exists = self.iso_exists(full_version, distribution)

            if (not check_result) and ftp_file_exists:
                file_url = iso.url.Url.file_url_generator(full_version, distribution, self.get_filename)
                down_dest = iso.url.Url.file_url_generator(full_version, distribution, iso.file.File.get_download_dest)

                logger.debug('Download source: %s', file_url)
                logger.debug('Download destination: %s', down_dest)

                ftp_down_cmd = 'RETR {}'.format(file_url)

                logger.info('Starting download of %s', file_url)
                self.ftp.retrbinary(ftp_down_cmd, open(down_dest, 'wb').write)
                logger.info('Download finished: %s', file_url)

                logger.info('Calculating checksum of %s', file_url)
                iso.file.File.add_iso_checksum(full_version, distribution, down_dest)
                logger.info('Calculating checksum finished: %s', file_url)
            else:
                logger.info("Skipping generation, already downloaded or not present on remote: %s", full_version)

    def generate(self, check_versions, virt_types, distribution):
        logger = logging.getLogger('logger')
        conf = iso.config.Config()
        packer_stds = conf.config['packer']
        distro_stds = conf.config['iso_naming_stds'][distribution]

        for full_version in check_versions:
            check_result = virt.file.File.virt_image_exists(full_version, distribution, virt_types[0])
            ftp_file_exists = self.iso_exists(full_version, distribution)

            if (not check_result) and ftp_file_exists:
                http_url = self.get_iso_http_url(full_version, distribution)
                http_checksum_url = self.get_checksum_http_url(full_version, distribution)
                down_dest = virt.file.File.get_generate_dest(full_version, distribution)
                virt_image_name = virt.file.File.get_virt_image_name(full_version, distribution, virt_types[0])

                logger.debug('Packer http url: %s', http_url)
                logger.debug('Generation destination: %s', down_dest)

                version_info = full_version.split('.')

                packer_data = {
                    'binary': packer_stds['bin_location'],
                    'templates': packer_stds['template_location'],
                    'distribution': distribution,
                    'version': version_info[0],
                    'update': version_info[1],
                    'http_url': http_url,
                    'http_checksum_url': http_checksum_url,
                    'vm_name': virt_image_name,
                    'HTTP_IP': packer_stds['kickstart']['http_ip'],
                    'HTTP_PORT': packer_stds['kickstart']['http_port'],
                    'output_directory': distro_stds[version_info[0]]['dest'],
                    'virt_type': virt_types[0],
                    'checksum_type': distro_stds[version_info[0]]['checksum_type']
                }

                if len(version_info) == 3:
                    packer_data['stamp_version'] = version_info[2]
                    packer_data['dot'] = '.'
                else:
                    packer_data['stamp_version'] = ""
                    packer_data['dot'] = ""

                packer_working_dir_fmt = distro_stds[version_info[0]]['packer_working_dir']
                packer_vars_file_fmt = distro_stds[version_info[0]]['packer_vars']
                packer_template_fmt = distro_stds[version_info[0]]['packer_template']

                packer_working_dir = packer_working_dir_fmt.format(**packer_data)
                packer_working_dir_full = '{}/{}'.format(packer_data['templates'], packer_working_dir)
                ansible_working_dir_full = '{}/../../ansible'.format(packer_working_dir_full)

                if os.path.exists(packer_working_dir_full):
                    packer_vars_file_name = packer_vars_file_fmt.format(**packer_data)
                    packer_template_name = packer_template_fmt.format(**packer_data)
                    packer_data['packer_vars_file_name'] = packer_vars_file_name
                    packer_data['packer_template_name'] = packer_template_name

                    http_kickstart_working_dir = '{}/kickstart'.format(packer_working_dir_full)

                    packer_1 = '{binary} build -var-file={packer_vars_file_name}'
                    packer_var_1 = '-var "url_iso={http_url}" -var "checksum_type={checksum_type}" -var "url_checksum={http_checksum_url}"'
                    packer_var_2 = '-var "vm_name={vm_name}" -var "HTTPIP={HTTP_IP}"'
                    packer_var_3 = '-var "HTTPPort={HTTP_PORT}" -var "output_directory={output_directory}"'
                    packer_2 = '{packer_template_name}'

                    packer_cmd_fmt = '{} {} {} {} {}'.format(packer_1, packer_var_1, packer_var_2, packer_var_3, packer_2)
                    packer_cmd = packer_cmd_fmt.format(**packer_data)
                    ansible_roles_cmd = 'ansible-galaxy install -f -r requirements.yml -p {}/roles'.format(ansible_working_dir_full)

                    logger.info('Starting generation: %s', virt_image_name)

                    packer_args = shlex.split(packer_cmd)
                    ansible_roles_args = shlex.split(ansible_roles_cmd)

                    logger.info("Starting local HTTP kickstart server...")

                    http_kickstart = subprocess.Popen(
                        ["/usr/bin/python3", "-m", "http.server"],
                        cwd=http_kickstart_working_dir
                    )

                    time.sleep(3)

                    logger.info("Checking if HTTP server is running on {HTTP_IP}:{HTTP_PORT}".format(**packer_data))

                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex((packer_data['HTTP_IP'], int(packer_data['HTTP_PORT'])))

                    if result == 0:
                       logger.info("HTTP is running")
                       sock.close()
                    else:
                       logger.error("HTTP is not running on expected address")
                       sys.exit(1)

                    logger.info("Downloading roles")

                    try:
                        ansible_roles_proc = subprocess.Popen(
                            ansible_roles_args,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            cwd=ansible_working_dir_full,
                            universal_newlines=True
                        )
                    except Exception as exc:
                        logger.error(str(exc))
                        sys.exit(1)

                    for line in iter(ansible_roles_proc.stdout.readline,''):
                        logger.debug(line.rstrip())

                    logger.info("Starting packer...")
                    logger.debug("Packer command: %s", packer_cmd)

                    try:
                        packer_proc = subprocess.Popen(
                            packer_args,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            cwd=packer_working_dir_full,
                            universal_newlines=True
                        )
                    except Exception as exc:
                        logger.error(str(exc))
                        sys.exit(1)

                    for line in iter(packer_proc.stdout.readline,''):
                        logger.debug(line.rstrip())

                    if http_kickstart.poll() is None:
                        http_kickstart.terminate()
                        logger.info("Stopped kickstart HTTP server")

                    if packer_proc.poll() is None:
                        packer_proc.terminate()

                    logger.info('Generation finished: %s', virt_image_name)
                else:
                    msg = 'Templates doesn\'t exist for {distribution} version {version}'.format(**packer_data)
                    logger.info(msg)
                    sys.exit()
            else:
                logger.info("Skipping generation, already generated or not present on remote: %s", full_version)
