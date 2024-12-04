import sys
import hakosim
import numpy
import time
import math
import pprint


def destination():
    #
    
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
    
    #3m浮上
    client.takeoff(15)

    #目的地へ移動
    client.moveToPosition(x=10,y=0,z=3,spped=3,yaw_deg=0)

    #カメラ撮影
    png_image = client.simGetImage("0",hakosim.ImageType.Scene)

    #ファイルとして保存
    if png_image:
        with open("scene.png","wb") as f:
            f.write(png_image)
            
    #着陸
    client.land()
    
    
    pose = client.simGetVehiclePose() #ドローンの位置と姿勢を取得
    roll, pitch, yaw = hakosim_types.Quaternionr.quaternian_to_euler(pose.orientation)
    print("ANGLE:{math.degrees(roll)} {math.degrees(pitch)}{mathdegrees(yaw)}")
    

    return 0

if __name__=="__main__":
    sys.exit(main())