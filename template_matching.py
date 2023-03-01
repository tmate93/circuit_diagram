import cv2 as cv
import imutils as im
import numpy as np
from matplotlib import pyplot as plt

def rotate_image(image, angle):
    result = im.rotate_bound(image, angle)
    return result

def scale_image(image, percent, maxwh):
    max_width = maxwh[1]
    max_height = maxwh[0]
    max_percent_width = max_width / image.shape[1] * 100
    max_percent_height = max_height / image.shape[0] * 100
    max_percent = 0
    if max_percent_width < max_percent_height:
        max_percent = max_percent_width
    else:
        max_percent = max_percent_height
    if percent > max_percent:
        percent = max_percent
    width = int(image.shape[1] * percent / 100)
    height = int(image.shape[0] * percent / 100)
    result = cv.resize(image, (width, height), interpolation = cv.INTER_AREA)
    return result, percent

def modifiedTemplateMatch(image, template, thresh, rot_range, rot_interval, scale_range, scale_interval, rm_redundant):
    height, width = template.shape
    image_maxwh = image.shape
    all_points = []
    
    for next_angle in range(rot_range[0], rot_range[1], rot_interval):
            for next_scale in range(scale_range[0], scale_range[1], scale_interval):
                scaled_template, actual_scale = scale_image(template, next_scale, image_maxwh)
                if next_angle == 0:
                    rotated_template = scaled_template
                else:
                    rotated_template = rotate_image(scaled_template, next_angle)
                
                matched_points = cv.matchTemplate(image,rotated_template,cv.TM_CCOEFF_NORMED)
                satisfied_points = np.where(matched_points >= thresh)
                
                for pt in zip(*satisfied_points[::-1]):
                    all_points.append([pt, next_angle, actual_scale])

    if rm_redundant == True:
        lone_points_list = []
        visited_points_list = []
        for point_info in all_points:
            point = point_info[0]
            scale = point_info[2]
            all_visited_points_not_close = True
            if len(visited_points_list) != 0:
                for visited_point in visited_points_list:
                    if ((abs(visited_point[0] - point[0]) < (width * scale / 100)) and (abs(visited_point[1] - point[1]) < (height * scale / 100))):
                        all_visited_points_not_close = False
                if all_visited_points_not_close == True:
                    lone_points_list.append(point_info)
                    visited_points_list.append(point)
            else:
                lone_points_list.append(point_info)
                visited_points_list.append(point)
        points_list = lone_points_list
    else:
        points_list = all_points

    return points_list

def template_match(img, template, thresh):
    img_bgr = cv.imread('./img/' + img)
    img_gray = cv.cvtColor(img_bgr, cv.COLOR_BGR2GRAY)
    template_bgr = cv.imread('./templates/' + template)
    template_gray = cv.cvtColor(template_bgr, cv.COLOR_BGR2GRAY)

    heigth, width = template_gray.shape
    
    
    res = modifiedTemplateMatch(img_gray, template_gray, thresh, [0,360], 45, [50,300], 10, True)
    print(res)
        
    
    for pt in res[::-1]:
        if pt[1] == 90 or pt[1] == 270:
            scaled_width = heigth * pt[2] / 100
            scaled_heigth = width * pt[2] / 100
        else:
            scaled_width = width * pt[2] / 100
            scaled_heigth = heigth * pt[2] / 100
        cv.rectangle(img_bgr, pt[0], (pt[0][0] + round(scaled_width), pt[0][1] + round(scaled_heigth)), (0,0,255), 2)
    
    
    cv.imwrite('./results/results_' + img, img_bgr)
    return res

template1 = template_match('test.png', 'template1.png', 0.9);
