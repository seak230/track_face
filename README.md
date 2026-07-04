# 🎯 Face Direction Tracker

실시간 웹캠 영상에서 얼굴의 바라보는 방향을 감지하고 표시하는 Python 프로그램입니다.

---

## 📌 개요

**Face Direction Tracker**는 [MediaPipe Face Mesh](https://developers.google.com/mediapipe/solutions/vision/face_landmarker)와 [OpenCV](https://opencv.org/)를 활용하여 웹캠으로 사용자의 얼굴을 실시간 인식하고, 코의 상대적 위치를 기반으로 현재 얼굴이 향하는 방향(정면, 좌, 우, 위, 아래 등)을 판별합니다.

---

## ✨ 주요 기능

- 🔍 **실시간 얼굴 인식** — MediaPipe Face Mesh로 468개의 얼굴 랜드마크 추적
- 📐 **방향 감지** — 코 끝 랜드마크의 얼굴 내 상대 위치 비율을 계산하여 방향 판별
- 🗂️ **8방향 지원** — 정면 / 좌 / 우 / 위 / 아래 / 상좌 / 상우 / 하좌 / 하우
- 🖥️ **시각화** — 코 위치에 빨간 점 및 방향 텍스트를 영상 화면에 오버레이
- 📟 **콘솔 출력** — 방향이 변경될 때만 터미널에 한국어로 출력 (도배 방지)
- 🪞 **거울 모드** — 영상을 좌우 반전하여 자연스러운 셀카 뷰 제공

---

## 🛠️ 동작 원리

```
웹캠 입력 → 이미지 좌우 반전(거울 모드) → BGR → RGB 변환
        → MediaPipe Face Mesh로 랜드마크 추출
        → 얼굴 외곽(뺨, 이마, 턱) 기준으로 코 끝의 상대 비율(ratio_x, ratio_y) 계산
        → 임계값 비교로 방향 판별
        → 화면 시각화 및 콘솔 출력
```

| 비율 조건 | 판별 방향 |
|---|---|
| `ratio_x < 0.35` | 좌 (Left) |
| `ratio_x > 0.65` | 우 (Right) |
| `ratio_y < 0.52` | 위 (Up) |
| `ratio_y > 0.60` | 아래 (Down) |
| 조건 없음 | 정면 (Front) |

---

## 📁 프로젝트 구조

```
track_face/
├── main.py              # 메인 실행 파일
├── requirements.txt     # 의존성 패키지 목록
├── .python-version      # Python 버전 지정 파일
├── .gitignore           # Git 제외 파일 목록
├── LICENSE              # 라이선스
└── README.md            # 프로젝트 설명 (이 파일)
```

---

## ⚙️ 설치 및 실행

### 1. 요구 사항

- Python 3.x
- 웹캠(카메라) 장치

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

주요 패키지:

| 패키지 | 버전 | 용도 |
|---|---|---|
| `mediapipe` | 0.10.14 | 얼굴 랜드마크 추출 |
| `opencv-python` | 5.0.0.93 | 웹캠 입력 및 영상 처리 |
| `numpy` | 2.5.0 | 수치 연산 |

### 3. 실행

```bash
python main.py
```

### 4. 종료

영상 화면을 클릭한 후 **`ESC`** 키를 누르면 프로그램이 종료됩니다.

---

## 📷 실행 화면 예시

프로그램 실행 시 웹캠 화면이 열리며, 코 위치에 **빨간 점**과 함께 현재 방향(`Dir: Front`, `Dir: Left` 등)이 표시됩니다.  
터미널에는 방향이 바뀔 때마다 한국어로 출력됩니다:

```
현재 방향: 정면
현재 방향: 좌
현재 방향: 상좌
현재 방향: 정면
```

---

## 📄 라이선스

이 프로젝트는 [LICENSE](./LICENSE) 파일에 명시된 라이선스를 따릅니다.
