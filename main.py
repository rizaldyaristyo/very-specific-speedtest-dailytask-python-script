# Speedtest Daily Tasklist

from routeros_ssh_connector import MikrotikDevice
import speedtest
import requests
import time

server = "d8xxxxxxxx13.sn.mynetname.net"
port = "22"
username = "your_mikrotik_ssh_username"
password = "your_mikrotik_ssh_password"

s1 = speedtest.Speedtest(secure=True)
s2 = speedtest.Speedtest(secure=True)
s3 = speedtest.Speedtest(secure=True)
router = MikrotikDevice()
router.connect(server, username, password, port)

router.send_command('/log warning "[SPEEDTEST] Speedtest Commencing..."')
print("[SPEEDTEST] Speedtest Commencing...")

router.send_command('/log warning "[SPEEDTEST] Creating Failsafe, Just in Case SSH Disconnected Mid Failover disablement..."')
print("[SPEEDTEST] Creating Failsafe, Just in Case SSH Disconnected Mid Failover disablement...")
router.send_command('system scheduler add name=failsave start-time=startup interval=7m disabled=no on-event="system scheduler set [find name=Failover] disabled=no; system scheduler remove failsave"')

get_last = router.send_command('/put ([ip firewall address-list get [find where comment="Server"] list])')

router.send_command('/system script run Restore')
router.send_command('/system scheduler set [find name=Failover] disabled=yes')

router.send_command('/ip firewall address-list set [find comment="Server"] list=ISP2')
router.send_command('/log warning "[SPEEDTEST] Testing ISP2 Download..."')
print("[SPEEDTEST] Testing ISP2 Download...")
s1.download(threads=None)
router.send_command('/log warning "[SPEEDTEST] Testing ISP2 Upload..."')
print("[SPEEDTEST] Testing ISP2 Upload...")
s1.upload(threads=None, pre_allocate=False)
result_s1 = s1.results.share()[:-4]

router.send_command('/ip firewall address-list set [find comment="Server"] list=ISP1')
router.send_command('/log warning "[SPEEDTEST] Testing ISP1 Download..."')
print("[SPEEDTEST] Testing ISP1 Download...")
s2.download(threads=None)
router.send_command('/log warning "[SPEEDTEST] Testing ISP1 Upload..."')
print("[SPEEDTEST] Testing ISP1 Upload...")
s2.upload(threads=None, pre_allocate=False)
result_s2 = s2.results.share()[:-4]

router.send_command('/ip firewall address-list set [find comment="Server"] list=ISP3')
router.send_command('/log warning "[SPEEDTEST] Testing ISP3 Download..."')
print("[SPEEDTEST] Testing ISP3 Download...")
s3.download(threads=None)
router.send_command('/log warning "[SPEEDTEST] Testing ISP3 Upload..."')
print("[SPEEDTEST] Testing ISP3 Upload...")
s3.upload(threads=None, pre_allocate=False)
result_s3 = s3.results.share()[:-4]

router.send_command('/log warning "[SPEEDTEST] Speedtest Complete, Restoring Test Route..."')
print("[SPEEDTEST] Speedtest Complete, Restoring Test Route...")
if "ISP1" in get_last:
    router.send_command('/ip firewall address-list set [find comment="Server"] list=ISP1')
elif "ISP2" in get_last:
    router.send_command('/ip firewall address-list set [find comment="Server"] list=ISP2')
elif "ISP3" in get_last:
    router.send_command('/ip firewall address-list set [find comment="Server"] list=ISP3')

router.send_command('/log warning "[SPEEDTEST] Re-enabling Failover and Removing Failsafe..."')
print("[SPEEDTEST] Re-enabling Failover and Removing Failsafe...")
router.send_command('/system scheduler set [find name=Failover] disabled=no')
router.send_command('/system scheduler remove failsave')

router.send_command('/log warning "[SPEEDTEST] All Clear, Disconnecting..."')
print("[SPEEDTEST] All Clear, Disconnecting...")
router.disconnect()

print_results = "[Speedtest Daily Task] \n\n" + result_s1 + "\n" + result_s2 + "\n" + result_s3

print(print_results)
f = open("result" + time.strftime("%d%m%Y %H%M%S") + ".txt", "w")
f.write(print_results)
f.close()
requests.get("https://api.telegram.org/bot50xxxxxxxx:xxxxxxxxxxxxR3wkuAo6Lxxxxxxxxxxxxxxx/sendMessage?chat_id=-10xxxxxxxxxxx&text=" + print_results)