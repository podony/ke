#!/usr/bin/bash
# ============================================================================
# BRUNCH installer for the Bolt EUV EON (Termux).
#
#   usage:  bash eon_installer.sh [branch]      (default: merge/boltpilot-camera-decel)
#
# v2 (2026-11-13) - the v1 pattern `rm -fr /data/openpilot && git clone ...`
# bricked devices: ANY clone failure (missing branch arg -> `git clone -b ""`,
# typo'd branch, flaky WiFi) happened AFTER the old install was already
# deleted, leaving /data/openpilot gone and no continue.sh -> the EON boots
# to the stock intro screen ("looks like nothing was ever installed").
# Reproduced in F:\cording\c2\_eon_install_sim (S2/S3/S4 all BRICKED).
#
# v2 rules:
#   1. never touch the existing install until a COMPLETE clone exists
#   2. clone into /data/openpilot.new, verify required files, retry x3
#   3. atomic swap (mv), keep previous version as /data/openpilot.old
#   4. reboot ONLY after a verified swap; on failure the device still boots
#   5. every step logged to /data/params/eon_install.log (survives reboots)
# ============================================================================
BRANCH="${1:-merge/boltpilot-camera-decel}"
REPO="https://github.com/podony/ke"
LOG=/data/params/eon_install.log
NEW=/data/openpilot.new
OLD_KEEP=/data/openpilot.old

mkdir -p /data/params

# One installer at a time: an SSH wrapper that retries keys re-runs the whole
# command per attempt, which launched 4 concurrent installers on 2026-11-14
# (racing on /data/openpilot.new). mkdir is atomic; trap cleans the lock.
LOCK=/data/params/eon_install.lock
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "FAIL: another eon_installer is running ($LOCK exists)."
  echo "      if stale: rmdir $LOCK and re-run."
  exit 1
fi
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

# Plain append redirect, NOT `exec > >(tee ...)`: on 2026-11-14 the tee
# child died with the SSH pipe and eon_install.log was never created.
# Watch progress from a second shell:  tail -f /data/params/eon_install.log
exec >> "$LOG" 2>&1
echo "==== eon_installer v2.1 $(date) branch=$BRANCH ===="

fail() {
  echo "FAIL: $1"
  echo "existing /data/openpilot was NOT touched; device still bootable"
  rm -fr "$NEW"
  exit 1
}

# --- 0. sanity: branch must be a real branch on the remote ------------------
[ -n "$1" ] || echo "no branch argument -> defaulting to $BRANCH"
LSR=$(git ls-remote --heads "$REPO" 2>&1)
if [ $? -ne 0 ]; then
  echo "$LSR"
  fail "cannot reach $REPO (network/WiFi down?) - nothing was changed"
fi
if ! echo "$LSR" | grep -q "refs/heads/$BRANCH\$"; then
  echo "available branches:"
  echo "$LSR" | sed 's#.*refs/heads/#  #'
  fail "branch '$BRANCH' does not exist on $REPO"
fi

# --- 1. clone next to (not instead of) the running install ------------------
rm -fr "$NEW"
ok=NO
for try in 1 2 3; do
  echo "clone attempt $try..."
  if git clone "$REPO" -b "$BRANCH" --single-branch --depth=1 "$NEW"; then
    ok=YES
    break
  fi
  rm -fr "$NEW"
  sleep 5
done
[ "$ok" = YES ] || fail "git clone failed 3x (network? GitHub down?)"

# --- 2. verify the clone is a bootable tree before swapping -----------------
for req in launch_openpilot.sh launch_chffrplus.sh launch_env.sh \
           selfdrive/manager/manager.py scripts/eon_installer.sh; do
  [ -f "$NEW/$req" ] || fail "clone incomplete: missing $req"
done

# --- 3. atomic swap, keep a rollback copy -----------------------------------
rm -fr "$OLD_KEEP"
if [ -d /data/openpilot ]; then
  mv /data/openpilot "$OLD_KEEP" || fail "could not move old install aside"
fi
mv "$NEW" /data/openpilot || {
  [ -d "$OLD_KEEP" ] && mv "$OLD_KEEP" /data/openpilot
  fail "could not move new install into place (rolled back)"
}

# --- 4. Termux boot hook ------------------------------------------------------
# v1 APPENDED its block on every install, so N reinstalls left N stale
# cd/exec blocks in continue.sh. Write it fresh instead.
CONT=/data/data/com.termux/files/continue.sh
{
  echo "#!/usr/bin/bash"
  echo "cd /data/openpilot"
  echo "exec ./launch_openpilot.sh"
} > "$CONT" && chmod u+x "$CONT" ||
  fail "could not write continue.sh (Termux data missing?)"

echo "==== install OK $(date): branch=$BRANCH, previous version kept at $OLD_KEEP ===="
sync   # the log must survive the reboot
reboot
