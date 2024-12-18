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
        {'x': 10, 'y': 0, 'z': 3},
        {'x': -5, 'y': -5, 'z': 3},
        {'x': 15, 'y': 10, 'z': 3}
    ]
    # 指定されたインデックスの目的地を返す
    if index is not None and 0 <= index < len(destinations):
        return destinations[index]
    # デフォルトで最初の目的地を返す
    return destinations[0]

# 目的地まで飛行
def fly_to_destination(client, destination, speed, yaw_deg):
    client.moveToPosition(x=destination['x'], y=destination['y'], z=destination['z'], speed=speed, yaw_deg=yaw_deg)

# 着陸
def landing(client, position, speed, yaw_deg):
    client.moveToPosition(x=position['x'], y=position['y'], z=0, speed=speed, yaw_deg=yaw_deg)

# 障害物回避
def avoidance():
    return 0

def parse_lidarData(data):
    #reshape array of floats to array of[X,Y,Z]
    points = numpy.array(data.point_cloud, dtype=numpy.dtype('f4'))
    points = numpy.reshape(points, (int(points.shape[0]/3),3))
    return points

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
                
                    if event.key == K_w:
                        print("front")
                        destination['x'] += 1
                        destination['y'] *= -1
                        fly_to_destination(client,destination,speed=5,yaw_deg=5)
                        #print('CUBIC AXIS VALUE:',data['axis'][event.axis])
                    if event.key == K_s:
                        print("back")
                        destination['x'] -= 1
                        destination['y'] *= -1
                        fly_to_destination(client,destination,speed=5,yaw_deg=5)
                    if event.key == K_a:
                        print("left")
                        destination['y'] += 1
                        destination['y'] *= -1
                        fly_to_destination(client,destination,speed=5,yaw_deg=5)
                    if event.key == K_d:
                        print("right")
                        destination['y'] -= 1
                        destination['y'] *= -1
                        fly_to_destination(client,destination,speed=5,yaw_deg=5)
                    # up down
                    if event.key == K_e:
                        client.takeoff(3)
                    if event.key == K_r:
                        client.land()
                    if event.key == K_UP:
                        print("up")
                        destination['z'] += 1
                        destination['y'] *= -1
                        fly_to_destination(client,destination,speed=5,yaw_deg=5)
                            #print('CUBIC AXIS VALUE:',data['axis'][event.axis])
                    if event.key == K_DOWN:
                        print("down")
                        destination['z'] -= 1
                        destination['y'] *= -1
                        fly_to_destination(client,destination,speed=5,yaw_deg=5)
                    if event.key == K_LEFT:
                        print("W")
                    if event.key == K_RIGHT:
                        print("W")
                    if event.key == K_f:
                        pygame.quit()
                        return 0
                    destination = debug_pos(client)
            #print("k")
    except KeyboardInterrupt:
        # Ctrl+Cが押されたときにジョイスティックをクリーンアップ
        pygame.quit()
    return 0

# キーボードセット
def keyboard(client):
    pygame.init()
    
    # connect to the HakoSim simulator
    client.default_drone_name = "DroneTransporter"
    client.confirmConnection()
    client.enableApiControl(True)
    client.armDisarm(True)
    keyboard_control(client)
    return 0

# デバッグ用: ドローンの現在位置と姿勢を表示
def debug_pos(client):
    pose = client.simGetVehiclePose()
    print(f"POS : {pose.position.x_val} {pose.position.y_val} {pose.position.z_val}")
    roll, pitch, yaw = hakosim.hakosim_types.Quaternionr.quaternion_to_euler(pose.orientation)
    print(f"ANGLE: {math.degrees(roll)} {math.degrees(pitch)} {math.degrees(yaw)}")
    destination = {'x': pose.position.x_val, 'y': pose.position.y_val, 'z': pose.position.z_val}
    return destination

# 離陸処理
def takeoff(client, altitude):
    client.takeoff(altitude)

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
    takeoff(client, altitude=3)

    '''
    lidarData = client.getLidarData()
    if (len(lidarData.point_cloud)<3):
        print("NO")
    else:
        print(f"len: {len(lidarData.point_cloud)}")
    points = parse_lidarData(lidarData)
    print("\tReading:time_stamp: %d number_of_points: %d"% (lidarData.time_stamp, len(points)))
    '''    

    # 目的地1まで移動
    dest1 = destination(index=0)
    fly_to_destination(client, dest1, speed=3, yaw_deg=0)
    landing(client, dest1, speed=3, yaw_deg=0)
    keyboard_control(client)

    # 投票時間 (10秒間停止)
    time.sleep(10)

    # 目的地2まで移動
    dest2 = destination(index=1)
    fly_to_destination(client, dest2, speed=3, yaw_deg=0)
    landing(client, dest2, speed=3, yaw_deg=0)

    # 投票時間 (10秒間停止)
    time.sleep(10)

    # 本部に戻る
    home = destination(index=2)
    fly_to_destination(client, home, speed=5, yaw_deg=0)
    landing(client, home, speed=5, yaw_deg=0)

    return 0

if __name__ == "__main__":
    sys.exit(main())