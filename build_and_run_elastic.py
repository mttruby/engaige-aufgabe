import os

from subprocess import Popen, PIPE

try:
    os.system("docker create --name elastic-rag-01 -p 9200:9200 docker.elastic.co/elasticsearch/elasticsearch:8.14.1")
except:
    print("Error creating elasticsearch container.")

try:
    os.system("docker start elastic-rag-01")
except:
    print("Error starting elasticsearch container.")


cmd = ["yes", "docker", "exec", "-it", "elastic-rag-01", "/usr/share/elasticsearch/bin/elasticsearch-reset-password", "-u", "elastic"]

p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
output, error = p.communicate(input=b'\n')

print(output)