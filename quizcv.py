import csv
import cv2
from cvzone.HandTrackingModule import HandDetector
import cvzone
import time

cap = cv2.VideoCapture(0)

panjang = 640
lebar = 480

cap.set(3, panjang)
cap.set(4, lebar)

detector = HandDetector(detectionCon=0.8)

# Class Quiz
class Quiz():
    def __init__(self, data):
        self.question = data[0]
        self.choice1 = data[1]
        self.choice2 = data[2]
        self.choice3 = data[3]
        self.choice4 = data[4]
        self.answer = int(data[5])

        self.userAns = None

    def update(self, cursor, bboxs):
        for x, bbox in enumerate(bboxs):
            x1, y1, x2, y2 = bbox
            # Jika ujung jari berada didaerah rectangle
            if x1 < cursor[0] < x2 and y1 < cursor[1] < y2:
                self.userAns = x + 1
                # Maka rectangle filled warna hijau
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), cv2.FILLED)

# import CSV
pathCSV = "QnA.csv"
with open(pathCSV, newline='\n') as f:
    reader = csv.reader(f)
    dataAll = list(reader)[1:] # [1:] artinya menghapus baris pertama (jadi 'Question', 'Choice1', 'Choice2', 'Choice3', 'Choice4', 'Answer' bakal hilang)

# Buat objek baru untuk setiap pertanyaan & jawaban quiz
quizList = []
for q in dataAll:
    quizList.append(Quiz(q))
jmlObjek = len(quizList)
print(f"Jml objek: {jmlObjek}")

qNo = 0
# Total pertanyaan
qTotal = len(dataAll)
print(f"Total pertanyaan: {qTotal}")

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    # Hand detector
    hands, img = detector.findHands(img, flipType=False)

    if qNo < qTotal:
        # Semua pertanyaan & jawaban quiz disini
        dataQuiz = quizList[qNo]

        # img = sumber capture
        # dataQuiz.question,choice1-4 = pertanyaan yang dijadiin text pada rectangle
        # position = posisi rectangle dalam x,y contoh: [100, 100]
        # scale  = ukuran skala
        # thickness = ketebalan font
        txt_pertanyaan = dataQuiz.question
        txt_pilihan1 = dataQuiz.choice1
        txt_pilihan2 = dataQuiz.choice2
        txt_pilihan3 = dataQuiz.choice3
        txt_pilihan4 = dataQuiz.choice4

        # Buat rectangle disertai text didalamnya
        img, bbox = cvzone.putTextRect(img, txt_pertanyaan, [100, 100], scale=1, thickness=1, border=2, offset=20)
        img, bbox1 = cvzone.putTextRect(img, txt_pilihan1, [100, 200], scale=1, thickness=1, border=2, offset=20)
        img, bbox2 = cvzone.putTextRect(img, txt_pilihan2, [300, 200], scale=1, thickness=1, border=2, offset=20)
        img, bbox3 = cvzone.putTextRect(img, txt_pilihan3, [100, 300], scale=1, thickness=1, border=2, offset=20)
        img, bbox4 = cvzone.putTextRect(img, txt_pilihan4, [300, 300], scale=1, thickness=1, border=2, offset=20)

        if hands:
            lmList = hands[0]['lmList']
            cursor = lmList[8]
            length, info = detector.findDistance(lmList[8], lmList[12])
            # hilangkan img jika tidak mau ada drawable distance jari
            # length, info, img = detector.findDistance(lmList[8], lmList[12], img)
            # Cetak jarak antara dua jari
            # print("Jarak: ", length)
            # jika jarak telunjuk dengan tengah < 15
            if length < 20:
                print("Aksi")
                dataQuiz.update(cursor, [bbox1, bbox2, bbox3, bbox4])
                # Cetak index rectangle
                print(dataQuiz.userAns)

                if dataQuiz.userAns is not None:
                    # Akalin agar tidak multiple time dalam satu action
                    # Jadi dijeda 0.3 detik
                    time.sleep(0.3)
                    qNo += 1
    else:
        score = 0
        for dataQuiz in quizList:
            if dataQuiz.answer == dataQuiz.userAns:
                score += 1
        score = round((score/qTotal) * 100, 2)
        print("Score: ", score)
        # Draw Score
        cvzone.putTextRect(img, "Quiz Selesai", [150, 200], 1, 1, offset=13, border=2)
        cvzone.putTextRect(img, f"Score: {score}", [400, 200], 1, 1, offset=13, border=2)

    # Draw progress bar
    barValue = 50 + (450//qTotal) * qNo
    cv2.rectangle(img, (50, 410), (barValue, 430), (0, 255, 0), cv2.FILLED)
    cv2.rectangle(img, (50, 410), (500, 430), (255, 0, 255), 2)
    persen = (qNo/qTotal) * 100
    img, _ = cvzone.putTextRect(img, f'{round(persen)}%', [530, 425], 1, 1, offset=13)

    cv2.imshow("Quiz", img)
    cv2.waitKey(1)
