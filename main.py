root_password = "root"
user_name = "colab"
user_password = "colabcolab"
vnc_passwd = user_password

import pathlib
import subprocess
import os

os.system("apt install openssh-server")

#Reset host keys
for i in pathlib.Path("/etc/ssh").glob("ssh_host_*_key"):
  i.unlink()
subprocess.run(["ssh-keygen", "-A"],check = True)

#Prevent ssh session disconnection.
with open("/etc/ssh/sshd_config", "a") as f:
  f.write("\n\nClientAliveInterval 120\n")

# try:
#   from config import *
# except:
#   print("config not found .. using defaults")

try:
  subprocess.run(["unminimize"], input = "y\n", check = True, universal_newlines = True)
except:
  os.system("apt-get update")
  subprocess.run(["unminimize"], input = "y\n", check = True, universal_newlines = True)


print(f"root password: {root_password}")
print(f"{user_name} password: {user_password}")
#print("✂️"*24)
subprocess.run(["useradd", "-s", "/bin/bash", "-m", user_name])
subprocess.run(["adduser", user_name, "sudo"], check = True)
subprocess.run(["chpasswd"], input = f"root:{root_password}", universal_newlines = True)
subprocess.run(["chpasswd"], input = f"{user_name}:{user_password}", universal_newlines = True)
subprocess.run(["service", "ssh", "restart"])

os.system("git clone https://github.com/Rayanfer32/remocolab.git")
print("installing turbovnc and vgl")
os.system("dpkg -i remocolab/libjpeg-turbo.deb")
os.system("dpkg -i remocolab/virtualgl.deb")
os.system("dpkg -i remocolab/turbovnc.deb")
os.system("apt install -f")
print("Installing xfce4 desktop environment and gui automation tools")
os.system("apt install xfce4 xfce4-terminal")
os.system("sudo apt-get update")
os.system("pip3 install paramiko pyautogui")

def sendsshcmd(cmdssh,mode=None):
  import paramiko
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh.connect("localhost","22",user_name,user_password,timeout=10)
  if mode == "exit":
    print("ssh command sent:",cmdssh)
    ssh.exec_command(cmdssh)
  elif mode == "sudo":
    stdin, stdout, stderr = ssh.exec_command(cmdssh ,get_pty = True)
    stdin.write(user_password+'\n')
    stdin.flush()
    out = stdout.read().decode()
    print("command sent:",cmdssh,"\noutput:",out)
    return out
  elif mode == "sudoexit":
    stdin, stdout, stderr = ssh.exec_command(cmdssh ,get_pty = True)
    stdin.write(user_password+'\n')
    stdin.flush()
  elif mode == "rootexit":
    stdin, stdout, stderr = ssh.exec_command("su" ,get_pty = True)
    stdin.write(root_password+'\n')
    stdin.write(cmdssh+'\n')
    stdin.flush()
  else:
    stdin, stdout, stderr = ssh.exec_command(cmdssh)
    out = stdout.read().decode()
    print("command sent:",cmdssh,"\noutput:",out)
    return out

vnc_sec_conf_p = pathlib.Path("/etc/turbovncserver-security.conf")
vnc_sec_conf_p.write_text("""\
no-remote-connections
no-httpd
no-x11-tcp-connections
""")
vncrun_py = pathlib.Path("vncrun.py")
vncrun_py.write_text("import subprocess, secrets, pathlib;vnc_passwd =\""+vnc_passwd+"""\"
vnc_viewonly_passwd = 'colab'
print("VNC password: {}".format(vnc_passwd))
vncpasswd_input = "{0}\\n{1}".format(vnc_passwd, vnc_viewonly_passwd)
vnc_user_dir = pathlib.Path.home().joinpath(".vnc")
vnc_user_dir.mkdir(exist_ok=True)
vnc_user_passwd = vnc_user_dir.joinpath("passwd")
with vnc_user_passwd.open('wb') as f:
  subprocess.run(
    ["/opt/TurboVNC/bin/vncpasswd", "-f"],
    stdout=f,
    input=vncpasswd_input,
    universal_newlines=True)
vnc_user_passwd.chmod(0o600)
subprocess.run(
  ["/opt/TurboVNC/bin/vncserver"]
)
#Disable screensaver because no one would want it.
(pathlib.Path.home() / ".xscreensaver").write_text("mode: off\\n")
""")
r = subprocess.run(
                  ["su", "-c", "python3 vncrun.py", "colab"],
                  check = True,
                  stdout = subprocess.PIPE,
                  universal_newlines = True)
print(r.stdout)

os.system('wget -qO - https://keys.anydesk.com/repos/DEB-GPG-KEY | apt-key add -')
os.system('echo "deb http://deb.anydesk.com/ all main" > /etc/apt/sources.list.d/anydesk-stable.list')
os.system('apt update > /dev/null')
os.system('apt install anydesk > /dev/null')

sendsshcmd("python3 /content/xfce_def.py")
sendsshcmd("python3 /content/adesk.py")

ad_id = sendsshcmd("anydesk --get-id")

# adpass ="necromancer123" #must be 15 letters  
print("ANYDESK ID:",ad_id)
# print("ANYDESK PASS:",adpass)
print("ENJOY YOUR DAY!!!")



import ssl
import pathlib, stat, shutil, urllib.request, subprocess, getpass, time
import secrets, json, re

def _download(url, path):
  try:
    print("downloading:",path)
    with urllib.request.urlopen(url,context=ssl._create_unverified_context()) as response:
      with open(path, 'wb') as outfile:
        shutil.copyfileobj(response, outfile)
  except:
    print("download fail")

def get_gpu_name():
  r = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], stdout = subprocess.PIPE, universal_newlines = True)
  if r.returncode != 0:
    return None
  return r.stdout.strip()

def _check_gpu_available():
  gpu_name = get_gpu_name()
  print(gpu_name)
  if gpu_name == None:
    print("This is not a runtime with GPU")
    return False
  elif gpu_name == "Tesla K80":
    print("Warning! GPU of your assigned virtual machine is Tesla K80.")
    print("You might get better GPU by reseting the runtime.")
    return True
  else:
    return True

def _setup_nvidia_gl():
  # Install TESLA DRIVER FOR LINUX X64.
  # Kernel module in this driver is already loaded and cannot be neither removed nor updated.
  # (nvidia, nvidia_uvm, nvidia_drm. See dmesg)
  # Version number of nvidia driver for Xorg must match version number of these kernel module.
  # But existing nvidia driver for Xorg might not match.
  # So overwrite them with the nvidia driver that is same version to loaded kernel module.
  ret = subprocess.run(
                  ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
                  stdout = subprocess.PIPE,
                  check = True,
                  universal_newlines = True)
  nvidia_version = ret.stdout.strip()
  nvidia_url = "https://us.download.nvidia.com/tesla/{0}/NVIDIA-Linux-x86_64-{0}.run".format(nvidia_version)
  _download(nvidia_url, "nvidia.run")
  pathlib.Path("nvidia.run").chmod(stat.S_IXUSR)
  subprocess.run(["./nvidia.run", "--no-kernel-module", "--ui=none"], input = "1\n", check = True, universal_newlines = True)
  # subprocess.Popen(["./nvidia.run", "--no-kernel-module", "--ui=none"], input = "1\n", check = True, universal_newlines = True)

  #https://virtualgl.org/Documentation/HeadlessNV
  subprocess.run(["nvidia-xconfig",
                  "-a",
                  "--allow-empty-initial-configuration",
                  "--virtual=1920x1200",
                  "--busid", "PCI:0:4:0"],
                 check = True
                )

  with open("/etc/X11/xorg.conf", "r") as f:
    conf = f.read()
    conf = re.sub('(Section "Device".*?)(EndSection)',
                  '\\1    MatchSeat      "seat-1"\n\\2',
                  conf,
                  1,
                  re.DOTALL)
  #  conf = conf + """
  #Section "Files"
  #    ModulePath "/usr/lib/xorg/modules"
  #    ModulePath "/usr/lib/x86_64-linux-gnu/nvidia-418/xorg/"
  #EndSection
  #"""

  with open("/etc/X11/xorg.conf", "w") as f:
    f.write(conf)

  #!service lightdm stop
  subprocess.run(["/opt/VirtualGL/bin/vglserver_config", "-config", "+s", "+f"], check = True)
  #user_name = "colab"
  #!usermod -a -G vglusers $user_name
  #!service lightdm start

  # Run Xorg server
  # VirtualGL and OpenGL application require Xorg running with nvidia driver to get Hardware 3D Acceleration.
  #
  # Without "-seat seat-1" option, Xorg try to open /dev/tty0 but it doesn't exists.
  # You can create /dev/tty0 with "mknod /dev/tty0 c 4 0" but you will get permision denied error.
  subprocess.Popen(["Xorg", "-seat", "seat-1", "-allowMouseOpenFail", "-novtswitch", "-nolisten", "tcp"])


if _check_gpu_available():
  _setup_nvidia_gl()
