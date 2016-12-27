Installation:
=========

  Compatible with python3

  **Download source:**

    git clone URL /opt/dist-iso-down

  **Install virtualenv:**

    pip install virtualenv

  **Setup virtual environment:**

    cd /opt/dist-iso-down
    virtualenv --no-site-packages venv

  **Activate virtual environment:**

    source venv/bin/activate

  **Install dependencies:**

    pip install -r requirements.txt

  For dist-iso-gen tool you must download packer and create packer templates.
  Paths to packer templates, names of generated images etc... are configured in config_gen.yml

Usage:
=========

#### IMPORTANT NOTE

  Tool will download/generate iso only if it doesn't exist in destination and if it is available
  on source ftp server.

#### Examples

  This will download all versions of centos distribution:

    /opt/dist-iso-down/dist-iso-down -s all -d centos

  This will download latest version of ubuntu distribution:

    /opt/dist-iso-down/dist-iso-down -s latest -d ubuntu

  This will download all versions of centos distribution with major version 6:

    /opt/dist-iso-down/dist-iso-down -s major -d centos -m 6

  This will generate all versions of centos to virtualbox image (type of image is configured in config):

    /opt/dist-iso-down/dist-iso-gen -s all -d centos -t vbox

  This will generate latest version of ubuntu distribution to qemu image:

    /opt/dist-iso-down/dist-iso-gen -s latest -d ubuntu -t qemu

  Running in cron (create also logrotate configuration to rotate logs):

    0 */12 * * * . /opt/dist-iso-down/venv/bin/activate && /opt/dist-iso-down/dist-iso-down -s all -d ubuntu 2>&1 >> /var/log/dist-iso-down.log

### Credits:

  __Author: Pavol Ipoth__

### Copyright:

  __License: GPLv3__
