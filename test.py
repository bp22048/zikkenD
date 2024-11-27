import sys
import hakosim
import numpy
import time
import math
import pprint


def destination():
    #目的地の位置情報を取得
    
    return 0

def main():
    
    if len(sys.argv)!= 2:
        print(f"Usage:{sys.argv[0]}<config_path>")
        return 1
        #sys.argv[0] = "..\config\custom.json"
    
    client = hakosim.MultirotorClient(sys.argv[1])
    client.confirmConnection()
    client.enableApiControl(True)
    client.armDisarm(True)

    client.takeoff(3)

    return 0

if __name__=="__main__":
    sys.exit(main())