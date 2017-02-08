Installation:
=========

  Compatible with python2

  **Download source:**

    git clone URL /opt/iso-imager

  **Install virtualenv:**

    pip install virtualenv

  **Setup virtual environment:**

    cd /opt/iso-imager
    virtualenv --no-site-packages venv

  **Activate virtual environment:**

    source venv/bin/activate

  **Install dependencies:**

    pip install -r requirements.txt

  For iso-imager-gen tool you must download packer and create packer templates.
  Paths to packer templates, names of generated images etc... are configured in config_gen.yml

Usage:
=========

#### IMPORTANT NOTE

  Tool will download/generate iso only if it doesn't exist in destination and if it is available
  on source ftp server.

#### Examples

  This will download all versions of centos distribution:

    /opt/iso-imager/iso-imager-down -s all -d centos

  This will download latest version of ubuntu distribution:

    /opt/iso-imager/iso-imager-down -s latest -d ubuntu

  This will download all versions of centos distribution with major version 6:

    /opt/iso-imager/iso-imager-down -s major -d centos -m 6

  This will generate all versions of centos to virtualbox image (type of image is configured in config):

    /opt/iso-imager/iso-imager-gen -g all -d centos -t vbox

  This will generate latest version of ubuntu distribution to qemu image:

    /opt/iso-imager/iso-imager-gen -g latest -d ubuntu -t qemu

  This will generate specific version of ubuntu distribution to qemu image:

    /opt/iso-imager/iso-imager-gen -g version -r 16.04.1 -d ubuntu -t qemu

  Running in cron (create also logrotate configuration to rotate logs):

    0 */12 * * * . /opt/iso-imager/venv/bin/activate && /opt/iso-imager/iso-imager-down -s all -d ubuntu 2>&1 >> /var/log/iso-imager.log

### Credits:

  __Author: Pavol Ipoth__

### Copyright:

  __License: GPLv3__
