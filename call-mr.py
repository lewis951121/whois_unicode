import os, datetime, time, subprocess

start = datetime.datetime.strptime("20210101", "%Y%m%d")
finish = datetime.datetime.strptime("20210310", "%Y%m%d")
old_date = datetime.datetime.strptime("20180401", "%Y%m%d")

now = start
# 0309: now i use one week. can be adjusted.
INTERVAL_DAYS = 7
week_no = 1

# 0327: some of the old folders are missing.
missing_old = ["20190623", "20190724", "20190805", "20191108",
               "20191109", "20191110", "20191227", "20191228", "20191229"]

while now.strftime("%Y%m%d") <= finish.strftime("%Y%m%d"):
    print now.strftime("%Y%m%d")
    now_str = now.strftime("%Y%m%d")

    inputf = open("scan-template.sh")
    outputf = open("scan" + now_str + ".sh", "w")
    for line in inputf:
        line = line.rstrip()
        if line.startswith("output="):
            new_line = "output=\"/home/hdp-netlab/i-luchaoyi/whois-unicode/" + now_str + "-" + str(week_no) + "\""
            print new_line
        elif "-input" in line:
            # 7 days.
            new_line = "  -input \"/home/hdp-netlab/whoisdb/log/new/" + now_str + "\" \\\n"
            if now.strftime("%Y%m%d") >= old_date.strftime("%Y%m%d"):
                # only dates after 20180401 have old data.
                # 0327: be careful, some old data is missing.
                if now_str not in missing_old:
                    new_line += "  -input \"/home/hdp-netlab/whoisdb/log/old/" + now_str + "\" \\\n"
            for temp in range(1, INTERVAL_DAYS):
                new_line += "  -input \"/home/hdp-netlab/whoisdb/log/new/" + (now + datetime.timedelta(days=temp)).strftime(
                    "%Y%m%d") + "\" \\\n"
                if now.strftime("%Y%m%d") >= old_date.strftime("%Y%m%d"):
                    if (now + datetime.timedelta(days=temp)).strftime("%Y%m%d") not in missing_old:
                        new_line += "  -input \"/home/hdp-netlab/whoisdb/log/old/" + \
                                    (now + datetime.timedelta(days=temp)).strftime("%Y%m%d") + "\" \\\n"
            new_line = new_line.rstrip("\n")
        elif line.startswith("job_name"):
            new_line = "job_name=\"i-luchaoyi-whois-unicode-" + now_str + "\""
        else:
            new_line = line
        outputf.write(new_line + "\n")
    outputf.close()
    ### FIXED: only look at failed cycles. check if the SUCCESS file exists in the output folder.
    cmd_str = os.popen(
        "hadoop fs -ls /home/hdp-netlab/i-luchaoyi/whois-unicode/" + now_str + "-" + str(week_no)).read()
    if "SUCCESS" in cmd_str:
        # this cycle has succeeded before. skip.
        print "SUCCESS"
    else:
        print "FAIL"
        # non-blocking call.
        subprocess.Popen("/bin/sh scan" + now_str + ".sh", shell=True)
        # time.sleep(900)

    now = now + datetime.timedelta(days=INTERVAL_DAYS)
    week_no += 1
    # break
