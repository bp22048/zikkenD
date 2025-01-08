import sys
import hakosim
import numpy
import time
import math
import pprint
import pygame
from pygame.locals import *

'''
axisについて
ドローンをコントローラ操作する時に使用している1次元4要素の配列
  exp. axis = [0.0, -1.0, 0.0, 0.0]

それぞれの要素がドローンの動作に関わり、値は -1.0から1.0の範囲
axis[0] : 旋回(マイナスが左回り、プラスが右回り)
axis[1] : 上昇下降(マイナスで上、プラスで下)
axis[2] : 左右(マイナスで左、プラスで右)
axis[3] : 前後(マイナスで前、プラスで後ろ)
'''


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
    '''
    distで指定された座標(高さは無視)に移動する
    '''
    drone_pos = debug_pos(client)
    axis = calculate_axis(round(drone_pos['x'],3),round(drone_pos['y'],3),dist['x'],dist['y'])
    while axis != [0.0, 0.0, 0.0, 0.0]:
        drone_pos = debug_pos(client)
        axis = calculate_axis(round(drone_pos['x'],3),round(drone_pos['y'],3),dist['x'],dist['y'])
        drone_angle(client,dist,axis)
        avoidance(client,axis)
        drone_control(client,axis)
        #time.sleep(1)
    time.sleep(5)
    drone_pos = debug_pos(client)
    delta_x = round(drone_pos['x'],3) - dist['x']
    delta_y = round(drone_pos['y'],3) - dist['y']
    print("誤差:x=",delta_x,",y=",delta_y)
    keyboard_control(client)

# 障害物回避
def avoidance(client,axis):
    axis = [x * -1 for x in axis]
    while obstacle_detection(client):
        drone_control(client,axis)
        time.sleep(2)
        drone_control(client,[0.0, -1.0, 0.0, 0.0])
        time.sleep(1)
    return True

# 障害物検出
def obstacle_detection(client):
    '''
    障害物の検出をしたときTrueを返す
    '''
    lidarData = client.getLidarData()
    points = parse_lidarData(lidarData)
    #print("\tReading:time_stamp: %d number_of_points: %d"% (lidarData.time_stamp, len(points)))
    #print(points)

    distances = numpy.sqrt(points[:, 0]**2 + points[:, 1]**2 + points[:, 2]**2)  # 各点の距離を計算
    close_obstacles = distances[distances<9.0]
    if len(close_obstacles) > 0:
        print(f"Obstacle detected: {len(close_obstacles)} points within 9m.")
        return True
    else: 
        #print("none")
        return False

def parse_lidarData(data):
    '''
    lidarで検出した点群の情報をreturn
    '''
    #reshape array of floats to array of[X,Y,Z]
    points = numpy.array(data.point_cloud, dtype=numpy.dtype('f4'))
    points = numpy.reshape(points, (int(points.shape[0]/3),3))
    return points

def motor_onoff(client):
    '''
    ドローンの起動、停止
    data['button'][0]によって操作できる
    '''
    data = client.getGameJoystickData()
    data['button'] = list(data['button'])
    data['button'][0] = True
    client.putGameJoystickData(data)
    time.sleep(1)
    data['button'][0] = False
    client.putGameJoystickData(data)

def drone_control(client,axis):
    '''
    ドローンの操作(前進後退、上昇下降など)
    '''
    data = client.getGameJoystickData()
    data['axis'] = list(data['axis'])
    data['axis'] = axis
    client.putGameJoystickData(data)
    return data

def calculate_axis(current_x, current_y, target_x, target_y, weight=1.5):
    '''
    ドローンの航行する方向を現在地と目的地から算出
    weightで速度指定(1が最大、2,3と増えるごとに遅くなる)
    '''
    delta_x = target_x - current_x
    delta_y = target_y - current_y
    bigger = max(abs(delta_x),abs(delta_y))
    
    if bigger == 0:
        bigger = 1
    #print("delta_y = ",delta_y,"delta_x = ",delta_x)
    bigger *= weight
    l_r = delta_y / bigger  # 左右
    f_b = delta_x / bigger  # 前後

    if (delta_y < 0)and(l_r < 0)or(delta_y >= 0)and(l_r >= 0): 
        l_r *= -1
    if (delta_x < 0)and(f_b < 0)or(delta_x >= 0)and(f_b >= 0): 
        f_b *= -1

    # 誤差2m以内で停止
    if (abs(delta_y) < 2)and(abs(delta_x) < 2):
        axis = [0.0, 0.0, 0.0, 0.0]
    else :
        axis = [0.0, 0.0, l_r, f_b]
    #print("axis = ",axis)
    return axis

def drone_angle(client,dist,axis):
    '''
    ドローンの向いている方向(yaw)を変える
    '''
    drone_pos = debug_pos(client)

    # 現在のドローンのyaw、目的地への角度(angle)を取得
    # +180 しているのは、-180 < yaw,angle < 180 を 0 < yaw,angle < 360 に変えるため
    yaw = drone_pos['yaw']+180
    angle = calculate_angle(drone_pos['x'],drone_pos['y'],dist['x'],dist['y'])+180
    #print("目標値：",angle)

    # 目標角度±10到達で旋回終了
    while(not(angle-10 < yaw < angle+10)):
        drone_pos = debug_pos(client)
        yaw = drone_pos['yaw']+180
        if yaw < angle:
            drone_control(client,[-1.0, 0.0, axis[2]*0.5, axis[3]*0.5])
        else: drone_control(client,[1.0, 0.0, axis[2]*0.5, axis[3]*0.5])
        
    drone_pos = debug_pos(client)
    #print("実測値",drone_pos['yaw']+180)

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
    return angle_in_degrees

def keyboard_control(client: hakosim.MultirotorClient): 
    '''
    キーボード操作(起動すると出てくる謎の小さいwindowをクリックしてからじゃないと動かない)

    上昇              : PageUp
    下降              : PageDown
    旋回              : Left,Right
    前進後退等         : w,a,s,d
    キーボード操作終了 : fキー
    liderData取得     : xキー
    '''
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

    fly_to_destination(client, destination(index=2))

    fly_to_destination(client, destination(index=0))

    fly_to_destination(client, destination(index=3))

    print("end")

    return 0

if __name__ == "__main__":
    sys.exit(main())