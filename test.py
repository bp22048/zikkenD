import sys
import hakosim
import numpy
import time
import math
import pprint


def destination():
    #目的地の取得
    
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
    
    while True:
        # LiDARデータを取得
        lidarData = client.getLidarData()
        
        if not lidarData.point_cloud:
            print("\tNo points received from LiDAR. Moving to target position.")
            # LiDARがデータを返さない場合、指定位置に移動
            client.moveToPosition(x, y, clearance_z, speed)
            break
        
        # LiDARデータを (x, y, z) に整形
        points = numpy.array(lidarData.point_cloud).reshape(-1, 3)
        distances = numpy.sqrt(points[:, 0]**2 + points[:, 1]**2 + points[:, 2]**2)  # 各点の距離を計算
        
        # 距離が7m未満の障害物を検出
        close_obstacles = distances[distances < 10.0]
        
        if len(close_obstacles) > 0:
            print(f"Obstacle detected: {len(close_obstacles)} points within 10m.")
            
            # 高度を5mずつ上げて回避する。ただし、最大高度を超えないようにする
            if clearance_z < max_altitude:
                clearance_z += 5
                print(f"Raising altitude to avoid obstacle: {clearance_z}")
                client.moveToPosition(x, y, clearance_z, speed)
            else:
                print("Reached maximum altitude.")
                break
        else:
            print("No close obstacles detected. Moving to target position.")
            client.moveToPosition(x, y, clearance_z, speed)
            break




def main():
    
    if len(sys.argv)!= 2:
        print(f"Usage:{sys.argv[0]}<config_path>")
        return 1
        #sys.argv[0] = "..\config\custom.json"
    
    #箱庭ドローンを走査するためのクライアントとオブジェクトを取得
    client = hakosim.MultirotorClient(sys.argv[1])
    #クライアントオブジェクトの初期化
    client.confirmConnection()
    client.enableApiControl(True)
    client.armDisarm(True)
    
    #自身のプログラム

    client.takeoff(5) #離陸
    
    pose = client.simGetVehiclePose() #ドローンの位置と姿勢を取得
    ##roll, pitch, yaw = hakosim_types.Quaternionr.quaternian_to_euler(pose.orientation)
    print("ANGLE:{math.degrees(roll)} {math.degrees(pitch)}{mathdegrees(yaw)}")
    
    #目的地の取得
    

    #目的地へ移動　x:x軸　y:y軸　z: 高度　speed：速さ(m/s)　機首の方向: yaw_deg
    x, y, z = 20, 0, 3
    moveToDestination(client, x, y, z)
    time.sleep(3)

    x, y, z = 50, 0, 20 
    moveToDestination(client, x, y, z)
    time.sleep(5)

    x, y, z = 0, 0, 20
    client.moveToPosition(x, y, z,speed = 5)
    time.sleep(5)
    

    
    
    client.land() #着陸
    
    

    return 0

if __name__=="__main__":
    sys.exit(main())
