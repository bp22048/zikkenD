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
        {'x': 15, 'y': -10, 'z': 3}
    ]
    # 指定されたインデックスの目的地を返す
    if index is not None and 0 <= index < len(destinations):
        return destinations[index]
    # デフォルトで最初の目的地を返す
    return destinations[0]

# 目的地まで飛行
def fly_to_destination(client, destination, speed, yaw_deg):

    client.moveToPosition(x=destination['x'], y=destination['y'], z=destination['z'], speed=speed, yaw_deg=yaw_deg)

# 障害物回避
def avoidance(client):
    
    lidarData = client.getLidarData()
    if (len(lidarData.point_cloud)<3):
        print("NO")
    else:
        print(f"len: {len(lidarData.point_cloud)}")
    points = parse_lidarData(lidarData)
    print("\tReading:time_stamp: %d number_of_points: %d"% (lidarData.time_stamp, len(points)))
    print(points)
    distances = numpy.sqrt(points[:, 0]**2 + points[:, 1]**2 + points[:, 2]**2)  # 各点の距離を計算
    close_obstacles = distances[distances<7.0]
    if len(close_obstacles) > 0:
        print(f"Obstacle detected: {len(close_obstacles)} points within 7m.")
        destination = debug_pos(client)
        destination['z'] += 5
        destination['y'] *= -1
        fly_to_destination(client,destination,speed=5,yaw_deg=5)
    else:
        print("No close obstacles detected. Moving to target position.")
    return 0

def search_block(points):

    return 0

def moveToDestination(client, x, y, z, speed=8):
    """
    指定した目的地に移動する関数。LiDARを使用して障害物を検知し、
    必要に応じて回避行動を取る。
    
    Parameters:
    - client: hakosimのクライアントオブジェクト
    - x, y, z: 移動先の座標
    - speed: 移動速度 (m/s)
    """
    max_altitude = 20  # 最大高度を10mに制限
    clearance_z = z    # 初期高度を指定されたz値に設定
    
    # LiDARデータを取得
    lidarData = client.getLidarData()
    
    if not lidarData.point_cloud:
        print("\tNo points received from LiDAR. Moving to target position.")
        # LiDARがデータを返さない場合、指定位置に移動
        client.moveToPosition(x, y, clearance_z, speed)
        pass
    
    # LiDARデータを (x, y, z) に整形
    points = numpy.array(lidarData.point_cloud).reshape(-1, 3)
    distances = numpy.sqrt(points[:, 0]**2 + points[:, 1]**2 + points[:, 2]**2)  # 各点の距離を計算
    
    # 距離が7m未満の障害物を検出
    close_obstacles = distances[distances<7.0]

    #print(close_obstacles)
    
    if len(close_obstacles) > 0:
        print(f"Obstacle detected: {len(close_obstacles)} points within 7m.")
        
        # 高度を5mずつ上げて回避する。ただし、最大高度を超えないようにする
        if clearance_z < max_altitude:
            point = debug_pos(client)
            clearance_z = point['z'] + 5
            print(f"Raising altitude to avoid obstacle: {clearance_z}")
            client.moveToPosition(point['x'], point['y'], clearance_z, speed)
            moveToDestination(client,x,y,clearance_z,speed)
        else:
            print("Reached maximum altitude.")
    else:
        print("No close obstacles detected. Moving to target position.")
        client.moveToPosition(x, y, clearance_z, speed)

def parse_lidarData(data):
    #reshape array of floats to array of[X,Y,Z]
    points = numpy.array(data.point_cloud, dtype=numpy.dtype('f4'))
    points = numpy.reshape(points, (int(points.shape[0]/3),3))
    return points

def motor_onoff(client):
    data = client.getGameJoystickData()
    data['button'] = list(data['button'])
    data['button'][0] = True
    client.putGameJoystickData(data)
    time.sleep(1)
    data['button'][0] = False
    client.putGameJoystickData(data)

def drone_control(client,data,axis):
    data['axis'] = list(data['axis'])
    data['axis'] = axis
    return data

def drone_angle(client,dist):
    drone_pos = debug_pos(client)
    angle = calculate_angle(drone_pos['x'],drone_pos['y'],dist['x'],dist['y'])
    if angle > 170:
        while(not(angle-10 < drone_pos['yaw'] < -180+(angle-170))):
            pass
    return 0

def calculate_angle(current_x, current_y, target_x, target_y):
    """
    現在位置と目標位置から、目標に正対するための角度を計算する。
    
    :param current_x: 現在のx座標
    :param current_y: 現在のy座標
    :param target_x: 目標のx座標
    :param target_y: 目標のy座標
    :return: 目標への角度（ラジアン）
    """
    # x, yの差分を計算
    delta_x = target_x - current_x
    delta_y = target_y - current_y
    
    # atan2で角度を計算
    angle = math.atan2(delta_y, delta_x)
    angle_in_degrees = math.degrees(angle)
    return angle_in_degrees*-1

# キーボード操作
def keyboard_control(client: hakosim.MultirotorClient): 
    pygame.init()
    print("keyboard_control mode")
    destination = debug_pos(client)
    try:
        while True:
            pygame.display.set_mode((100, 100))
            data = client.getGameJoystickData()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == K_e:
                        motor_onoff(client)
                    if event.key == K_w:
                        print("front")
                        data = drone_control(client,data,[0.0, 0.0, 0.0, -1.0])
                    if event.key == K_s:
                        print("back")
                        data = drone_control(client,data,[0.0, 0.0, 0.0, 1.0])
                    if event.key == K_a:
                        print("left")
                        data = drone_control(client,data,[0.0, 0.0, -1.0, 0.0])
                    if event.key == K_d:
                        print("right")
                        data = drone_control(client,data,[0.0, 0.0, 1.0, 0.0])
                    # up down
                    if event.key == K_UP:
                        print("up")
                        data = drone_control(client,data,[0.0, -1.0, 0.0, 0.0])
                    if event.key == K_DOWN:
                        print("down")
                        data = drone_control(client,data,[0.0, 1.0, 0.0, 0.0])
                    if event.key == K_b:
                        print("stop")
                        data = drone_control(client,data,[0.0, 0.0, 0.0, 0.0])
                    if event.key == K_LEFT:
                        print("yaw_left")
                        data = drone_control(client,data,[-1.0, 0.0, 0.0, 0.0])
                    if event.key == K_RIGHT:
                        print("yaw_right")
                        data = drone_control(client,data,[1.0, 0.0, 0.0, 0.0])
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
            client.putGameJoystickData(data)
    except KeyboardInterrupt:
        # Ctrl+Cが押されたときにジョイスティックをクリーンアップ
        pygame.quit()
    return 0

# デバッグ用: ドローンの現在位置と姿勢を表示
def debug_pos(client):
    pose = client.simGetVehiclePose()
    print(f"POS : {pose.position.x_val} {pose.position.y_val} {pose.position.z_val}")
    roll, pitch, yaw = hakosim.hakosim_types.Quaternionr.quaternion_to_euler(pose.orientation)
    print(f"ANGLE: {math.degrees(roll)} {math.degrees(pitch)} {math.degrees(yaw)}")
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
    #pygame.init()
    # クライアントオブジェクトの初期化
    client.confirmConnection()
    client.enableApiControl(True)
    client.armDisarm(True)
    # 離陸
    # 左回りに0~180,-180~0
    client.takeoff(3)

    dist3 = destination(index=2)
    desti = debug_pos(client)
    angle = calculate_angle(desti['x'],desti['y'],dist3['x'],dist3['y'])


    
    client.moveToPosition(dist3['x'],dist3['y'],dist3['z'],3)

    #keyboard_control(client)

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