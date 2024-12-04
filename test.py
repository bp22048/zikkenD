import sys
import hakosim
import numpy
import time
import math
import pprint


def destination():
    #目的地の取得
    
    return 0

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
    roll, pitch, yaw = hakosim_types.Quaternionr.quaternian_to_euler(pose.orientation)
    print("ANGLE:{math.degrees(roll)} {math.degrees(pitch)}{mathdegrees(yaw)}")
    
    #目的地の取得

    #目的地へ移動　x:x軸　y:y軸　z: 高度　speed：速さ(m/s)　機首の方向: yaw_deg
    client.moveToPosition(x,y,z=3,speed=3,yaw_deg=0)
    
    client.land() #着陸
    
    

    return 0

if __name__=="__main__":
    sys.exit(main())