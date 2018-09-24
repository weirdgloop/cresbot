#! /bin/bash
# Compress log files to save space and remove old logs

rotate() {
	local -r MAX=10
	local i=1

	cd /home/cqm/cresbot/logs/

	for log_file in hiscorecounts-*; do
		# ignore the first one in case it's still in use
		if [ $i != 1 ]; then
			# compress log file - no op if it's already compressed
			gzip $log_file

			if [ "$i" -gt "$MAX" ]; then
				rm -f $log_file
			fi
		fi

		((i++))
	done
}

rotate
