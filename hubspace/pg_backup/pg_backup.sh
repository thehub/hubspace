#!/bin/bash

#usage: pg_backup -D dbname -U usernamce -P password 

while [ $# -gt 0 ]; do
    case $1 in
	-D|dbname)
	    shift
	    dbname=$1
	    ;;
	-U|username)
            shift
	    username=$1
	    ;;
	-P|password)
	    shift
	    password=$1
	    ;;	
        -O|output)
	    shift
	    output_file=$1
	    ;;
    esac

    shift
done


export PGPASSWORD=$password
if ! touch $output_file ; then
    echo "can't write to file $output_file"
    exit 1
fi
pg_dump -Fc $dbname -U $username  > $output_file
