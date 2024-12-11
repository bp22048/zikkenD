import sys
import hakosim
import numpy
import time
import math
import pprint

#目的地
def destination():
    #test
    
    return 0

#目的地まで飛行
def fly_to_destination():
    
    return 0

#着陸
def landing():
    return 0

#障害物回避
def avoidance():
    return 0

def debug_pos(client):
    pose = client.simGetVehiclePose()
    print(f"POS  : {pose.position.x_val} {pose.position.y_val} {pose.position.z_val}")
    roll, pitch, yaw = hakosim.hakosim_types.Quaternionr.quaternion_to_euler(pose.orientation)
    print(f"ANGLE: {math.degrees(roll)} {math.degrees(pitch)} {math.degrees(yaw)}")


def main():
    
    if len(sys.argv)!= 2:
        print(f"Usage:{sys.argv[0]}<config_path>")
        return 1
    
    #箱庭ドローンを走査するためのクライアントとオブジェクトを取得
    client = hakosim.MultirotorClient(sys.argv[1])
    #クライアントオブジェクトの初期化
    client.confirmConnection()
    client.enableApiControl(True)
    client.armDisarm(True)
    
    #自身のプログラム

    #離陸
    client.takeoff(3) 

    #ドローンを目的地1まで移動
    client.moveToPosition(x=10,y=0,z=3,speed=3,yaw_deg=0)

    #着陸
    client.land()

    #投票時間(今回は10秒間停止)
    time.sleep(10)

    #離陸
    client.takeoff(3)

    #ドローンを目的地2まで移動
    client.moveToPosition(x=-5,y=-5,z=3,speed=3,yaw_deg=0)

    #着陸
    client.land()
    return 0

if __name__=="__main__":
    sys.exit(main())
