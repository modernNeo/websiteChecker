#!/bin/bash

create_box (){
	output="$@"
	greatestLength=0
	for i in "${output[@]}"
	do
		if [ $greatestLength -lt ${#i} ]; then
			greatestLength=${#i}
		fi
	done

	# section for printing top border
	echo; for i in $(seq $(($greatestLength + 8))); do echo -n "#"; done; echo
	echo -n "###"; for i in $(seq $(($greatestLength + 2))); do echo -n " "; done; echo "###"

	# sectiom for printing logs
	for i in "${output[@]}"
	do
		echo -n "### "$i
		for i in $(seq $(($greatestLength - ${#i} +1 ))); do echo -n " "; done;
		echo "###"
	done
	
	# section for printing bottom border
	echo -n "###"; for i in $(seq $(($greatestLength + 2))); do echo -n " "; done;	echo "###"	
	for i in $(seq $(($greatestLength + 8))); do echo -n "#"; done;
	echo

}

############################################################
## REFERENCE PAGE FOR CHROME "Linux Package Signing Keys" ##
## https://www.google.com/linuxrepositories/              ##
############################################################
output[0]="Adding the repos that are needed for"
output[1]="Google Chrome and updating the repo list"
create_box $output
sudo mkdir -p /etc/apt/sources.list.d/
sudo bash -c "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google-chrome.list"
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo apt-get -y update


##################################################
## REFERENCE PAGE FOR CHROMEDRIVER INSTALLATION ##
## https://gist.github.com/mikesmullin/2636776  ##
##################################################
output[0]="Installing the tools needed to"
output[1]="Set up a virtual python environment"
output[2]="And install the needed modules and"
outoyt[3]="tools for running selenium"
output[4]="with Chrome on a server with no monitor"
create_box $output
sudo apt-get install -y python3-venv
python3 -m venv ENV
. ENV/bin/activate
pip3 install -r requirements.txt
sudo apt-get install unzip
wget http://chromedriver.storage.googleapis.com/LATEST_RELEASE
if [ $(uname -m) == i686 ]; 
then
	b=32;
elif [ $(uname -m) == x86_64 ]; 
then
	b=64; 
fi
latest=$(cat LATEST_RELEASE)
wget 'http://chromedriver.storage.googleapis.com/'$latest'/chromedriver_linux'$b'.zip'
unzip 'chromedriver_linux'$b'.zip'
rm 'chromedriver_linux'$b'.zip'
sudo mv chromedriver /usr/bin/.
export DISPLAY=:99
sudo apt-get install -y google-chrome-stable