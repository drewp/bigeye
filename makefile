commands_in_use:
	grep "X obj" lighting.pd | cut -d' ' -f 5 | sort -u

install_packages:
	echo per http://puredata.info/docs/faq/debian
	sudo add-apt-repository "deb http://apt.puredata.info/releases `lsb_release -c | awk '{print $2}'` main"
	sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key 9f0fe587374bbe81
	sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key D63D3D09C39F5EEB
	sudo apt-get update
	sudo aptitude install -y pd-extended pd-moonlib puredata-extra
