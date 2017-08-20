#!/bin/bash

user="diapy"
home_user="/home/${user}"
cur_path=$(pwd)

diapyorama_exec="diapyorama.py"
bin_path="${home_user}/bin"
diapyorama_exec_path="${bin_path}/${diapyorama_exec}"
slides_path="${home_user}/slides"
openbox_path="${home_user}/.config"

be_root()
{
	if [ `id -u` -eq 0 ]
	then
		echo "Use with a no-admin user"
		#"$@"
	elif [ -x /bin/sudo -o -x /usr/bin/sudo  ]
	then
		/usr/bin/sudo "$@"
	else
		echo "Install sudo"
	fi
}

install_apt()
{
	for input in "$@"
	do
		dpkg -s "$input" > /dev/null 2>&1
		if [ "$?" -ne 0 ]
		then
			be_root apt install -y --no-install-recommends "$input"
		fi
	done
}

check_dir()
{
	for input in "$@"
	do
		if [ ! -d "$input" ]
		then
			mkdir -p "$input"
		fi
	done
}


#be_root apt-get update

install_apt xorg openbox lightdm sqlite3
install_apt python3 python3-tk python3-pil.imagetk

check_dir "$bin_path" "$slides_path" "$openbox_path"

be_root cp "${cur_path}/config/lightdm/lightdm.conf" /etc/lightdm/lightdm.conf

if [ -f "${home_user}/.profile" -a ! -f "${home_user}/.xsessionrc" ]
then
	ln -s "${home_user}/.profile" "${home_user}/.xsessionrc"
fi

if [ ! -h "$diapyorama_exec_path" ]
then
	ln -s "${cur_path}/${diapyorama_exec}" "$diapyorama_exec_path"
fi

if [ ! -h "${openbox_path}/openbox" ]
then
	ln -s "${cur_path}/config/openbox" "$openbox_path"
fi

if [ ! -f "${bin_path}/convertslides" -a -f "${cur_path}/tools/convertslides" ]
then
	ln -s "${cur_path}/tools/convertslides" "$bin_path"
fi

# ft=bash
