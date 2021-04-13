#!/bin/bash

# hadoop client location
HADOOP_INSTALL="/usr/bin/hadoop/software/yarn"
HADOOP="$HADOOP_INSTALL/bin/hadoop"

# time, tag, balabala...
tag=`date +%Y%m%d`

job_name="i-luchaoyi_whois-unicode"
#input="/home/hdp-netlab/i-luchaoyi/GDPR/whois-data-14days/20180101-1/"
#input="/home/hdp-netlab/whoisdb/log/new/20180401"
#input="/home/hdp-netlab/i-liubaojun/data/gdpr/large-scale/20190520_inpit/"
output="/home/hdp-netlab/i-luchaoyi/whois-unicode/"

# input and out put
local_dir=`pwd`
# tools_dir="${local_dir}/tools"

# python file location
mapper_file=$local_dir/mapper.py
reducer_file=$local_dir/reducer.py

mapper=`basename $mapper_file`
reducer=`basename $reducer_file`

# WARNING
$HADOOP fs -rm -r $output

$HADOOP streaming \
  -D mapred.job.priority=NORMAL \
  -D mapred.job.name="$job_name" \
  -D mapred.reduce.tasks=50  \
  -D mapreduce.reduce.maxattempts=20 \
  -jobconf mapreduce.reduce.memory.mb=12288 \
  -input "/home/hdp-netlab/whoisdb/log/new/20180401" \
  -output "$output" \
  -mapper "./mapper.py" \
  -reducer "./reducer.py" \
  -file "$mapper_file" \
  -file "$reducer_file" 
# -cmdenv LD_LIBRARY_PATH=./baojun/baojun/lib/