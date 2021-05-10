from camera import Camera
from cart import Cart
from cruiser import Cruiser

if __name__ == '__main__':
    # init
    front_camera = Camera()
    cruiser = Cruiser()
    cart = Cart()
    front_camera.start()

    # param set
    cart.speed = 50

    while True:
        front_image = front_camera.read()
        angle = cruiser.cruise(front_image) * 4
        print('angle = {}'.format(angle))  # DEBUG
        cart.steer(cart.speed, angle)











