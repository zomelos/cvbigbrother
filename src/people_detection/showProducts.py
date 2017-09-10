#import numpy as np
import cv2
import mysql.connector

VISITOR_DATA_TABLE = 'visitor_coordinates'

#cap=cv2.VideoCapture('../../video/GOPR0579.MP4')

myConnection = mysql.connector.connect(host='127.0.0.1', port='3306', user='root', password='toor', database='bigbrother')
cur = myConnection.cursor()

def getProducts():
    cur.execute("Select * from products")
    products = cur.fetchall()
    return  products


def drawProducts(frame, productData):
    #global cv2
    for row in productData:
        top = row[2]
        left = row[1]
        bottom = row[4]
        right = row[3]
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.putText(frame, row[5], (left + 5, top + 10), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0, 255,255))

def storePosition(frame_id, object_id, x, y):
    sql = 'INSERT INTO `' + VISITOR_DATA_TABLE + '` (`frame_id`, `object_id`, `x_coordinate`, `y_coordinate`, `created`)'
    sql += ' VALUES (' + str(frame_id) + ', ' + str(object_id) + ', ' + str(x) + ', ' + str(y) + ', NOW());'
    cur.execute(sql)
    myConnection.commit()

# while (1):
#     ret ,frame=cap.read()
#     drawProducts(getProducts())
#     cv2.imshow('video',frame)
#     k = cv2.waitKey(10)
#     if k==27:
#         break
#
# cap.release()
# cv2.destroyAllWindows()
# myConnection.close()