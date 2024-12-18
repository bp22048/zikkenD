import sys
import hakosim
import numpy
import time
import math
import pprint


def destination():
    #目的地の取得
    
    return 0

def moveToDestination(client, x, y, z, speed = 5):
    #障害物検出
    lidarData = client.getLidarData()
    #points = parse_lidarData(lidarData) #障害物情報の整形
    #print("\tReading: time_stamp: %d number_of_points: %d" %(pprint.pformat(lidarData.pose.position))) #障害物情報の出力
    if not lidarData.point_cloud:
        print("\tNo points received from Lidar data")
        # 基準の高さへ移動
        client.moveToPositionAsync(x, y, z ,speed ,yaw_deg=0).join()
    else:
        print(f"Obstacle detected: {len(lidarData.point_cloud)} points")
        # 障害物の回避ロジック
        clearance_z = z
        while len(lidarData.point_cloud) >= 3:  # 障害物が存在する間
            clearance_z += 1  # 高度を1mずつ上げる
            print(f"Raising altitude to avoid obstacle: {clearance_z}")
            client.moveToPosition(x, y, clearance_z, speed)
            lidarData = client.getLidarData()  # 最新のLiDARデータを取得
        
        print("Obstacle avoided, resuming normal movement.")
        client.moveToPosition(x, y, z, speed)

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

    client.takeoff(3) #離陸
    
    pose = client.simGetVehiclePose() #ドローンの位置と姿勢を取得
    ##roll, pitch, yaw = hakosim_types.Quaternionr.quaternian_to_euler(pose.orientation)
    print("ANGLE:{math.degrees(roll)} {math.degrees(pitch)}{mathdegrees(yaw)}")
    
    #目的地の取得
    

    #目的地へ移動　x:x軸　y:y軸　z: 高度　speed：速さ(m/s)　機首の方向: yaw_deg
    x,y,z = 50,0,3
    moveToDestination(client, x, y, z)
    
    
    
    
    
    
    client.land() #着陸
    
    

    return 0

if __name__=="__main__":
    sys.exit(main())