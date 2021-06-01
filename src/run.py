#%%
import settings
from camera import Camera
from cart import Cart
from cruiser import img_deal, init_predictor, angle_predict

settings.set_working_dir()

front_camera = Camera()
angle_predictor = init_predictor()
cart = Cart()

cart.speed = settings.velocity

while True:
    front_image = front_camera.read()
    img, mask = img_deal(front_image)

    # DEBUG
    # cv2.imwrite('debug/{}.jpg'.format(cnt), front_image)
    # cv2.imwrite('debug_hsv/{}.jpg'.format(cnt), mask)

    cart.angle = angle_predict(img, angle_predictor)

    cart.steer(cart.speed, cart.angle)
