#!/bin/sh

# Downloads Raspbian SD image and prepares it for testing (enable SSH and add trusted key)
# Downloads also the dependencies (kernel and dtb file) for QEMU emulation

set -e -x

show_help_and_exit() {
  cat << EOF
Usage: $0 raspbian-version

Arguments:
    raspbian-version    - Official Raspbian Buster version, for example 2019-07-10
EOF
  exit 1
}

version=""
while [ $# -gt 0 ]; do
  case "$1" in
    -*)
      echo "Error: unsupported option $1"
      show_help_and_exit_error
      ;;
    *)
      version="$1"
      shift
      ;;
  esac
done

if [ -z "$version" ]; then
	show_help_and_exit
fi

currdir=$(pwd)
scriptdir=$(cd `dirname $0` && pwd)
workdir=${currdir}/tmp-work
mkdir -p ${workdir}

raspbian_filename_zip="${version}-raspbian-buster-lite.zip"
raspbian_filename_img="${version}-raspbian-buster-lite.img"
raspbian_mender_filename_img="${version}-raspbian-mender-testing.img"

if [ -f ${currdir}/${raspbian_mender_filename_img} ]; then
    echo "Found testing image in current directory. Exiting"
    exit 0
fi

# Get superuser privilages to be able to mount the SD image
sudo true

cd ${workdir}

# For some reason, Raspbian version 2019-04-08 is in a folder named 2019-04-09
if [ ${version} = "2019-04-08" ]; then
    raspbian_url="https://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2019-04-09/${raspbian_filename_zip}"
# For some reason, Raspbian version 2019-07-10 is in a folder named 2019-07-12
elif [ ${version} = "2019-07-10" ]; then
    raspbian_url="https://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2019-07-12/${raspbian_filename_zip}"
else
    raspbian_url="https://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-${version}/${raspbian_filename_zip}"
fi

echo "##### Donwloading and extracting..."
wget -q -nc ${raspbian_url}
unzip ${raspbian_filename_zip}
rm ${raspbian_filename_zip}
wget -q -nc https://raw.githubusercontent.com/dhruvvyas90/qemu-rpi-kernel/master/kernel-qemu-4.19.50-buster
wget -q -nc https://raw.githubusercontent.com/dhruvvyas90/qemu-rpi-kernel/master/versatile-pb-buster.dtb

echo "##### Preparing image for tests..."
boot_start=$(fdisk -l ${raspbian_filename_img} | grep Linux | tr -s ' ' | cut -d ' ' -f2)
sector_size=$(fdisk -l ${raspbian_filename_img} | grep '^Sector' | cut -d' ' -f4)
offset=$(expr $boot_start \* $sector_size)
mkdir -p img-rootfs
sudo mount -o loop,offset=$offset ${raspbian_filename_img} img-rootfs

sudo mkdir img-rootfs/home/pi/.ssh
cat ${scriptdir}/../ssh-keys/key.pub | sudo tee img-rootfs/home/pi/.ssh/authorized_keys
sudo ln -s /lib/systemd/system/ssh.service img-rootfs/etc/systemd/system/multi-user.target.wants/ssh.service
sudo umount img-rootfs
rmdir img-rootfs

mv ${raspbian_filename_img} ${currdir}/${raspbian_mender_filename_img}
mv kernel-qemu-4.19.50-buster ${currdir}/
mv versatile-pb-buster.dtb ${currdir}/

cd ${currdir}
rm -rf ${workdir}

echo "##### Done"

exit 0
