import os

# import cv2
import numpy as np
from tensorflow.keras.models import load_model

def pinterest(memberno, data):
    data = np.array(data.split(','), dtype=int)
    print('-> data: ', data)

    data = np.array([data])
    print('-> data: ', data)

    path = os.path.dirname(os.path.abspath(__file__))
    print('-> path:', path) # -> path: C:\kd\ws_python\django_basic\ais\AImodels

    model = load_model(os.path.join(path, 'Pinterest.h5')) # 모델 읽기
    p = model.predict(data) # 모델 사용
    print('-> p:', p) # [[0.54815423 0.01504818 0.01776066 0.16331927 0.25571758]]
    
    # 0: 카운터, 1: 배달대행, 2: 물류, 3: 재택근무, 4: 음식점, 5: 임상시험, 6: 기타  
    index = np.argmax(p) 
    print('-> index: ', index) # 0 ~ 4
    per = round(np.max(p) * 100, 1)
    print('-> per: ', per) 


    if index == 0:
        label = '카운터'
    elif index == 1:
        label = '배달대행'
    elif index == 2:
        label = '물류'
    elif index == 3:
        label = '재택근무'
    elif index == 4:
        label = '음식점'
    elif index == 5:
        label = '임상시험'
    elif index == 6:
        label = '기타'

    result = {}
    if per >= 20:
        result = {"index": index, "label": label, "per": per}
    else:
        result = {"index": index, "label": f'가장 인접한 추천: {label}', "per": per}
   
    # ------------------------------------------------------------
    # Oracle에 추천 카테고리 번호 등록
    # cate 테이블: 1번~5번 카테고리가 등록되어 있어야함.
    # member 테이블: 사용하려면 회원이 등록되어 있어야 테스트 가능
    # ------------------------------------------------------------
    import cx_Oracle  # Oracle
    from sqlalchemy import create_engine  # Pandas -> Oracle
    
    # Oracle Connection 연결, kd 계정으로 XE 사용.
    # conn = cx_Oracle.connect('kd/1234@localhost:1521/XE')
    conn = cx_Oracle.connect('team4/1234@43.201.72.175:1521/XE')
    cursor = conn.cursor() # SQL 실행 객체 생성
    
    # 기존의 추천 정보 삭제
    sql='''
    DELETE FROM recommendation WHERE memberno=:memberno
    '''
    cursor.execute(sql, [memberno]) 
    conn.commit()

    # 새로운 추천 정보 등록
    sql = '''
    INSERT INTO recommendation(recomno, memberno, jobcateno, recom, rcdate)
    VALUES(recommendation_seq.nextval, :memberno, :jobcateno, :recom, sysdate)
    '''
    # print(type(memberno)) # str
    # print(type(index))
    # index: 0 ~, seq: 1 가지만 추천 
    cursor.execute(sql, [memberno, int(index+1), 1]) # np.int32등을 지원하지 않음.
    conn.commit()
    
    cursor.close()
    conn.close() 
    # ------------------------------------------------------------

    return result