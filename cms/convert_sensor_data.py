import math
from cms.convert_device_id    import convert_device_id

def convert_sensor_data(s):

  s.update({"date":s["datetime"][0:10], "time":s["datetime"][11:23]})

  # 子機のidと座標
  s["device_id"],tmp_pos_x,tmp_pos_y = convert_device_id(s["device_id"])
  s.update({"pos_x":tmp_pos_x, "pos_y":tmp_pos_y})

  # センサの種類
  if(s["sensor_id"] == 0):
    s["sensor_id"] = "初期データ"

  # 加速度データの計算
  elif(s["sensor_id"] == 28):
    s["sensor_id"] = "加速度"
    s["ac"] = convert_acceleration(s)

  # 照度データの計算
  elif(s["sensor_id"] == 36):
    s["sensor_id"] = "照度"
    s["ilu"] = convert_illuminance(s)

  # 赤外線データの計算
  elif(s["sensor_id"] == 64):
    s["sensor_id"] = "赤外線"
    s["tu"] = convert_temperature(s)

  # 該当なし
  else:
    s["sensor_id"] = "Error"

  return s


def convert_acceleration(s):
  tmp_ax  = s["sensor_value"][-8:-6]
  tmp_ay  = s["sensor_value"][-6:-4]
  tmp_az  = s["sensor_value"][-4:-2]  
  tmp_ac = 0
  const =  1.9844 / 127 * 9.8067

  for ac in [tmp_ax, tmp_ay, tmp_az]:
    if(len(ac) == 0):
      ac = "0"
      
    ac = int("0x" + ac, 0)

    if(ac < 128):
      ac = round(ac * const, 4) 
    else:
      ac = -round((255 - ac + 1) * const, 4)

    tmp_ac += ac**2

  tmp_ac = round(math.sqrt(tmp_ac), 4)

  return tmp_ac


def convert_illuminance(s):
  tmp_ilu = s["sensor_value"][-8:-4]

  if(len(tmp_ilu) == 0):
    tmp_ilu = "0"

  tmp_ilu = int(int("0x" + tmp_ilu, 0) / 1023 * 3 *100 / 0.29)

  return tmp_ilu


def convert_temperature(s):
    tmp_vu = s["sensor_value"][-8:-4]
    tmp_vu = int("0x" + tmp_vu, 0)

    if(tmp_vu < 32767):
      tmp_vu = round(tmp_vu)* 1.5625*(10**-7)
    else:
      tmp_vu = -round((65535 - tmp_vu + 1))* 1.5625*(10**-7)

    tmp_tu = s["sensor_value"][-4:]
    tmp_tu = int("0x" + tmp_tu, 0) / 128

    ## 定数 ##
    S0 = 6*(10**-14)
    a1 = 1.75*(10**3)
    a2 = -1.678*(10**-5)
    Tdie = tmp_tu 
    Tref = 298.15
    Vobj = tmp_vu 
    b0 = -2.94*(10**-5)
    b1 = -5.7*(10**-7)
    b2 = 4.63*(10**-9)
    c2 = 13.4

    S = S0*(1 + a1*(Tdie - Tref) +a2*((Tdie - Tref)**2))
    Vos = b0 + b1*(Tdie - Tref) + b2*((Tdie - Tref)**2)
    fVobj = (Vobj - Vos) + c2*((Vobj - Vos)**2)
    tmp_tu = str(math.sqrt(math.sqrt((Tdie**4) + (fVobj / S))))[:4]
    tmp_tu = float(tmp_tu)

    return tmp_tu

