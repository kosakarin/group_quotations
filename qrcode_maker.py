import base64, os
from PIL import Image, ImageSequence
from io import BytesIO
from amzqr import amzqr

class qrcode: 
    def __init__(self, text, picture = None, colorized = False, contrast = 1.0, brightness = 1.0, image_type = 'png'):
        self.text = str(text)
        self.picture = picture
        self.colorized = colorized
        self.contrast = contrast
        self.brightness = brightness
        self.image_type = image_type
		
        self.get_qrcode()
        self.load_qrcode_to_base64()
        self.remove_temp_img()

    def get_qrcode(self):
        self.version, self.level, self.qr_name = amzqr.run(self.text,
                                                           picture = self.picture,
                                                           colorized = self.colorized,
                                                           contrast = self.contrast,
                                                           brightness = self.brightness)

    def load_qrcode_to_base64(self):
        qr_img = Image.open(self.qr_name)
        buf = BytesIO()
        if self.image_type == 'png':
            qr_img.save(buf, format = 'PNG')
            self.base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
        elif self.image_type == 'gif':
            print('gif')
            self.info = qr_img.info
            sequence = [f.copy() for f in ImageSequence.Iterator(qr_img)]
            sequence[0].save(buf, format='GIF', save_all=True,
                         append_images=sequence[1:], disposal=2,
                         quality=100, **self.info)
            self.base64_str =  f'base64://{base64.b64encode(buf.getvalue()).decode()}'


    def remove_temp_img(self):
        os.remove(self.qr_name)
