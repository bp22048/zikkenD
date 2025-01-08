def moveToDestination(client, x, y, z, speed=8):
    """
    指定した目的地に移動する関数。LiDARを使用して障害物を検知し、
    必要に応じて回避行動を取る。
    """
    max_altitude = 20  # 最大高度を20mに制限
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
        
        # 距離が10m未満の障害物を検出
        close_obstacles = distances[distances < 10.0]
        
        if len(close_obstacles) > 0:
            print(f"Obstacle detected: {len(close_obstacles)} points within 10m.")
            
            # 高度を5mずつ上げて回避する。ただし、最大高度を超えないようにする
            if clearance_z < max_altitude:
                clearance_z += 5
                print(f"Raising altitude to avoid obstacle: {clearance_z}")
                
                # 現在位置を取得
                pose = client.simGetVehiclePose()
                current_x = pose.position.x_val
                current_y = pose.position.y_val
                
                # 新しい位置に移動
                client.moveToPosition(current_x + 10, current_y + 10, clearance_z, speed)
            else:
                print("Reached maximum altitude.")
                break
        else:
            print("No close obstacles detected. Moving to target position.")
            client.moveToPosition(x, y, clearance_z, speed)
            break
