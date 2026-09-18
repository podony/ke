import re
old = open('_old_params_full.cc', encoding='utf-8').read()
m = re.search(r'std::unordered_map<std::string, uint32_t> keys = \{(.*?)\n\};', old, re.S)
body = m.group(1)
entries = re.findall(r'\{\s*"((?:[^"\\]|\\.)*)",\s*(\w+)\s*\}', body)
print(len(entries))
missing = ['CarParams','DoReboot','DongleId','IMEI','IsMetric','IsOnroad','IsTakingSnapshot','TrainingVersion','Version','carFingerprint','dp_0813','dp_alka','dp_cam_decel','dp_cam_decel_bump_dist','dp_cam_decel_bump_speed','dp_cam_decel_end','dp_cam_decel_safety_factor','dp_cam_decel_start','dp_car_dashcam_mode_removal','dp_car_list','dp_device_auto_shutdown','dp_device_auto_shutdown_in','dp_device_disable_temp_check','dp_device_enable_comma_registration','dp_fileserv','dp_hkg_min_steer_speed_bypass','dp_lat_lane_change_assist_speed','dp_lat_lane_priority_mode','dp_lat_lane_priority_mode_speed_based','dp_logging','dp_long_accel_profile','dp_long_de2e','dp_long_missing_lead_warning','dp_long_use_df_tune','dp_long_use_krkeegen_tune','dp_mapd','dp_mapd_vision_turn_control','dp_no_fan_ctrl','dp_no_gps_ctrl','dp_otisserv','dp_toyota_enhanced_bsm','dp_toyota_zss','dp_vag_timebomb_bypass','error_description','uniqueID']
found = {k for k,_ in entries}
still = [k for k in missing if k not in found]
print("still not found:", still)
for k,t in entries:
    if k in ('CarParams','Version','DongleId','IMEI','IsOnroad','TrainingVersion'):
        print(k, t)
