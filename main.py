import cv2
import mediapipe as mp
import pyautogui

# --- [마우스 클릭 좌표 설정] ---
# 본인 모니터 해상도에 맞게 클릭할 X, Y 좌표를 숫자로 적어주세요.
LEFT_CLICK_POS = (580, 140)   # 왼쪽을 봤을 때 마우스가 이동해서 클릭할 위치 (X, Y)
RIGHT_CLICK_POS = (2250, 98) # 오른쪽을 봤을 때 마우스가 이동해서 클릭할 위치 (X, Y)
# -------------------------------

# 만약 마우스가 통제 불능이 되면 마우스를 모니터의 모서리 끝으로 확 던지면 프로그램이 정지됩니다. (안전장치)
pyautogui.FAILSAFE = True 
pyautogui.PAUSE = 0.1 # 마우스 이동 후 클릭까지의 아주 짧은 딜레이

# MediaPipe Face Mesh 초기화
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1, 
    refine_landmarks=True, 
    min_detection_confidence=0.5, 
    min_tracking_confidence=0.5
)

# 웹캠 켜기
cap = cv2.VideoCapture(0)

print("프로그램을 종료하려면 화면을 클릭하고 'ESC' 키를 누르세요.")
print("안전장치: 마우스가 멈추지 않으면 물리적 마우스를 모니터 네 모서리 끝 중 한 곳으로 끝까지 미세요.")

# 터미널 도배를 막기 위해 이전 방향을 저장할 변수
prev_direction = ""

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("웹캠을 찾을 수 없습니다.")
        break

    # 거울 모드를 위해 이미지를 좌우 반전시키고 BGR을 RGB로 변환
    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # 얼굴 인식 수행
    results = face_mesh.process(image_rgb)
    
    h, w, _ = image.shape

    # 얼굴이 인식되었을 경우
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # 1. 얼굴 외곽 기준점 가져오기
            x1 = face_landmarks.landmark[234].x  
            x2 = face_landmarks.landmark[454].x  
            y1 = face_landmarks.landmark[10].y   
            y2 = face_landmarks.landmark[152].y  

            screen_left_x = min(x1, x2)
            screen_right_x = max(x1, x2)
            screen_top_y = min(y1, y2)
            screen_bottom_y = max(y1, y2)

            # 2. 코 끝 (랜드마크 인덱스 1번)
            nose_tip = face_landmarks.landmark[1]
            nose_x = nose_tip.x
            nose_y = nose_tip.y
            
            # 3. 코의 상대적 위치(비율) 계산
            ratio_x = (nose_x - screen_left_x) / (screen_right_x - screen_left_x + 1e-6)
            ratio_y = (nose_y - screen_top_y) / (screen_bottom_y - screen_top_y + 1e-6)

            # 4. 바라보는 방향 판별
            text_x, kr_x = "", ""
            text_y, kr_y = "", ""

            if ratio_x < 0.35:
                text_x, kr_x = "Left", "좌"
            elif ratio_x > 0.65:
                text_x, kr_x = "Right", "우"

            if ratio_y < 0.52:
                text_y, kr_y = "Up", "위"     
            elif ratio_y > 0.6:
                text_y, kr_y = "Down", "아래"  

            # 최종 방향 조합
            if kr_y and kr_x:
                dir_kr = f"{kr_y}{kr_x}".replace("위", "상").replace("아래", "하")
                dir_eng = f"{text_y}-{text_x}"
            elif kr_x:
                dir_kr = kr_x
                dir_eng = text_x
            elif kr_y:
                dir_kr = kr_y
                dir_eng = text_y
            else:
                dir_kr = "정면"
                dir_eng = "Front"

            # 5. 방향이 이전과 달라졌을 때 (즉, 방금 새 방향을 쳐다봤을 때) 실행
            if dir_kr != prev_direction:
                print(f"현재 방향: {dir_kr}")
                
                # '좌' 방향을 인식했을 때 마우스 제어
                if dir_kr == "좌":
                    print(f" > 왼쪽 좌표 {LEFT_CLICK_POS} 로 이동 후 클릭!")
                    pyautogui.moveTo(LEFT_CLICK_POS[0], LEFT_CLICK_POS[1])
                    pyautogui.click()
                
                # '우' 방향을 인식했을 때 마우스 제어
                elif dir_kr == "우":
                    print(f" > 오른쪽 좌표 {RIGHT_CLICK_POS} 로 이동 후 클릭!")
                    pyautogui.moveTo(RIGHT_CLICK_POS[0], RIGHT_CLICK_POS[1])
                    pyautogui.click()

                # 현재 방향 갱신
                prev_direction = dir_kr

            # 6. 화면 시각화 처리
            cx = int(nose_x * w)
            cy = int(nose_y * h)
            
            cv2.circle(image, (cx, cy), 15, (0, 0, 255), -1)
            cv2.putText(image, f"Dir: {dir_eng}", (cx + 25, cy - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(image, f"(X:{ratio_x:.2f} Y:{ratio_y:.2f})", (cx + 25, cy + 15), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    cv2.imshow('Face Direction Pointer', image)
    
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()