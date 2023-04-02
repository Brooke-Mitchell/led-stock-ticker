import time

from constants import LOADING_IMAGE
from renderer.renderer import Renderer
from util.color import Color
from util.position import Position
from util.utils import align_text, load_image, align_image, off_screen
from version import __version__
import requests


class UserRenderer(Renderer):
    """
    Render user information

    Arguments:
        data (api.Data):        Data instance

    Attributes:
        coords (dict):          Coordinates dictionary
    """

    def __init__(self, matrix, canvas, draw, config, data):
        super().__init__(matrix, canvas, draw, config)
        self.data = data
        self.coords = self.config.layout.coords['user']

    def render(self):
        self.clear()
        self.render_logo()
        self.render_version()
        self.matrix.SetImage(self.canvas)
        time.sleep(self.config.rotation_rate)

    def render_version(self):
        x, y = align_text(self.font.getsize('FINBERRY'),
                          self.matrix.width,
                          self.matrix.height,
                          Position.RIGHT,
                          Position.TOP)
        self.draw.text((x, y), 'FINBERRY', Color.PURPLE, self.font)
        for x in range(0, 10):  # try 10 times
            try:
                userName = requests.get('https://finberry-stock-simulator-server.vercel.app/account/user?basicMode=true&email=brookemitchell120@gmail.com')
                userName = userName.json()
                str_error = None
            except Exception as str_error:
                pass

            if str_error:
                time.sleep(2)  # wait for 2 seconds before trying to fetch the data again
            else:
                break
        user = userName[0]['username'] 
        x, y = align_text(self.font.getsize(user),
                          self.matrix.width,
                          self.matrix.height,
                          Position.CENTER,
                          Position.BOTTOM)
        if off_screen(self.matrix.width, self.font.getsize(user)[0]):
            self.scroll_text(user, self.font, Color.GREEN, Color.BLACK, (1, y))
        else:
            self.draw.text((x, y), user, Color.GREEN, self.font)

    def render_logo(self):
        img = load_image(LOADING_IMAGE, tuple(self.coords['image']['size']))
        x, y = align_image(img,
                           self.matrix.width,
                           self.matrix.height,
                           Position.LEFT,
                           Position.TOP)
        y += self.coords['image']['position']['offset']['y']
        self.canvas.paste(img, (x, y))