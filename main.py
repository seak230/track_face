import cv2
import mediapipe as mp

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
            # 1. 얼굴 외곽 기준점 가져오기 (비율 계산용)
            x1 = face_landmarks.landmark[234].x  # 왼쪽 뺨
            x2 = face_landmarks.landmark[454].x  # 오른쪽 뺨
            y1 = face_landmarks.landmark[10].y   # 이마 위쪽
            y2 = face_landmarks.landmark[152].y  # 턱 아래쪽

            # 화면상의 상하좌우 최소/최대 좌표 계산
            screen_left_x = min(x1, x2)
            screen_right_x = max(x1, x2)
            screen_top_y = min(y1, y2)
            screen_bottom_y = max(y1, y2)

            # 2. 코 끝 (랜드마크 인덱스 1번)
            nose_tip = face_landmarks.landmark[1]
            nose_x = nose_tip.x
            nose_y = nose_tip.y
            
            # 3. 얼굴 전체 영역 안에서 코의 상대적 위치(비율) 계산 (0.0 ~ 1.0)
            # 분모가 0이 되는 것을 방지하기 위해 아주 작은 값(1e-6)을 더함
            ratio_x = (nose_x - screen_left_x) / (screen_right_x - screen_left_x + 1e-6)
            ratio_y = (nose_y - screen_top_y) / (screen_bottom_y - screen_top_y + 1e-6)

            # 4. 바라보는 방향 판별 (임계값 설정)
            text_x, kr_x = "", ""
            text_y, kr_y = "", ""

            # 좌우 판단 (얼굴 안에서 코가 왼쪽/오른쪽으로 얼마나 쏠렸나)
            if ratio_x < 0.35:
                text_x, kr_x = "Left", "좌"
            elif ratio_x > 0.65:
                text_x, kr_x = "Right", "우"

            # 상하 판단 (사람의 코는 보통 얼굴 중심보다 살짝 아래에 있으므로 기준점을 0.5~0.65로 잡음)
            if ratio_y < 0.52:
                text_y, kr_y = "Up", "위"     # 코가 이마 쪽에 가까워짐
            elif ratio_y > 0.6:
                text_y, kr_y = "Down", "아래"  # 코가 턱 쪽에 가까워짐

            # 최종 방향 조합 (예: 상좌, 하우, 정면)
            if kr_y and kr_x:
                dir_kr = f"{kr_y}{kr_x}"  # 위좌 -> 상좌로 하고 싶다면 글자를 변경
                dir_eng = f"{text_y}-{text_x}"
                # '위좌'보다 '상좌'가 자연스러우니 교체
                dir_kr = dir_kr.replace("위", "상").replace("아래", "하")
            elif kr_x:
                dir_kr = kr_x
                dir_eng = text_x
            elif kr_y:
                dir_kr = kr_y
                dir_eng = text_y
            else:
                dir_kr = "정면"
                dir_eng = "Front"

            # 5. 콘솔(터미널)에 방향 출력 (방향이 바뀔 때만 한 번씩 출력)
            if dir_kr != prev_direction:
                print(f"현재 방향: {dir_kr}")
                prev_direction = dir_kr

            # 6. 화면 시각화 처리
            cx = int(nose_x * w)
            cy = int(nose_y * h)
            
            # 빨간 점 그리기
            cv2.circle(image, (cx, cy), 15, (0, 0, 255), -1)
            
            # 영상 화면에는 영어로 방향 텍스트 표시
            cv2.putText(image, f"Dir: {dir_eng}", (cx + 25, cy - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            # 디버깅용: 코의 실제 비율을 화면에 작게 표시
            cv2.putText(image, f"(X:{ratio_x:.2f} Y:{ratio_y:.2f})", (cx + 25, cy + 15), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    # 화면에 출력
    cv2.imshow('Face Direction Pointer', image)
    
    # ESC 키를 누르면 종료
    if cv2.waitKey(5) & 0xFF == 27:
        break

# 자원 해제
cap.release()
cv2.destroyAllWindows()