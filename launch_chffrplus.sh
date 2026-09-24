#!/usr/bin/bash

if [ -z "$BASEDIR" ]; then
  BASEDIR="/data/openpilot"
fi

source "$BASEDIR/launch_env.sh"

# EON marker: this launcher is only installed on the Bolt EON (Termux)
if [ ! -f /EON ]; then
  touch /EON
fi


DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

# Upload EON diagnostic logs to GitHub logs/ branch (non-fatal, WiFi required)
function upload_eon_logs {
  local diagdir="/data/params"
  local logdir="$BASEDIR/eon_logs"
  mkdir -p "$logdir"

  # Copy diag files to a git-managed dir
  for f in eon_ssh_diag.txt eon_apk_diag.txt eon_carlist_diag.txt; do
    if [ -s "$diagdir/$f" ]; then
      cp -f "$diagdir/$f" "$logdir/$f"
    fi
  done

  # Also grab a snapshot of key params (read-only, safe)
  {
    echo "=== $(date) EON param snapshot ==="
    echo "GithubSshKeys size: $(wc -c < /data/params/d/GithubSshKeys 2>/dev/null || echo missing)"
    echo "mappy installed: $(pm list packages 2>/dev/null | grep -c mappyobn || echo 0)"
    echo "sshd process: $(pgrep -c sshd 2>/dev/null || echo 0)"
    echo "openpilot HEAD: $(cd "$BASEDIR" && git log --oneline -1 2>/dev/null)"
    echo "carlist_diag last 20 lines:"
    tail -20 /tmp/car_list_diag.txt 2>/dev/null || echo "(none)"
  } > "$logdir/summary.txt"

  # Try to push to logs/ branch (best-effort, 15s timeout)
  cd "$BASEDIR" || return
  local origin_url
  origin_url=$(git remote get-url origin 2>/dev/null)
  [ -n "$origin_url" ] || return
  # Re-authenticate on every boot in case the token changed.
  git remote set-url origin "$origin_url" 2>/dev/null
  case "$origin_url" in
    http://*|https://*)
      # Inject a token (dp_git_token param) if present; GitHub requires auth.
      local token
      token=$(cat /data/params/d/dp_git_token 2>/dev/null)
      if [ -n "$token" ]; then
        git remote set-url origin "https://x-access-token:$token@github.com/podony/ke.git" 2>/dev/null
      fi
      # Use a throwaway worktree so we never touch the main checkout.
      git worktree add -q -f /tmp/eon_logs_wt logs 2>/dev/null \
        || { git branch -q logs 2>/dev/null; git worktree add -q -f /tmp/eon_logs_wt logs 2>/dev/null; }
      if [ -d /tmp/eon_logs_wt ]; then
        cp -rf "$BASEDIR/eon_logs/." /tmp/eon_logs_wt/eon_logs/ 2>/dev/null
        ( cd /tmp/eon_logs_wt && \
          git -c user.email="eon@openpilot" -c user.name="EON" \
            commit -qam "eon logs $(date +%s)" --allow-empty 2>/dev/null; \
          timeout 15 git push -qf origin logs 2>>/data/params/eon_log_upload.txt \
            && echo "push OK $(date)" >> /data/params/eon_log_upload.txt \
            || echo "push FAIL rc=$? $(date)" >> /data/params/eon_log_upload.txt )
        git worktree remove -qf /tmp/eon_logs_wt 2>/dev/null
      fi
      ;;
    *) ;;
  esac
}

function two_init {
  fix_openpilot_symlinks "$BASEDIR"

  # Upload diagnostic logs to GitHub logs/ branch (non-fatal)
  upload_eon_logs &

  # convert to no ir ctrl param
  if [ -f /data/media/0/no_ir_ctrl ]; then
    echo -n 1 > /data/params/d/dp_device_no_ir_ctrl
  fi

  mount -o remount,rw /system
  # font installer
  if [ -f /EON ]; then
    if [ ! -f /system/fonts/NotoSansCJKtc-Regular.otf ]; then
      rm -fr /system/fonts/NotoSansTC*.otf
      rm -fr /system/fonts/NotoSansSC*.otf
      rm -fr /system/fonts/NotoSansKR*.otf
      rm -fr /system/fonts/NotoSansJP*.otf
      cp -rf /data/openpilot/selfdrive/assets/fonts/NotoSansCJKtc-* /system/fonts/
      cp -rf /data/openpilot/selfdrive/assets/fonts/fonts.xml /system/etc/fonts.xml
      chmod 644 /system/etc/fonts.xml
      chmod 644 /system/fonts/NotoSansCJKtc-*
    fi
  fi

  # openpilot ssh key installer
  # Re-install if the param file is missing OR empty (a previous failed
  # boot can leave an empty file, which would otherwise stay empty forever).
  # Diagnostics: /tmp is wiped on reboot, keep ssh diag in /data/params.
  SSHDIAG=/data/params/eon_ssh_diag.txt
  if [ ! -f /data/params/d/GithubSshKeys ] || [ ! -s /data/params/d/GithubSshKeys ]; then
    echo "two_init: ssh keys (re)install path entered" >> $SSHD
    [ ! -f "$BASEDIR/system/comma/home/setup_keys" ] && echo "BASEDIR setup_keys file MISSING: $BASEDIR/system/comma/home/setup_keys" >> $SSHD
    echo -n openpilot > /data/params/d/GithubUsername
    SETUP_KEYS="/system/comma/home/setup_keys"
    if [ ! -f "$SETUP_KEYS" ] && [ -f "$BASEDIR/system/comma/home/setup_keys" ]; then
      mkdir -p /system/comma/home
      cp -f "$BASEDIR/system/comma/home/setup_keys" "$SETUP_KEYS"
      echo "copied setup_keys from $BASEDIR -> $SETUP_KEYS" >> $SSHD
    fi
    if [ -f "$SETUP_KEYS" ]; then
      cat "$SETUP_KEYS" > /data/params/d/GithubSshKeys
    fi
    # Fallback: if the key file is still empty, write it directly from the
    # repo copy so an empty GithubSshKeys can never persist.
    if [ ! -s /data/params/d/GithubSshKeys ] && [ -f "$BASEDIR/system/comma/home/setup_keys" ]; then
      cat "$BASEDIR/system/comma/home/setup_keys" > /data/params/d/GithubSshKeys
      echo "fallback: wrote key directly from BASEDIR ($(wc -c < /data/params/d/GithubSshKeys) bytes)" >> $SSHD
    fi
    echo -n 1 > /data/params/d/SshEnabled
    setprop persist.neos.ssh 1 2>/dev/null || true
    echo "wrote GithubSshKeys ($(wc -c < /data/params/d/GithubSshKeys) bytes)" >> $SSHD
    if [ ! -s /data/params/d/GithubSshKeys ]; then
      echo "ERROR: GithubSshKeys is STILL EMPTY after all fallbacks" >> $SSHD
    fi
  else
    echo "two_init: ssh keys already present, skipped" >> $SSHD
  fi

  # Final guarantee: the param file must never be empty. This runs on EVERY
  # boot regardless of the branch taken above, and writes the raw file
  # directly (independent of the params .so key table).
  if [ -f "$BASEDIR/system/comma/home/setup_keys" ] && [ ! -s /data/params/d/GithubSshKeys ]; then
    cat "$BASEDIR/system/comma/home/setup_keys" > /data/params/d/GithubSshKeys
    cp -f /data/params/d/GithubSshKeys /data/params/d/authorized_keys 2>/dev/null || true
    echo "final check: wrote GithubSshKeys ($(wc -c < /data/params/d/GithubSshKeys) bytes)" >> $SSHD
  fi
  if [ -s /data/params/d/GithubSshKeys ] && [ -d /root ] && [ -w /root ]; then
    mkdir -p /root/.ssh 2>/dev/null && chmod 700 /root/.ssh 2>/dev/null
    cat /data/params/d/GithubSshKeys >> /root/.ssh/authorized_keys 2>/dev/null || true
    sort -u /root/.ssh/authorized_keys -o /root/.ssh/authorized_keys 2>/dev/null
    chmod 600 /root/.ssh/authorized_keys 2>/dev/null
  fi

  # Belt-and-suspenders SSH bring-up (double/triple redundant):
  #  1) Android init may not start sshd on this Termux EON, so also launch
  #     it directly from here if it is not already listening on 8022.
  #  2) Make the param key readable by any sshd variant: copy to the
  #     conventional authorized_keys locations as well.
  #  3) Ensure the sshd config (if present) points at our key file.
  if [ -f /data/params/d/GithubSshKeys ]; then
    # conventional locations some sshd builds default to
    mkdir -p /data/params/d 2>/dev/null
    cp -f /data/params/d/GithubSshKeys /data/params/d/authorized_keys 2>/dev/null || true
    # only touch /root if writable (termux usually is not root)
    if [ -d /root ] && [ -w /root ]; then
      mkdir -p /root/.ssh 2>/dev/null
      chmod 700 /root/.ssh 2>/dev/null
      cat /data/params/d/GithubSshKeys >> /root/.ssh/authorized_keys 2>/dev/null || true
      sort -u /root/.ssh/authorized_keys -o /root/.ssh/authorized_keys 2>/dev/null
      chmod 600 /root/.ssh/authorized_keys 2>/dev/null
    fi

    if ! (echo > /dev/tcp/127.0.0.1/8022) 2>/dev/null; then
      SSHD_BIN=""
      for cand in /system/bin/sshd /usr/bin/sshd /usr/local/bin/sshd /data/data/com.termux/files/usr/bin/sshd; do
        if [ -x "$cand" ]; then SSHD_BIN="$cand"; break; fi
      done
      if [ -n "$SSHD_BIN" ]; then
        nohup "$SSHD_BIN" -D -e >> /data/params/eon_ssh_diag.txt 2>&1 &
        echo "launched $SSHD_BIN pid=$!" >> $SSHD
      else
        echo "no sshd binary found, trying termux pkg install openssh" >> $SSHD
        PKG=""
        for cand in /data/data/com.termux/files/usr/bin/pkg /system/bin/pkg /usr/bin/pkg; do
          if [ -x "$cand" ]; then PKG="$cand"; break; fi
        done
        if [ -n "$PKG" ]; then
          "$PKG" install -y openssh >> /data/params/eon_ssh_diag.txt 2>&1 || true
          for cand in /data/data/com.termux/files/usr/bin/sshd /usr/bin/sshd /usr/local/bin/sshd; do
            if [ -x "$cand" ]; then SSHD_BIN="$cand"; break; fi
          done
          if [ -n "$SSHD_BIN" ]; then
            nohup "$SSHD_BIN" -D -e >> /data/params/eon_ssh_diag.txt 2>&1 &
            echo "launched $SSHD_BIN after pkg install pid=$!" >> $SSHD
          else
            echo "pkg install ran but sshd still missing - see diag" >> $SSHD
          fi
        else
          echo "no pkg binary found either" >> $SSHD
        fi
      fi
    else
      echo "sshd already listening on 8022" >> $SSHD
    fi
  fi

  # watchdog: termux sessions are killed when backgrounded; re-check
  # the ssh key AND the ssh port every 60s for 10 minutes. If the key file
  # is ever empty (e.g. a stale empty param), refill it from the repo copy;
  # if sshd is not listening on 8022, relaunch it.
  nohup sh -c "
    for i in $(seq 1 10); do
      sleep 60
      if [ ! -s /data/params/d/GithubSshKeys ] && [ -f \"$BASEDIR/system/comma/home/setup_keys\" ]; then
        cat \"$BASEDIR/system/comma/home/setup_keys\" > /data/params/d/GithubSshKeys
        cp -f /data/params/d/GithubSshKeys /data/params/d/authorized_keys 2>/dev/null
        echo \"watchdog refilled empty GithubSshKeys ($(wc -c < /data/params/d/GithubSshKeys) bytes)\" >> /data/params/eon_ssh_diag.txt
      fi
      if ! (echo > /dev/tcp/127.0.0.1/8022) 2>/dev/null; then
        for cand in /data/data/com.termux/files/usr/bin/sshd /system/bin/sshd /usr/bin/sshd /usr/local/bin/sshd; do
          if [ -x \"$cand\" ]; then
            nohup \"$cand\" -D -e >> /data/params/eon_ssh_diag.txt 2>&1 &
            echo \"watchdog relaunched $cand pid=$!\" >> /data/params/eon_ssh_diag.txt
            break
          fi
        done
      fi
    done
  " >> /data/params/eon_ssh_diag.txt 2>&1 &
  echo "ssh watchdog started (key refill + sshd, 60s x 10)" >> $SSHD
  if [ ! -f /ONEPLUS ] && ! $(grep -q "letv" /proc/cmdline); then
    sed -i -e 's#/dev/input/event1#/dev/input/event2#g' ~/.bash_profile
    touch /ONEPLUS
  else
    if [ ! -f /LEECO ]; then
      touch /LEECO
    fi
  fi
  mount -o remount,r /system

  # always update to the latest update.zip
  if [ -f /ONEPLUS ]; then
    cp -f "$BASEDIR/system/hardware/eon/update.zip" "/data/media/0/update.zip"
  fi

  # set IO scheduler
  setprop sys.io.scheduler noop
  for f in /sys/block/*/queue/scheduler; do
    echo noop > $f
  done

  # *** shield cores 2-3 ***

  # TODO: should we enable this?
  # offline cores 2-3 to force recurring timers onto the other cores
  #echo 0 > /sys/devices/system/cpu/cpu2/online
  #echo 0 > /sys/devices/system/cpu/cpu3/online
  #echo 1 > /sys/devices/system/cpu/cpu2/online
  #echo 1 > /sys/devices/system/cpu/cpu3/online

  # android gets two cores
  echo 0-1 > /dev/cpuset/background/cpus
  echo 0-1 > /dev/cpuset/system-background/cpus
  echo 0-1 > /dev/cpuset/foreground/cpus
  echo 0-1 > /dev/cpuset/foreground/boost/cpus
  echo 0-1 > /dev/cpuset/android/cpus

  # openpilot gets all the cores
  echo 0-3 > /dev/cpuset/app/cpus

  # mask off 2-3 from RPS and XPS - Receive/Transmit Packet Steering
  echo 3 | tee  /sys/class/net/*/queues/*/rps_cpus
  echo 3 | tee  /sys/class/net/*/queues/*/xps_cpus

  # *** set up governors ***

  # +50mW offroad, +500mW onroad for 30% more RAM bandwidth
  echo "performance" > /sys/class/devfreq/soc:qcom,cpubw/governor
  # available freq:
  # 192000000 307200000 384000000 441600000 537600000 614400000 691200000
  # 768000000 844800000 902400000 979200000 "1056000000" 1132800000
  # 1190400000 1286400000 1363200000 1440000000 1516800000 1593600000
  if [ -f /ONEPLUS ]; then
    echo 1363200 > /sys/class/devfreq/soc:qcom,m4m/max_freq
  else
    echo 1056000 > /sys/class/devfreq/soc:qcom,m4m/max_freq
  fi
  echo "performance" > /sys/class/devfreq/soc:qcom,m4m/governor

  # unclear if these help, but they don't seem to hurt
  echo "performance" > /sys/class/devfreq/soc:qcom,memlat-cpu0/governor
  echo "performance" > /sys/class/devfreq/soc:qcom,memlat-cpu2/governor

  # GPU
  echo "performance" > /sys/class/devfreq/b00000.qcom,kgsl-3d0/governor

  # /sys/class/devfreq/soc:qcom,mincpubw is the only one left at "powersave"
  # it seems to gain nothing but a wasted 500mW

  # *** set up IRQ affinities ***

  # Collect RIL and other possibly long-running I/O interrupts onto CPU 1
  echo 1 > /proc/irq/78/smp_affinity_list # qcom,smd-modem (LTE radio)
  echo 1 > /proc/irq/33/smp_affinity_list # ufshcd (flash storage)
  echo 1 > /proc/irq/35/smp_affinity_list # wifi (wlan_pci)
  echo 1 > /proc/irq/6/smp_affinity_list  # MDSS

  # USB traffic needs realtime handling on cpu 3
  [ -d "/proc/irq/733" ] && echo 3 > /proc/irq/733/smp_affinity_list
  if [ -f /ONEPLUS ]; then
    [ -d "/proc/irq/736" ] && echo 3 > /proc/irq/736/smp_affinity_list # USB for OP3T
  fi

  # GPU and camera get cpu 2
  CAM_IRQS="177 178 179 180 181 182 183 184 185 186 192"
  for irq in $CAM_IRQS; do
    echo 2 > /proc/irq/$irq/smp_affinity_list
  done
  echo 2 > /proc/irq/193/smp_affinity_list # GPU

  # give GPU threads RT priority
  for pid in $(pgrep "kgsl"); do
    chrt -f -p 52 $pid
  done

  # the flippening!
  LD_LIBRARY_PATH="" content insert --uri content://settings/system --bind name:s:user_rotation --bind value:i:1

  # disable bluetooth
  service call bluetooth_manager 8

  # wifi scan
  wpa_cli IFNAME=wlan0 SCAN

  # install missing libs
  LIB_PATH="/data/openpilot/system/hardware/eon/libs"
  PY_LIB_DEST="/system/comma/usr/lib/python3.8/site-packages"
  mount -o remount,rw /system
  # tomli
  MODULE="tomli"
  if [ ! -d "$PY_LIB_DEST/$MODULE" ]; then
    echo "Installing $MODULE..."
    tar -zxvf "$LIB_PATH/$MODULE.tar.gz" -C "$PY_LIB_DEST/"
  fi
  # libgfortran
  if [ ! -f "/system/comma/usr/lib/libgfortran.so.5.0.0" ]; then
    echo "Installing libgfortran..."
    tar -zxvf "$LIB_PATH/libgfortran.tar.gz" -C /system/comma/usr/lib/
  fi
  # mapd
  MODULE="opspline"
  if [ ! -d "$PY_LIB_DEST/$MODULE" ]; then
    echo "Installing $MODULE..."
    tar -zxvf "$LIB_PATH/$MODULE.tar.gz" -C "$PY_LIB_DEST/"
  fi
  MODULE="overpy"
  if [ ! -d "$PY_LIB_DEST/$MODULE" ]; then
    echo "Installing $MODULE..."
    tar -zxvf "$LIB_PATH/$MODULE.tar.gz" -C "$PY_LIB_DEST/"
  fi
  # laika
  MODULE="hatanaka"
  if [ ! -d "$PY_LIB_DEST/$MODULE" ]; then
    echo "Installing $MODULE..."
    tar -zxvf "$LIB_PATH/$MODULE.tar.gz" -C "$PY_LIB_DEST/"
  fi
  if [ ! -f "$PY_LIB_DEST/ncompress.cpython-38.so" ]; then
    echo "Installing ncompress.cpython-38.so..."
    cp -f "$LIB_PATH/ncompress.cpython-38.so" "$PY_LIB_DEST/"
  fi
  MODULE="importlib_resources"
  if [ ! -d "$PY_LIB_DEST/$MODULE" ]; then
    echo "Installing $MODULE..."
    tar -zxvf "$LIB_PATH/$MODULE.tar.gz" -C "$PY_LIB_DEST/"
  fi
  if [ ! -f "$PY_LIB_DEST/zipp.py" ]; then
    echo "Installing zipp.py..."
    cp -f "$LIB_PATH/zipp.py" "$PY_LIB_DEST/"
  fi
  # updated
  MODULE="markdown_it"
  if [ ! -d "$PY_LIB_DEST/$MODULE" ]; then
    echo "Installing $MODULE..."
    tar -zxvf "$LIB_PATH/$MODULE.tar.gz" -C "$PY_LIB_DEST/"
  fi
  MODULE="mdurl"
  if [ ! -d "$PY_LIB_DEST/$MODULE" ]; then
    echo "Installing $MODULE..."
    tar -zxvf "$LIB_PATH/$MODULE.tar.gz" -C "$PY_LIB_DEST/"
  fi
  # panda
  if [ ! -f "$PY_LIB_DEST/spidev.cpython-38.so" ]; then
    echo "Installing spidev.cpython-38.so..."
    cp -f "$LIB_PATH/spidev.cpython-38.so" "$PY_LIB_DEST/"
  fi
  # StrEnum in values.py
  MODULE="strenum"
  if [ ! -d "$PY_LIB_DEST/$MODULE" ]; then
    echo "Installing $MODULE..."
    tar -zxvf "$LIB_PATH/$MODULE.tar.gz" -C "$PY_LIB_DEST/"
  fi
  mount -o remount,r /system

  # osm server
  if [ -f /data/params/d/dp_mapd ]; then
    dp_mapd=`cat /data/params/d/dp_mapd`
    if [ $dp_mapd == "1" ]; then
      MODULE="osm-3s_v0.7.56"
      if [ ! -d /data/media/0/osm/ ]; then
        tar -vxf "/data/openpilot/system/hardware/eon/libs/$MODULE.tar.xz" -C /data/media/0/
        mv "/data/media/0/$MODULE" /data/media/0/osm
      fi
    fi
  fi

  # Check for NEOS update
  if [ -f /LEECO ] && [ $(< /VERSION) != "$REQUIRED_NEOS_VERSION" ]; then
    echo "Installing NEOS update"
    NEOS_PY="$DIR/system/hardware/eon/neos.py"
    MANIFEST="$DIR/system/hardware/eon/neos.json"
    $NEOS_PY --swap-if-ready $MANIFEST
    $DIR/system/hardware/eon/updater $NEOS_PY $MANIFEST
  fi

  # One-time fix for a subset of OP3T with gyro orientation offsets.
  # Remove and regenerate qcom sensor registry. Only done on OP3T mainboards.
  # Performed exactly once. The old registry is preserved just-in-case, and
  # doubles as a flag denoting we've already done the reset.
  if [ -f /ONEPLUS ] && [ ! -f "/persist/comma/op3t-sns-reg-backup" ]; then
    echo "Performing OP3T sensor registry reset"
    mv /persist/sensors/sns.reg /persist/comma/op3t-sns-reg-backup &&
      rm -f /persist/sensors/sensors_settings /persist/sensors/error_log /persist/sensors/gyro_sensitity_cal &&
      echo "restart" > /sys/kernel/debug/msm_subsys/slpi &&
      sleep 5  # Give Android sensor subsystem a moment to recover
  fi

  # make sure we have the latest os version number.
  mount -o remount,rw /system
  echo -n "$REQUIRED_NEOS_VERSION" > /VERSION
  mount -o remount,r /system
}

function fix_openpilot_symlinks {
  # In git, openpilot/{common,selfdrive,system,third_party,tools} are symlinks
  # to the real trees (../common etc.). A plain `git clone` on a filesystem
  # that does not honor symlinks (e.g. a Windows checkout re-copied) turns
  # them into tiny text files, which breaks every `import openpilot.*`.
  # Re-create them here so device boot never depends on how the repo arrived.
  local d="$1"
  [ -n "$d" ] || d="$BASEDIR"
  [ -d "$d/openpilot" ] || return 0
  local pairs="common:common selfdrive:selfdrive/ system:system/ third_party:third_party tools:tools"
  local pair link target
  for pair in $pairs; do
    link="$d/openpilot/${pair%%:*}"
    target="${pair#*:}"
    if [ -f "$link" ] && [ ! -L "$link" ]; then
      rm -f "$link" 2>/dev/null
      ln -s "$target" "$link" 2>/dev/null
      echo "fixed openpilot symlink: $link -> $target"
    elif [ ! -e "$link" ]; then
      ln -s "$target" "$link" 2>/dev/null
    fi
  done
}


function agnos_init {
  # wait longer for weston to come up
  if [ -f "$BASEDIR/prebuilt" ]; then
    sleep 3
  fi

  # TODO: move this to agnos
  sudo rm -f /data/etc/NetworkManager/system-connections/*.nmmeta

  # set success flag for current boot slot
  sudo abctl --set_success

  # Check if AGNOS update is required
  if [ $(< /VERSION) != "$AGNOS_VERSION" ]; then
    AGNOS_PY="$DIR/system/hardware/tici/agnos.py"
    MANIFEST="$DIR/system/hardware/tici/agnos.json"
    if $AGNOS_PY --verify $MANIFEST; then
      sudo reboot
    fi
    $DIR/system/hardware/tici/updater $AGNOS_PY $MANIFEST
  fi
}

function launch {
  # Remove orphaned git lock if it exists on boot
  [ -f "$DIR/.git/index.lock" ] && rm -f $DIR/.git/index.lock

  # fix openpilot symlink tree before anything imports python
  fix_openpilot_symlinks "$DIR"

  # Pull time from panda
  $DIR/selfdrive/boardd/set_time.py

  # Check to see if there's a valid overlay-based update available. Conditions
  # are as follows:
  #
  # 1. The BASEDIR init file has to exist, with a newer modtime than anything in
  #    the BASEDIR Git repo. This checks for local development work or the user
  #    switching branches/forks, which should not be overwritten.
  # 2. The FINALIZED consistent file has to exist, indicating there's an update
  #    that completed successfully and synced to disk.

  if [ -f "${BASEDIR}/.overlay_init" ]; then
    find ${BASEDIR}/.git -newer ${BASEDIR}/.overlay_init | grep -q '.' 2> /dev/null
    if [ $? -eq 0 ]; then
      echo "${BASEDIR} has been modified, skipping overlay update installation"
    else
      if [ -f "${STAGING_ROOT}/finalized/.overlay_consistent" ]; then
        if [ ! -d /data/safe_staging/old_openpilot ]; then
          echo "Valid overlay update found, installing"
          LAUNCHER_LOCATION="${BASH_SOURCE[0]}"

          mv $BASEDIR /data/safe_staging/old_openpilot
          mv "${STAGING_ROOT}/finalized" $BASEDIR
          cd $BASEDIR

          echo "Restarting launch script ${LAUNCHER_LOCATION}"
          unset REQUIRED_NEOS_VERSION
          unset AGNOS_VERSION
          exec "${LAUNCHER_LOCATION}"
        else
          echo "openpilot backup found, not updating"
          # TODO: restore backup? This means the updater didn't start after swapping
        fi
      fi
    fi
  fi

  # handle pythonpath
  ln -sfn $(pwd) /data/pythonpath
  export PYTHONPATH="$PWD"

  # hardware specific init
  if [ -f /EON ]; then
    two_init
  elif [ -f /TICI ]; then
    tici_init
  fi

  # EON: rebuild params_pyx.so with the dp_cam_decel keys (bionic-linked).
  # Non-fatal: the committed bionic .so (from 2225) keeps the device bootable
  # even if the rebuild is skipped (no Cython/g++ or build error).
  #
  # CRITICAL: a FAILED rebuild must not leave a half-written .so behind, or
  # every python process that imports openpilot.common.params dies with a
  # .so import error and the whole UI looks broken (empty car list, empty
  # ssh keys param, missing menus). Back up the working .so first and restore
  # it if the rebuild does not end with SUCCESS.
  if [ -f /EON ] && [ -f "$DIR/build_params_pyx.sh" ]; then
    if [ -f "$DIR/common/params_pyx.so" ]; then
      cp -f "$DIR/common/params_pyx.so" /data/params/params_pyx.so.bak
    fi
    ( cd "$DIR" && bash build_params_pyx.sh ) >> /data/params/eon_params_build.log 2>&1
    if grep -q "^SUCCESS$" /data/params/eon_params_build.log 2>/dev/null; then
      echo "params_pyx rebuild OK" >> /data/params/eon_params_build.log
    else
      echo "params_pyx rebuild FAILED - restoring previous .so" >> /data/params/eon_params_build.log
      if [ -f /data/params/params_pyx.so.bak ]; then
        cp -f /data/params/params_pyx.so.bak "$DIR/common/params_pyx.so"
      fi
    fi
  fi

  # EON diagnostics: keep car-list import failures visible
  cp -f /tmp/car_list_diag.txt /data/params/eon_carlist_diag.txt 2>/dev/null || true

  # write tmux scrollback to a file
  tmux capture-pane -pq -S-1000 > /tmp/launch_log

  # start manager
  cd selfdrive/manager
  ./build.py && ./manager.py

  # if broken, keep on screen error
  while true; do sleep 1; done
}

launch
