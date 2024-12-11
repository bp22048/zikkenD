import sys
import hakosim
import numpy
import time
import math
import pprint


def destination():
    #6666666666
    
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

    client.moveToPosition(x=4,y=5,z=4,speed=10,yaw_deg=0)

    client.land()

    client.takeoff(3) #離陸

    client.moveToPosition(x=-3,y=-3,z=3,speed=10,yaw_deg=0)

    client.land()

    return 0

if __name__=="__main__":
    sys.exit(main())
