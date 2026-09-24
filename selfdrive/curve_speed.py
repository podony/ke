from openpilot.common.conversions import Conversions as CV
from openpilot.common.params import Params

MIN_CURVE_SPEED = 32. * CV.KPH_TO_MS  # ~32 kph floor, never decel below this
CURV_FACTOR_DEFAULT = 0.98


def get_curve_speed_kph(v_ego, curvatures, factor=CURV_FACTOR_DEFAULT):
  """Return a curve speed limit in kph, or 0 if no curve is detected.

  Math ported from boltpilot scc_smoother.cal_curve_speed:
  a_y_max drops with speed (comfort), v = sqrt(a_y_max / curvature).
  """
  if len(curvatures) < 2:
    return 0.
  curv = (curvatures[-1] + curvatures[-2]) / 2.
  if abs(curv) < 1e-4:
    return 0.
  a_y_max = 2.975 - v_ego * 0.0375  # ~2.6 @ 25mph, ~1.85 @ 75mph
  a_y_max = max(a_y_max, 0.5)
  v_curvature = (a_y_max / abs(curv)) ** 0.5
  model_speed = v_curvature * 0.85 * factor
  if model_speed < v_ego:
    return max(model_speed, MIN_CURVE_SPEED) * CV.MS_TO_KPH
  return 0.


class CurveDecelHelper:
  """Caps the set speed on curves. Self-contained on purpose: reads only
  lateralPlan curvatures + CS.vEgo so it plugs into stock 2225 controlsd."""

  def __init__(self, params: Params):
    self.params = params
    try:
      self.factor = float(params.get("dp_curve_decel_curv_factor", encoding="utf-8") or CURV_FACTOR_DEFAULT)
    except ValueError:
      self.factor = CURV_FACTOR_DEFAULT

  @property
  def enabled(self):
    return self.params.get_bool("dp_curve_decel")

  def get_speed_limit_kph(self, v_ego, curvatures):
    if not self.enabled:
      return 0.
    return get_curve_speed_kph(v_ego, curvatures, self.factor)
