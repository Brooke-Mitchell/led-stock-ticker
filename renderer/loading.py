from constants import LOADING_IMAGE
from renderer.renderer import Renderer
from util.color import Color
from util.position import Position
from util.utils import align_text, load_image, align_image
from version import __version__
import requests


class Loading(Renderer):
    """Render a splash screen while tickers' data is being fetched"""

    def __init__(self, matrix, canvas, draw, config):
        super().__init__(matrix, canvas, draw, config)
        self.coords: dict = self.config.layout.coords['loading']
        self.render()

    def render(self):
        self.render_logo()
        self.render_version()
        self.matrix.SetImage(self.canvas)

    def render_version(self):
        x, y = align_text(self.font.getsize(__version__),
                          self.matrix.width,
                          self.matrix.height,
                          Position.RIGHT,
                          Position.BOTTOM)
        userName = requests.get('https://finberry-stock-simulator-server.vercel.app/account/user?basicMode=true&email=test@testfin.com')
        userName = userName.json()
        user = userName[0]['username'] 
        self.draw.text((x, y), 'Brooke Mitchell', Color.PURPLE, self.font)
        x, y = align_text(self.font.getsize(__version__),
                          self.matrix.width,
                          self.matrix.height,
                          Position.RIGHT,
                          Position.TOP)
        self.draw.text((x, y), 'FINBERRY', Color.PURPLE, self.font)

    def render_logo(self):
        img = load_image(LOADING_IMAGE, tuple(self.coords['image']['size']))
        x, y = align_image(img,
                           self.matrix.width,
                           self.matrix.height,
                           Position.LEFT,
                           Position.TOP)
        y += self.coords['image']['position']['offset']['y']
        self.canvas.paste(img, (x, y))
