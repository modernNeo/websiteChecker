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

	# section for bordering
	echo; for i in $(seq $(($greatestLength + 8))); do echo -n "#"; done; echo
	echo -n "###"; for i in $(seq $(($greatestLength + 2))); do echo -n " "; done; echo "###"

	# sectiom for printing logs
	for i in "${output[@]}"
	do

		echo -n "### "$i
		for i in $(seq $(($greatestLength - ${#i} +1 ))); do echo -n " "; done;
		echo "###"
	done
	
	# section for bordering
	echo -n "###"; for i in $(seq $(($greatestLength + 2))); do echo -n " "; done;	echo "###"	
	for i in $(seq $(($greatestLength + 8))); do echo -n "#"; done;
	echo

}

output[0]="Installng sendemail along with all other neeeded libaries"
output[1]="For sending an email with gmail"
create_box $output
sudo apt-get -y update
sudo apt-get install -y sendemail
sudo apt-get install -y libio-socket-ssl-perl 
sudo apt-get install -y ssmtp
echo "enter your gmail user name here [everything before @gmail.com]: "
read gmailuserName
echo "Enter password"
read gmailPassword
sudo bash -c "echo 'root=$gmailuserName@gmail' > /etc/ssmtp/ssmpt.conf"
sudo bash -c "echo 'mailhub=smtp.gmail.com:465' >> /etc/ssmtp/ssmpt.conf"
sudo bash -c "echo 'FromLineOverride=YES' >> /etc/ssmtp/ssmpt.conf"
sudo bash -c "echo 'AuthUser=$gmailuserName@gmail.com' >> /etc/ssmtp/ssmpt.conf"
sudo bash -c "echo 'AuthPass=$gmailPassword' >> /etc/ssmtp/ssmpt.conf"
sudo bash -c "echo 'UseSTARTTLS=YES' >> /etc/ssmtp/ssmpt.conf"
touch ./email.log
#chmod 640 /etc/ssmtp/ssmtp.conf

output[0]="example commands to send email"
output[1]="sendemail [ -l ./email.log ] -f sender@gmail.com -u \"Brazil Email Test\" -t receiver@domain.com -s \"smtp.gmail.com:587\" -o tls=auto -xu youremail@gmail.com [ -xp password ] [ -o message-file=\"/home/ubuntu/body.txt\" ] "
create_box $output