from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QApplication, QLabel
from PySide2.QtMultimedia import QCamera, QCameraInfo, QCameraImageCapture
from PIL import Image, ImageQt


class Camera(QLabel):
    """
        在QCamera获取摄像头图像的基础上使用QLabel进行显示
        方便对图像的大小/拉伸和旋转等进行调整
    """
    def __init__(self, parent) -> None:
        super().__init__(parent)
        # QLabel初始化
        # TODO: 可调整大小
        self.setFixedSize(180, 320)
        # 相机初始化
        self._init_camera()

    def start(self):
        # 定时获取图像
        if self.camera is not None:
            self.camera.start()
            self.timer.start(100)  # 100ms

    def stop(self):
        # 停止获取图像
        if self.camera is not None:
            self.camera.stop()
            self.timer.stop()

    def _init_camera(self):
        # 初始化摄像头和定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self._capture)
        available_cameras = QCameraInfo.availableCameras()
        if len(available_cameras) != 0:
            self.camera = QCamera(available_cameras[0], self)
            self.image_capture = QCameraImageCapture(self.camera)
            self.image_capture.setCaptureDestination(QCameraImageCapture.CaptureToBuffer)
            self.image_capture.imageCaptured.connect(self._show_image)
        else:
            self.camera = None
            self.setText("未检出到摄像头")

    def _show_image(self, request_id, qimage):
        # 图像经过处理再显示
        image = Image.fromqimage(qimage)
        pix_image = self._img_preprocessing(image)
        self.setPixmap(pix_image)
        self.setScaledContents(True)
        QApplication.processEvents()  # refresh

    def _img_preprocessing(self, img):
        # TODO: 调整图像
        img = img.resize((self.height(), self.width()), Image.ANTIALIAS)  # 缩放
        img = img.transpose(Image.ROTATE_90)  # 旋转
        return ImageQt.toqpixmap(img)

    def _capture(self):
        # 截取图像
        self.camera.searchAndLock()
        self.image_capture.capture()
        self.camera.unlock()