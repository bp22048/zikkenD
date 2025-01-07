import sys
import hakosim
import numpy
import time
import math
import pprint
import pygame
from pygame.locals import *

# 目的地

def destination(index=None):
    # 複数の目的地をリストとして定義
    destinations = [
        {'x': 50, 'y': 0, 'z': 3},
        {'x': -5, 'y': -5, 'z': 3},
        {'x': 15, 'y': 10, 'z': 3},
        {'x': 3, 'y': 0, 'z': 3}
    ]
    # 指定されたインデックスの目的地を返す
    if index is not None and 0 <= index < len(destinations):
        return destinations[index]
    # デフォルトで最初の目的地を返す
    return destinations[0]

def fly_to_destination(client,dist):
    drone_pos = debug_pos(client)
    axis = calculate_axis(round(drone_pos['x'],3),round(drone_pos['y'],3),dist['x'],dist['y'])
    while axis != [0.0, 0.0, 0.0, 0.0]:
        drone_pos = debug_pos(client)
        axis = calculate_axis(round(drone_pos['x'],3),round(drone_pos['y'],3),dist['x'],dist['y'])
        axis = avoidance(client,axis)
        drone_control(client,axis)
        #time.sleep(1)
    time.sleep(5)
    drone_pos = debug_pos(client)
    delta_x = round(drone_pos['x'],3) - dist['x']
    delta_y = round(drone_pos['y'],3) - dist['y']
    print("誤差:x=",delta_x,",y=",delta_y)

# 障害物回避
def avoidance(client,axis):
    
    lidarData = client.getLidarData()
    #if (len(lidarData.point_cloud)<3):
    #    print("NO")
    #else:
        #print(f"len: {len(lidarData.point_cloud)}")
    points = parse_lidarData(lidarData)
    #print("\tReading:time_stamp: %d number_of_points: %d"% (lidarData.time_stamp, len(points)))
    #print(points)
    distances = numpy.sqrt(points[:, 0]**2 + points[:, 1]**2 + points[:, 2]**2)  # 各点の距離を計算
    close_obstacles = distances[distances<9.0]
    if len(close_obstacles) > 0:
        print(f"Obstacle detected: {len(close_obstacles)} points within 9m.")
        axis = [0.0, 0.0, 0.0, 0.0]
    #else:
        #print("No close obstacles detected. Moving to target position.")
    return axis

def parse_lidarData(data):
    #reshape array of floats to array of[X,Y,Z]
    points = numpy.array(data.point_cloud, dtype=numpy.dtype('f4'))
    points = numpy.reshape(points, (int(points.shape[0]/3),3))
    return points

#ドローンの起動、停止
def motor_onoff(client):
    data = client.getGameJoystickData()
    data['button'] = list(data['button'])
    data['button'][0] = True
    client.putGameJoystickData(data)
    time.sleep(1)
    data['button'][0] = False
    client.putGameJoystickData(data)

#ドローンの移動指示
def drone_control(client,axis):
    data = client.getGameJoystickData()
    data['axis'] = list(data['axis'])
    data['axis'] = axis
    client.putGameJoystickData(data)
    return data

#ドローンの航行する方向を現在地と目的地から算出、weightで速度指定(1が最大、2,3と増えるごとに遅くなる)
def calculate_axis(current_x, current_y, target_x, target_y, weight=1.5):
    delta_x = target_x - current_x
    delta_y = target_y - current_y
    bigger = max(abs(delta_x),abs(delta_y))
    
    if bigger == 0:
        bigger = 1
    #print("delta_y = ",delta_y,"delta_x = ",delta_x)
    bigger *= weight
    l_r = delta_y / bigger
    f_b = delta_x / bigger
    if (delta_y < 0)and(l_r < 0)or(delta_y >= 0)and(l_r >= 0): 
        l_r *= -1
    if (delta_x < 0)and(f_b < 0)or(delta_x >= 0)and(f_b >= 0): 
        f_b *= -1
    #print(l_r,",",f_b)
    if (abs(delta_y) < 2)and(abs(delta_x) < 2):
        axis = [0.0, 0.0, 0.0, 0.0]
    else :
        axis = [0.0, 0.0, l_r, f_b]
    #print("axis = ",axis)
    return axis

# キーボード操作
def keyboard_control(client: hakosim.MultirotorClient): 
    pygame.init()
    print("keyboard_control mode")
    destination = debug_pos(client)
    try:
        while True:
            pygame.display.set_mode((100, 100))
            
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == K_e:
                        motor_onoff(client)
                    if event.key == K_w:
                        print("front")
                        data = drone_control(client,[0.0, 0.0, 0.0, -1.0])
                    if event.key == K_s:
                        print("back")
                        data = drone_control(client,[0.0, 0.0, 0.0, 1.0])
                    if event.key == K_a:
                        print("left")
                        data = drone_control(client,[0.0, 0.0, -1.0, 0.0])
                    if event.key == K_d:
                        print("right")
                        data = drone_control(client,[0.0, 0.0, 1.0, 0.0])
                    # up down
                    if event.key == K_UP:
                        print("up")
                        data = drone_control(client,[0.0, -1.0, 0.0, 0.0])
                    if event.key == K_DOWN:
                        print("down")
                        data = drone_control(client,[0.0, 1.0, 0.0, 0.0])
                    if event.key == K_b:
                        print("stop")
                        data = drone_control(client,[0.0, 0.0, 0.0, 0.0])
                    if event.key == K_LEFT:
                        print("yaw_left")
                        data = drone_control(client,[-1.0, 0.0, 0.0, 0.0])
                    if event.key == K_RIGHT:
                        print("yaw_right")
                        data = drone_control(client,[1.0, 0.0, 0.0, 0.0])
                    if event.key == K_x:
                        lidarData = client.getLidarData()
                        if (len(lidarData.point_cloud)<3):
                            print("NO")
                        else:
                            print(f"len: {len(lidarData.point_cloud)}")
                        points = parse_lidarData(lidarData)
                        print("\tReading:time_stamp: %d number_of_points: %d"% (lidarData.time_stamp, len(points)))
                        print(points)
                        distances = numpy.sqrt(points[:, 0]**2 + points[:, 1]**2 + points[:, 2]**2)  # 各点の距離を計算
                        print(distances)
                    if event.key == K_f:
                        pygame.quit()
                        return 0
                    destination = debug_pos(client)
                if event.type == pygame.KEYUP:
                    if event.key == (K_w)or(K_s)or(K_a)or(K_d)or(K_UP)or(K_DOWN)or(K_LEFT)or(K_RIGHT):
                        data = drone_control(client,[0.0, 0.0, 0.0, 0.0])
            
    except KeyboardInterrupt:
        # Ctrl+Cが押されたときにジョイスティックをクリーンアップ
        pygame.quit()
    return 0

# デバッグ用: ドローンの現在位置と姿勢を表示
def debug_pos(client):
    pose = client.simGetVehiclePose()
    #print(f"POS : {pose.position.x_val} {pose.position.y_val} {pose.position.z_val}")
    roll, pitch, yaw = hakosim.hakosim_types.Quaternionr.quaternion_to_euler(pose.orientation)
    #print(f"ANGLE: {math.degrees(roll)} {math.degrees(pitch)} {math.degrees(yaw)}")
    destination = {'x': pose.position.x_val, 'y': pose.position.y_val, 'z': pose.position.z_val, 'yaw': math.degrees(yaw)}
    return destination

# プログラムのメイン処理
def main():
    # 引数チェック
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <config_path>")
        return 1

    # 箱庭ドローンを走査するためのクライアントとオブジェクトを取得
    client = hakosim.MultirotorClient(sys.argv[1])
    # クライアントオブジェクトの初期化
    client.confirmConnection()
    client.enableApiControl(True)
    client.armDisarm(True)
    # 離陸

    #keyboard_control(client)

    #''' ドローン起動、takeoffまで
    motor_onoff(client)
    drone_control(client,[0.0, -1.0, 0.0, 0.0])
    time.sleep(1)
    drone_control(client,[0.0, 0.0, 0.0, 0.0])
    #'''

    dist = destination(index=0)
    fly_to_destination(client, dist)

    fly_to_destination(client, destination(index=3))

    #angle = calculate_angle(desti['x'],desti['y'],dist3['x'],dist3['y'])
    
    #client.moveToPosition(dist3['x'],dist3['y'],dist3['z'],3)

    print("end")
    
    lidarData = client.getLidarData()
    if (len(lidarData.point_cloud)<3):
        print("NO")
    else:
        print(f"len: {len(lidarData.point_cloud)}")
    points = parse_lidarData(lidarData)
    print("\tReading:time_stamp: %d number_of_points: %d"% (lidarData.time_stamp, len(points)))
       

    

    # 目的地1まで移動
    dest1 = destination(index=0)
    

    return 0

if __name__ == "__main__":
    sys.exit(main())