import cv2
import os
import numpy as np
import time

# ====================================================================
# --- 設定區 (請根據您的環境進行修改) ---
# ====================================================================

LEFT_CAMERA_INDEX =2
RIGHT_CAMERA_INDEX = 4

SAVE_PATH_L = "/home/juze/colcon_ws/src/img_l"
SAVE_PATH_R = "/home/juze/colcon_ws/src/img_r"

FRAME_WIDTH = 1920  # 寬度 (pixels)
FRAME_HEIGHT = 1080  # 高度 (pixels)

CHECKERBOARD_SIZE = (4, 3)

# ====================================================================
# --- 主程式碼 (通常不需要修改) ---
# ====================================================================

def setup_cameras():
    """初始化並設定攝影機，並檢查是否成功開啟。"""
    cap_l = cv2.VideoCapture(LEFT_CAMERA_INDEX)
    cap_r = cv2.VideoCapture(RIGHT_CAMERA_INDEX )

    if not cap_l.isOpened():
        print(f"錯誤: 無法開啟左相機 (索引: {LEFT_CAMERA_INDEX})")
        return None, None
    if not cap_r.isOpened():
        print(f"錯誤: 無法開啟右相機 (索引: {RIGHT_CAMERA_INDEX})")
        return None, None

    print("雙相機已成功開啟。")

    if FRAME_WIDTH > 0 and FRAME_HEIGHT > 0:
        cap_l.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        cap_l.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        cap_r.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        cap_r.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        print(f"嘗試設定解析度為 {FRAME_WIDTH}x{FRAME_HEIGHT}...")

    # 等待相機曝光穩定
    time.sleep(1)

    return cap_l, cap_r

def main():
    """主執行函式"""

    os.makedirs(SAVE_PATH_L, exist_ok=True)
    os.makedirs(SAVE_PATH_R, exist_ok=True)
    print(f"左相機影像將儲存至: {SAVE_PATH_L}")
    print(f"右相機影像將儲存至: {SAVE_PATH_R}")

    cap_l, cap_r = setup_cameras()
    if cap_l is None or cap_r is None:
        return

    img_counter = 0

    # === 顯示畫面尺寸 ===
    DISPLAY_WIDTH = 1920
    DISPLAY_HEIGHT = 1080

    # === 顯示畫面用縮放函數 ===
    def resize_frame(frame, width, height):
        return cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)

    # 主要迴圈中加上縮放顯示：
    while True:
        ret_l, frame_l = cap_l.read()
        ret_r, frame_r = cap_r.read()

        if not ret_l or not ret_r:
            print("錯誤: 無法從攝影機擷取畫面。")
            break

        gray_l = cv2.cvtColor(frame_l, cv2.COLOR_BGR2GRAY)
        gray_r = cv2.cvtColor(frame_r, cv2.COLOR_BGR2GRAY)

        # 加強棋盤格偵測穩定性
        flags = cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
        ret_l_cal, corners_l = cv2.findChessboardCorners(gray_l, CHECKERBOARD_SIZE, flags)
        ret_r_cal, corners_r = cv2.findChessboardCorners(gray_r, CHECKERBOARD_SIZE, flags)

        # 在高解析度 frame 上畫出角點標記與文字
        display_frame_l = frame_l.copy()
        display_frame_r = frame_r.copy()

        instruction_text = "Press 'SPACE' to capture, 'Q' to quit"
        cv2.putText(display_frame_l, instruction_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(display_frame_r, instruction_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        cv2.putText(display_frame_l, f"Captured: {img_counter}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(display_frame_r, f"Captured: {img_counter}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        if ret_l_cal:
            cv2.drawChessboardCorners(display_frame_l, CHECKERBOARD_SIZE, corners_l, ret_l_cal)
            cv2.putText(display_frame_l, "Chessboard FOUND!", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(display_frame_l, "Chessboard NOT found", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        if ret_r_cal:
            cv2.drawChessboardCorners(display_frame_r, CHECKERBOARD_SIZE, corners_r, ret_r_cal)
            cv2.putText(display_frame_r, "Chessboard FOUND!", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(display_frame_r, "Chessboard NOT found", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # 縮小顯示畫面
        display_frame_l = resize_frame(display_frame_l, DISPLAY_WIDTH, DISPLAY_HEIGHT)
        display_frame_r = resize_frame(display_frame_r, DISPLAY_WIDTH, DISPLAY_HEIGHT)

        cv2.imshow('Left Camera', display_frame_l)
        cv2.imshow('Right Camera', display_frame_r)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q') or key == 27:  # ESC 鍵也可以退出
            print("程式結束。")
            break
        elif key == ord(' '):
            if ret_l_cal and ret_r_cal:
                img_name_l = f"left_{img_counter}.png"
                img_name_r = f"right_{img_counter}.png"

                full_path_l = os.path.join(SAVE_PATH_L, img_name_l)
                full_path_r = os.path.join(SAVE_PATH_R, img_name_r)

                # 儲存高解析度原始影像
                cv2.imwrite(full_path_l, frame_l)
                cv2.imwrite(full_path_r, frame_r)

                print(f"成功儲存! [{img_counter}] -> {full_path_l} 和 {full_path_r}")
                img_counter += 1
            else:
                print("錯誤: 拍照失敗。請確保左右兩個畫面都成功偵測到棋盤格。")

    cap_l.release()
    cap_r.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
