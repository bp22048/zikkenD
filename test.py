import sys
import hakosim
import numpy
import time
import math
import pprint

# 目的地

def destination():
    # テスト用の目的地を返す (例: x=10, y=0, z=3)
    return {'x': 10, 'y': 0, 'z': 3}

# 目的地まで飛行
def fly_to_destination(client, destination, speed, yaw_deg):
    client.moveToPosition(x=destination['x'], y=destination['y'], z=destination['z'], speed=speed, yaw_deg=yaw_deg)

# 着陸
def landing(client, position, speed, yaw_deg):
    client.moveToPosition(x=position['x'], y=position['y'], z=0, speed=speed, yaw_deg=yaw_deg)

# 障害物回避
def avoidance():
    return 0

# デバッグ用: ドローンの現在位置と姿勢を表示
def debug_pos(client):
    pose = client.simGetVehiclePose()
    print(f"POS : {pose.position.x_val} {pose.position.y_val} {pose.position.z_val}")
    roll, pitch, yaw = hakosim.hakosim_types.Quaternionr.quaternion_to_euler(pose.orientation)
    print(f"ANGLE: {math.degrees(roll)} {math.degrees(pitch)} {math.degrees(yaw)}")

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

    # 目的地1まで移動
    dest1 = destination()
    fly_to_destination(client, dest1, speed=3, yaw_deg=0)
    landing(client, dest1, speed=3, yaw_deg=0)

    # 投票時間 (10秒間停止)
    time.sleep(10)

    # 目的地2まで移動
    dest2 = {'x': -5, 'y': -5, 'z': 3}
    fly_to_destination(client, dest2, speed=3, yaw_deg=0)
    landing(client, dest2, speed=3, yaw_deg=0)

    # 投票時間 (10秒間停止)
    time.sleep(10)

    # 本部に戻る
    home = {'x': 0, 'y': 0, 'z': 3}
    fly_to_destination(client, home, speed=5, yaw_deg=0)
    landing(client, home, speed=5, yaw_deg=0)

    return 0

if __name__ == "__main__":
    sys.exit(main())
