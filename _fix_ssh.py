# fix ssh setup_keys in launch_chffrplus.sh
p = "launch_chffrplus.sh"
s = open(p, encoding="utf-8").read()
old = """  # openpilot ssh key installer
  if [ ! -f /data/params/d/GithubSshKeys ]; then
    echo -n openpilot > /data/params/d/GithubUsername
    cat /system/comma/home/setup_keys > /data/params/d/GithubSshKeys
    echo -n 1 > /data/params/d/SshEnabled
    setprop persist.neos.ssh 1
  fi"""
new = """  # openpilot ssh key installer
  if [ ! -f /data/params/d/GithubSshKeys ]; then
    echo -n openpilot > /data/params/d/GithubUsername
    SETUP_KEYS="/system/comma/home/setup_keys"
    if [ ! -f "$SETUP_KEYS" ] && [ -f "$BASEDIR/system/comma/home/setup_keys" ]; then
      mkdir -p /system/comma/home
      cp -f "$BASEDIR/system/comma/home/setup_keys" "$SETUP_KEYS"
    fi
    if [ -f "$SETUP_KEYS" ]; then
      cat "$SETUP_KEYS" > /data/params/d/GithubSshKeys
      echo -n 1 > /data/params/d/SshEnabled
      setprop persist.neos.ssh 1
    else
      echo "WARNING: setup_keys not found, SSH keys left empty"
    fi
  fi"""
assert old in s, "pattern not found"
open(p, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
print("patched")
