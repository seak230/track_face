import cv2
import mediapipe as mp
import pyautogui
import pygetwindow as gw  # 특정 창 인식을 위해 추가된 라이브러리

# --- [설정 부분] ---
# 본인 모니터 해상도에 맞게 클릭할 X, Y 좌표를 숫자로 적어주세요.
FRONT_CLICK_POS = (580, 140)   # 왼쪽을 봤을 때
RIGHT_CLICK_POS = (2250, 98)  # 오른쪽을 봤을 때

# ★ 여기에 마우스 제어가 작동하길 원하는 프로그램의 창 이름을 적어주세요. 
# (예: "Chrome", "메모장", "리그 오브 레전드" 등)
TARGET_WINDOW_TITLE = "Obsidian"  
# -------------------------------

pyautogui.FAILSAFE = True 
pyautogui.PAUSE = 0.1 

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1, 
    refine_landmarks=True, 
    min_detection_confidence=0.5, 
    min_tracking_confidence=0.5
)

cap = cv2.VideoCapture(0)

print(f"[{TARGET_WINDOW_TITLE}] 창이 맨 앞에 띄워져 있을 때만 작동합니다.")
print("프로그램을 종료하려면 화면을 클릭하고 'ESC' 키를 누르세요.")

prev_direction = ""

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("웹캠을 찾을 수 없습니다.")
        break

    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    results = face_mesh.process(image_rgb)
    
    h, w, _ = image.shape

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            x1 = face_landmarks.landmark[234].x  
            x2 = face_landmarks.landmark[454].x  
            y1 = face_landmarks.landmark[10].y   
            y2 = face_landmarks.landmark[152].y  

            screen_left_x = min(x1, x2)
            screen_right_x = max(x1, x2)
            screen_top_y = min(y1, y2)
            screen_bottom_y = max(y1, y2)

            nose_tip = face_landmarks.landmark[1]
            nose_x = nose_tip.x
            nose_y = nose_tip.y
            
            ratio_x = (nose_x - screen_left_x) / (screen_right_x - screen_left_x + 1e-6)
            ratio_y = (nose_y - screen_top_y) / (screen_bottom_y - screen_top_y + 1e-6)

            text_x, kr_x = "", ""
            text_y, kr_y = "", ""

            if ratio_x > 0.65:
                text_x, kr_x = "Right", "우"

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

            # 5. 방향이 이전과 달라졌을 때 실행
            if dir_kr != prev_direction:
                print(f"현재 방향: {dir_kr}")
                
                # --- [특정 창 활성화 검사] ---
                # 현재 맨 앞(Foreground)에 있는 창의 정보를 가져옵니다.
                active_window = gw.getActiveWindow()
                
                # 창이 존재하고, 그 창의 제목에 우리가 설정한 이름이 포함되어 있을 때만 마우스 동작
                if active_window is not None and TARGET_WINDOW_TITLE in active_window.title:
                    
                    if dir_kr == "정면":
                        print(f" > 왼쪽 좌표 {FRONT_CLICK_POS} 로 이동 후 클릭!")
                        pyautogui.moveTo(FRONT_CLICK_POS[0], FRONT_CLICK_POS[1])
                        pyautogui.click()
                        
                        screen_w, screen_h = pyautogui.size()
                        center_x = screen_w // 2
                        center_y = screen_h // 3
                        
                        pyautogui.moveTo(center_x, center_y)
                        print(f" > 마우스 커서 정중앙({center_x}, {center_y})으로 복귀 완료!")
                        
                    elif dir_kr == "우":
                        print(f" > 오른쪽 좌표 {RIGHT_CLICK_POS} 로 이동 후 클릭!")
                        pyautogui.moveTo(RIGHT_CLICK_POS[0], RIGHT_CLICK_POS[1])
                        pyautogui.click()
                else:
                    # 조건에 맞지 않으면 마우스 제어를 무시함
                    current_title = active_window.title if active_window else "알 수 없음"
                    print(f" ⏸ 대상 창이 아닙니다. 클릭 무시 (현재 창: {current_title})")

                # 방향 갱신 (창이 활성화 안 되어 클릭을 무시했더라도 방향은 바뀌었다고 기억해 둠)
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