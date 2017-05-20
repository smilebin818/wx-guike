import os, sys, threading

port = 7818

print("killing server which is using port: {0}".format(port))
# os.system("ps -ef | grep makeServer.py | grep -v grep | cut -c 9-15 | xargs kill -s 9")
os.system("netstat -ntlp | grep 7818 | awk '{print $7}' | awk -F/ '{print $1}' | xargs kill")

if len(sys.argv) == 2 and sys.argv[1] == "shut":
    sys.exit(0)

print("restarting cqwdt_restart.py 7818")

os.system("cd /home/yanbin/wx-cqwdt/ && nohup python /home/yanbin/wx-cqwdt/makeServer.py&")



