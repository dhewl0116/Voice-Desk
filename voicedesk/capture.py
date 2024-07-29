import cv2


def capture_and_split_image():
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)
    
    if not cap.isOpened():
        print("camera is not opened")
    else:
        ret, original_image = cap.read()
        if not ret:
            print("can't capture")
        else:
            for i in range(25):
                ret, original_image = cap.read()

    
    # 이미지를 두 부분으로 나누기
    height, width = original_image.shape[:2]
    half_width = width // 2
    left_half = original_image[:, :half_width]
    right_half = original_image[:, half_width:]

    # 각 부분을 별도의 파일로 저장
    cv2.imwrite("/home/jimin/voicedesk/left.png", left_half)
    cv2.imwrite("/home/jimin/voicedesk/right.png", right_half)
    cap.release()
