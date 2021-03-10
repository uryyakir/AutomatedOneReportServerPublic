#!/bin/bash  
threshold=29
DAYS=`sudo certbot certificates | grep -oP "VALID: \d{1,2} days" | grep -oP "\d{1,2}" | xargs echo`

if [ $DAYS -lt $threshold ]
	then sudo certbot renew && echo "$DAYS is less than $threshold"

else 
	echo "we gucci, still got $DAYS left"
fi

# this script is run via crontab: 0 */12 * * * cd /home/ec2-user/AutomatedOneReportAPI/ && ./certbot-renew.sh
