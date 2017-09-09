import numpy as np
import cv2
import mysql.connector

cap=cv2.VideoCapture('GOPR0579.MP4')
def getProducts():
    myConnection = mysql.connector.connect(host='127.0.0.1', port='3306', user='root', password='admin', database='bigbrother')
    cur = myConnection.cursor()
    cur.execute("Select * from products")
    products = cur.fetchall()
    myConnection.close()
    return  products


def drawProducts(productData):
    for row in productData:
        top = row[2]
        left = row[1]
        bottom = row[4]
        right = row[3]
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 3)
        cv2.putText(frame, row[5], (right + 2, top + 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0,0,255))

while (1):
    ret ,frame=cap.read()
    drawProducts(getProducts())
    cv2.imshow('video',frame)
    k = cv2.waitKey(10)
    if k==27:
        break