import cv2 as cv
import imutils as im
import numpy as np

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
    element_id = 1
    element_type = "Resistor"
    
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
                    all_points.append([pt, next_angle, actual_scale, element_id, element_type, width, height])
                    element_id += 1

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

    height, width = template_gray.shape
    
    res = modifiedTemplateMatch(img_gray, template_gray, thresh, [0,360], 45, [50,300], 10, True)
        
    for pt in res[::-1]:
        if pt[1] == 90 or pt[1] == 270:
            scaled_width = height * pt[2] / 100
            scaled_height = width * pt[2] / 100
        else:
            scaled_width = width * pt[2] / 100
            scaled_height = height * pt[2] / 100
        cv.rectangle(img_bgr, pt[0], (pt[0][0] + round(scaled_width), pt[0][1] + round(scaled_height)), (255,255,255), -1)
    
    
    cv.imwrite('./results/results_' + img, img_bgr)

    return res, img_bgr

def detect_lines(image):
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    (thresh, black) = cv.threshold(gray, 127, 255, cv.THRESH_BINARY)
    edges = cv.Canny(black, 50, 150, apertureSize=3, L2gradient=True)

    lines_list = []
    lines = cv.HoughLinesP(
        edges,  # Input edge image
        3,  # Distance resolution in pixels
        np.pi / 180,  # Angle resolution in radians
        threshold=60,  # Min number of votes for valid line
        minLineLength=10,  # Min allowed length of line
        maxLineGap=3  # Max allowed gap between line for joining them
    )

    if lines is not None:
        for points in lines:
            x1, y1, x2, y2 = points[0]
            line_i = [(x1, y1), (x2, y2)]
            keep_line = True
            for j in range(len(lines_list)):
                angle_diff = abs(angle(line_i) - angle(lines_list[j]))
                if angle_diff < np.pi/10:
                    dist_diff = abs(distance(line_i) - distance(lines_list[j]))
                    if dist_diff < 10:
                        keep_line = False
                        break
            if keep_line:
                cv.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                lines_list.append(line_i)

        cv.imwrite('./results/detectedLines.png', image)
    else:
        print("No lines detected")

    return lines_list

def angle(line):
    x1, y1 = line[0]
    x2, y2 = line[1]
    return np.arctan2(y2-y1, x2-x1)

def distance(line):
    x1, y1 = line[0]
    x2, y2 = line[1]
    return np.sqrt((x2-x1)**2 + (y2-y1)**2)

def check_connection(elements, lines):
    connections = []
    
    for line in lines:
        startConnected, endConnected = False, False
        startId, endId = 0, 0
        
        for element in elements:
            if is_near_rect(line[0], element[0], element[1], element[5], element[6]):
                startConnected = True
                startId = element[3]
            if is_near_rect(line[1], element[0], element[1], element[5], element[6]):
                endConnected = True
                endId = element[3]
        if startConnected and endConnected and endId != startId:
            connections.append([startId, endId])
    return connections
        

def is_near_rect(point, center, rotation, width, height):
    x, y = point
    cx, cy = center

    if rotation == 90 or rotation == 270:
        actual_width = height
        actual_height = width
    else:
        actual_width = width
        actual_height = height

    if cx - 25 <= x + actual_width / 2 <= cx + actual_width  + 25 and cy - 25 <= y + actual_height / 2 <= cy + actual_height  + 25:
        return True
    else:
        return False

def element_to_JSON(element):
    data = {}
    data['type'] = element[4]
    data['posX'] = element[0][0]
    data['posY'] = element[0][1]
    data['id'] = element[3]
    data['rot'] = int(element[1] / 90)

    return data
        
def connection_to_JSON(connection_data):
    data = {}

    data['type'] = "Connection"
    data['anchor1'] = connection_data[0]
    data['anchor2'] = connection_data[1]

    return data   
    
def main(img):
    elements, template1_img = template_match(img, 'template1.png', 0.9);

    lines = detect_lines(template1_img)

    connections = check_connection(elements, lines)

    data = []

    for element in elements:
        data.append(element_to_JSON(element))
    for connection in connections:
        data.append(connection_to_JSON(connection))

    return data
