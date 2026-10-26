#!/usr/bin/env bash
# EON ssh keepalive: refill empty key param, merge keys into every
# authorized_keys an sshd variant may read, and relaunch sshd if port 8022
# died. Extracted from launch_chffrplus.sh (the inline sh -c string with
# escaped quotes was untestable and had the same blind-append corruption:
# a target file without a trailing newline fuses two keys into one garbage
# line, which is the "ssh key changed after install" lockout).
#
# Usage: eon_ssh_watchdog.sh [BASEDIR]   (default /data/openpilot)
if [ "$1" = "--merge-once" ]; then
  MERGE_ONLY=1
  shift
fi
BASEDIR="${1:-/data/openpilot}"
DIAG=/data/params/eon_ssh_diag.txt
PARAM=/data/params/d/GithubSshKeys
SETUP="$BASEDIR/system/comma/home/setup_keys"

merge_into() {
  # $1 = authorized_keys target. Merge existing + param, dedup, atomic write.
  local tgt="$1" dir tmp
  dir="$(dirname "$tgt")"
  mkdir -p "$dir" 2>/dev/null || return 0
  chmod 700 "$dir" 2>/dev/null
  tmp="$tgt.merge.tmp"
  # `&& echo` after each cat: a source file without a trailing newline would
  # otherwise fuse its last line with the next file's first line BEFORE sort
  # runs. The injected blank line is dropped by the grep below.
  { [ -f "$tgt" ] && cat "$tgt" && echo; [ -f "$PARAM" ] && cat "$PARAM" && echo; } \
    | tr -d '\r' | grep -v 'PRIVATE KEY' | grep -v '^[[:space:]]*$' | sort -u > "$tmp" 2>/dev/null
  if [ -s "$tmp" ]; then
    cat "$tmp" > "$tgt"
    chmod 600 "$tgt" 2>/dev/null
  fi
  rm -f "$tmp"
}

if [ "${MERGE_ONLY:-0}" = "1" ]; then
  [ -s "$PARAM" ] || exit 1
  merge_into /data/params/d/authorized_keys
  merge_into /data/data/com.termux/files/home/.ssh/authorized_keys
  merge_into /root/.ssh/authorized_keys
  exit 0
fi

for i in $(seq 1 10); do
  sleep 60

  # Refill an empty param from the repo copy (merge, never overwrite).
  if [ ! -s "$PARAM" ] && [ -f "$SETUP" ]; then
    { [ -f "$PARAM" ] && cat "$PARAM" && echo; cat "$SETUP" && echo; } \
      | tr -d '\r' | grep -v 'PRIVATE KEY' | grep -v '^[[:space:]]*$' | sort -u > "$PARAM.tmp" 2>/dev/null
    if [ -s "$PARAM.tmp" ]; then
      cat "$PARAM.tmp" > "$PARAM"
      echo "$(date) watchdog refilled empty GithubSshKeys ($(wc -c < "$PARAM") bytes)" >> "$DIAG"
    fi
    rm -f "$PARAM.tmp"
  fi

  if [ -s "$PARAM" ]; then
    merge_into /data/params/d/authorized_keys
    merge_into /data/data/com.termux/files/home/.ssh/authorized_keys
    merge_into /root/.ssh/authorized_keys
  fi

  if ! (echo > /dev/tcp/127.0.0.1/8022) 2>/dev/null; then
    for hk in /data/params/ssh_hostkeys/ssh_host_*_key; do
      [ -f "$hk" ] || continue
      [ -f "/data/data/com.termux/files/usr/etc/ssh/$(basename "$hk")" ] || \
        cp "$hk" "/data/data/com.termux/files/usr/etc/ssh/$(basename "$hk")" 2>/dev/null
    done
    for cand in /data/data/com.termux/files/usr/bin/sshd /system/bin/sshd /usr/bin/sshd /usr/local/bin/sshd; do
      if [ -x "$cand" ]; then
        nohup "$cand" -D -e >> "$DIAG" 2>&1 &
        echo "$(date) watchdog relaunched $cand pid=$!" >> "$DIAG"
        break
      fi
    done
  fi
done
