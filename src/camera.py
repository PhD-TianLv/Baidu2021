import cv2
from threading import Thread


class Camera:
    def __init__(self, src=0, shape=[480, 320], autoStart=True):
        self.stream = cv2.VideoCapture(src)
        # self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, shape[0])
        # self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, shape[1])
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        # self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter::fourcc('M', 'J', 'P', 'G'));
        # self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y', 'U', 'Y', 'V'));
        self.running = True
        if not autoStart:
            self.running = False
        for _ in range(10):  #warm up the camera
            (self.grabbed, self.frame) = self.stream.read()

        self.start()

    def start(self):
        self.running = True
        Thread(target=self.update, args=()).start()

    def stop(self):
        self.running = False

    def update(self):
        while self.running:
            (self.grabbed, self.frame) = self.stream.read()
            # print(self.frame)
            # time.sleep(1)
            # if self.src == 0:
            #     path = "images/{}.png".format(count);
            #     count = count + 1;
            #     cv2.imwrite(path, self.frame);

    def read(self):
        assert self.running, 'camera stoped'
        return self.frame
