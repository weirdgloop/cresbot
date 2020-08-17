#! /bin/bash
# Compress log files to save space and remove old logs

rotate() {
	local -r MAX=40
	local i=1

	cd /home/cqm/cresbot/logs/

	for log_file in $(ls -t hiscorecounts-*.log); do
		# ignore the first one in case it's still in use
		if [[ $i != 1 ]]; then
			# compress log file - no op if it's already compressed
			gzip $log_file

			if (( $i > $MAX )); then
				rm -f $log_file
			fi
		fi

		((i++))
	done

	for log_file in $(ls -t hiscorecounts-*.json); do
		# ignore the first one in case it's still in use
		if [[ $i != 1 ]]; then
			# compress log file - no op if it's already compressed
			gzip $log_file

			if (( $i > $MAX )); then
				rm -f $log_file
			fi
		fi

		((i++))
	done
}

rotate
