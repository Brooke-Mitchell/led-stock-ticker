import time

from constants import DOWNWARD_IMAGE,UPWARD_IMAGE,EQUAL_IMAGE
from renderer.renderer import Renderer
from util.color import Color
from util.position import Position
from util.utils import align_text, load_image, align_image, off_screen
from version import __version__
import requests


class BalanceRenderer(Renderer):
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
        self.coords = self.config.layout.coords['balance']

    def render(self):
        self.clear()
        self.render_version()
        self.render_logo()
        self.matrix.SetImage(self.canvas)
        time.sleep(self.config.rotation_rate)

    def render_version(self):
        balance = requests.get('https://finberry-stock-simulator-server.vercel.app/game/balancecalculation/balance/simulatoremail/6425108e872b0491c9873188/brookemitchell120@gmail.com')
        balance = balance.json()
        total = balance['stockBalance'] + balance['cashBalance']
        self.LossGainBalance=3000-50000
        total_string='Total= $ '+str(total)
        GainLoss='$ '+str(self.LossGainBalance)
        x, y = align_text(self.font.getsize(total_string),
                          self.matrix.width,
                          self.matrix.height,
                          Position.RIGHT,
                          Position.TOP)
        self.draw.text((x, y), total_string, Color.PURPLE, self.font)

        x, y = align_text(self.font.getsize(GainLoss),
                          self.matrix.width,
                          self.matrix.height,
                          Position.RIGHT,
                          Position.CENTER)
        if(self.LossGainBalance<0):
            self.draw.text((x, y), GainLoss, Color.RED, self.font)
        elif(self.LossGainBalance==0):
            self.draw.text((x, y), GainLoss, Color.YELLOW, self.font)
        else:
            self.draw.text((x, y), GainLoss, Color.GREEN, self.font)

    def render_logo(self):
        if(self.LossGainBalance<0):
            img = load_image(DOWNWARD_IMAGE, tuple(self.coords['image']['size']))
        elif(self.LossGainBalance==0):
            img = load_image(EQUAL_IMAGE, tuple(self.coords['image']['size']))
        else:
            img = load_image(UPWARD_IMAGE, tuple(self.coords['image']['size']))
        x, y = align_image(img,
                           self.matrix.width,
                           self.matrix.height,
                           Position.LEFT,
                           Position.CENTER)
        y += self.coords['image']['position']['offset']['y']
        self.canvas.paste(img, (x, y))