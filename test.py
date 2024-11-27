import sys
import hakosim

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
    #これ見えてる？

    return 0

if __name__=="__main__":
    sys.exit(main())