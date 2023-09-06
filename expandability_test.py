import requests
import time

# response.request #전송한 request 객체에 접근
# response.status_code # 응답 결과 코드
# response.raise_for_status() # 200 OK가 아닌 경우 에러 발동
# response.json() # json response일 경우 딕셔너리 타입으로 바로 변환


url = "https://api.bell.zeroweb.kr/health-check?db=1"
urlTest = "http://127.0.0.1:5000/health-check"
payload = {'db': '1'}
errorTimes = 0 #마지막error발생시간, log에 찍히는 시간
normalTimes = 0 #오류 수정 시간 계산을 위한 정상회복된 시간
errorCorrectionTime = 0 #오류수정 시간
firstErrorTime = True # 첫 오류 발생
countNormalNum = 3 # 정상회복 횟수 0~3
runStart = 0 #1회 동작 시작시간
runEnd = 0 #1회 동작 종료시간


def getHttp():
    global countNormalNum, errorTimes, normalTimes, firstErrorTime
    response = requests.get(urlTest)    
    if response.status_code >= 200 and response.status_code < 300:
        if countNormalNum == 3:            
            print("정상")
            print("응답코드 : " + str(response.status_code))            
            normalTimes = time.time()
            korTimes = time.strftime('%Y-%m-%d'+ ' ' +'%X')
            resCode = response.status_code
            print("TimeStamp : " + str(int(normalTimes)))
            print("한국시간 : " + str(korTimes))
            printLog(1, normalTimes, korTimes, resCode, 0)
        else:
            if countNormalNum != 2:
                print("정상(오류 수정 중)")
                print("응답코드 : " + str(response.status_code))            
                normalTimes = time.time()
                korTimes = time.strftime('%Y-%m-%d'+ ' ' +'%X')
                resCode = response.status_code
                print("TimeStamp : " + str(int(normalTimes)))
                print("한국시간 : " + str(korTimes))
                printLog(1, normalTimes, korTimes, resCode, 0)
            countNormalNum = countNormalNum + 1
            if countNormalNum == 3:
                firstErrorTime = True
                # 오류 수정타임
                normalTimes = time.time()
                korTimes = time.strftime('%Y-%m-%d'+ ' ' +'%X')
                resCode = response.status_code
                #errorCorrectionTime = normalTimes - errorTimes
                errorCorrectionTimeMs = int((normalTimes - errorTimes) * 1000)
                errorCorrectionTimeSec = round(normalTimes - errorTimes, 1)
                print("정상(오류 수정 완료)")
                print("응답코드 : " + str(response.status_code))
                print("TimeStamp : " + str(int(normalTimes)))
                print("한국시간 : " + str(korTimes))
                # 000초 (0000(ms))
                errorCorrectionTime = str(errorCorrectionTimeSec) + "Sec" + '(' + str(errorCorrectionTimeMs) + '(ms)' + ')'
                print("오류 수정 시간 : " + str(errorCorrectionTimeSec) + "Sec" + '(' + str(errorCorrectionTimeMs) + '(ms)' + ')')
                # 로그 파일 작성
                printLog(0, normalTimes, korTimes, resCode, errorCorrectionTime)
    else:
        # 오류 발생 (에러로그)
        print("비정상")
        print("응답코드 : " + str(response.status_code))
        # 에러 시간 측정
        errorTimes = time.time()
        korTimes = time.strftime('%Y-%m-%d'+ ' ' +'%X')
        resCode = response.status_code   
        # 에러 발생시 count 는 0
        countNormalNum = 0
        print("TimeStamp : " + str(int(errorTimes)))
        print("한국시간 : " + str(korTimes))
        # 로그 파일 작성
        if firstErrorTime:
            firstErrorTime = False
            printLog(2, errorTimes, korTimes, resCode, 0)    
        else:
            printLog(1, errorTimes, korTimes, resCode, 0)
    print("------- - ------- - -------")


def printLog(_result, _times, _kortimes, _code, _ectimes):    
    timeStamp = int(_times)
    log_message = ""
    # 실패 ->성공
    if _result == 0:
        log_message = f"TimeStamp: {timeStamp} KST : {_kortimes} Code: {_code} Error correction time: {_ectimes}\n"
    elif _result == 2:
        log_message = f"TimeStamp: {timeStamp} KST : {_kortimes} Code: {_code} StartError\n"
    # 성공 or 실패                    
    else:
        log_message = f"TimeStamp: {timeStamp} KST : {_kortimes} Code: {_code}\n"
    #log 파일 작성     
    with open("expandability_test_result.log", "a") as f:
        f.write(log_message)
while True:
    runStart = time.time()
    getHttp()
    runEnd = time.time()
    runtime = runEnd - runStart
    print("runtime : " + str(runtime))
    if runtime <= 0.1:
        time.sleep(0.1 - runtime)
