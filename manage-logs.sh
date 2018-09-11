#! /bin/bash
# Compress log files to save space and remove old logs

MAX=10

i=1

cd /home/cqm/cresbot/logs/

for log_file in $(ls -lt | grep hiscorecounts-*); do
	# ignore the first one in case it's still in use
	if [ $i == 1 ]; then
		continue
	fi

	# compress log file - no op if it's already compressed
	gzip $log_file

	if [ $i > $max ]; then
		rm -f $log_file
	fi

	((i++))
done
