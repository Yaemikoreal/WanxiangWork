import cv2


class ImageRecognition:
    def __init__(self, **kwargs):
        self.image_path = kwargs.get("image_path")

    def detect_license_plate(self, image_path):
        """
        从给定的图像路径加载图像，并尝试检测车牌。
        """
        # 加载图像并转换为灰度图像
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 高斯模糊减少噪声
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 30, 200)

        # 查找轮廓
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        plate_contour = None

        # 筛选合适的轮廓
        for contour in contours:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

            # 假设车牌是矩形或四边形
            if len(approx) == 4 and cv2.contourArea(contour) > 1000:
                plate_contour = approx
                break

        # 如果找到了车牌轮廓
        if plate_contour is not None:
            cv2.drawContours(image, [plate_contour], -1, (0, 255, 0), 3)
            x, y, w, h = cv2.boundingRect(plate_contour)
            roi = image[y:y + h, x:x + w]
            cv2.imshow("License Plate", roi)

        # 显示原始图像和边缘图像
        cv2.imshow("Original Image", image)
        cv2.imshow("Edge Detection", edged)

        # 等待按键后关闭窗口
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def calculate(self):
        self.detect_license_plate(image_path=self.image_path)


def main():
    data_dt = {
        "url": 'https://image.baidu.com/search/index',
        "image_path": 'car.png'
    }
    obj = ImageRecognition(**data_dt)
    obj.calculate()


if __name__ == '__main__':
    main()
