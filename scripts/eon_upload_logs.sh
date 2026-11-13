#!/bin/bash
# ============================================================================
# Standalone EON diag-log exfiltration — works with NO SSH from the PC.
# Collects diag files + a fresh eon_diag.sh report, pushes them to the
# `logs` branch of origin. Called from launch_chffrplus.sh on every boot
# and from controlsd's crash handler (once per boot).
#
# One-time setup on the device (repo-scoped fine-grained PAT for podony/ke):
#   echo ghp_XXXXXXXX > /data/params/d/dp_git_token
#
# Safe to run any time, read-only w.r.t. openpilot state.
# ============================================================================
BASEDIR="${BASEDIR:-/data/openpilot}"
diagdir="/data/params"
logdir="$BASEDIR/eon_logs"
uplog="$diagdir/eon_log_upload.txt"
mkdir -p "$logdir"

# Fresh python-env / brand-import snapshot (eon_diag.sh only reads state and
# writes its own report file).
if [ -f "$BASEDIR/scripts/eon_diag.sh" ]; then
  timeout 90 sh "$BASEDIR/scripts/eon_diag.sh" >/dev/null 2>&1
fi

for f in eon_ssh_diag.txt eon_apk_diag.txt eon_carlist_diag.txt \
         eon_controlsd_crash.txt eon_manager_boot.log eon_diag_report.txt \
         eon_libs_diag.txt; do
  [ -s "$diagdir/$f" ] && cp -f "$diagdir/$f" "$logdir/$f"
done

{
  echo "=== $(date) EON param snapshot ==="
  echo "GithubSshKeys size: $(wc -c < /data/params/d/GithubSshKeys 2>/dev/null || echo missing)"
  echo "mappy installed: $(pm list packages 2>/dev/null | grep -c mappyobn || echo 0)"
  echo "sshd process: $(pgrep -c sshd 2>/dev/null || echo 0)"
  echo "controlsd process: $(pgrep -fc controlsd 2>/dev/null || echo 0)"
  echo "openpilot HEAD: $(cd "$BASEDIR" && git log --oneline -1 2>/dev/null)"
  echo "carlist_diag last 20 lines:"
  tail -20 "$diagdir/eon_carlist_diag.txt" 2>/dev/null || echo "(none)"
} > "$logdir/summary.txt"

# Also refresh the USB-HTTP serve dir (no-token channel, see serve_eon_logs
# in launch_chffrplus.sh; PC: curl http://172.30.1.1:8099/<file>)
servedir="$diagdir/eon_serve"
mkdir -p "$servedir"
cp -f "$logdir"/*.txt "$servedir/" 2>/dev/null

cd "$BASEDIR" || exit 0
origin_url=$(git remote get-url origin 2>/dev/null)
if [ -z "$origin_url" ]; then
  echo "no origin $(date)" >> "$uplog"; exit 0
fi
case "$origin_url" in
  http://*|https://*) ;;
  *) echo "origin not https, skip $(date)" >> "$uplog"; exit 0 ;;
esac

token=$(cat /data/params/d/dp_git_token 2>/dev/null | tr -d '\r\n ')
if [ -z "$token" ]; then
  echo "NO dp_git_token -> push skipped $(date). Set: echo <PAT> > /data/params/d/dp_git_token" >> "$uplog"
  exit 0
fi

git remote set-url origin "https://x-access-token:$token@github.com/podony/ke.git" 2>/dev/null
git worktree add -q -f /tmp/eon_logs_wt logs 2>/dev/null \
  || { git branch -q logs 2>/dev/null; git worktree add -q -f /tmp/eon_logs_wt logs 2>/dev/null; }
if [ -d /tmp/eon_logs_wt ]; then
  cp -rf "$logdir/." /tmp/eon_logs_wt/eon_logs/ 2>/dev/null
  ( cd /tmp/eon_logs_wt && \
    git -c user.email="eon@openpilot" -c user.name="EON" \
      commit -qam "eon logs $(date +%s)" --allow-empty 2>/dev/null; \
    timeout 20 git push -qf origin logs 2>>"$uplog" \
      && echo "push OK $(date)" >> "$uplog" \
      || echo "push FAIL rc=$? $(date)" >> "$uplog" )
  git worktree remove -qf /tmp/eon_logs_wt 2>/dev/null
fi
# never leave the token in .git/config
git remote set-url origin "$origin_url" 2>/dev/null
