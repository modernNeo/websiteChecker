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
	echo; echo
}

output[0]="Installng sendemail along with all other neeeded libaries"
output[1]="For sending an email with gmail"
create_box $output
sudo apt-get -y update
sudo apt-get install -y sendemail libio-socket-ssl-perl ssmtp
echo "enter your gmail user name here [everything before \"@gmail.com\"]: "
read gmailuserName
touch ./email.log

output[0]="Example command to send email:"
output[1]=""
output[2]="sendemail -f $gmailuserName@gmail.com -t receiver@domain.com \\"
output[3]="-s smtp.gmail.com:587 -xu $gmailuserName@gmail.com \\"
output[4]="[ -l ./email.log ] [ -u Brazil Email Test ] \\"
output[5]="[ -o tls=auto ] [ -xp password ] \\"
output[6]="[ -o message-file=\"/home/ubuntu/body.txt\" ]"
output[7]=""
output[8]="*command options in \"[ ]\" are optional"
create_box $output