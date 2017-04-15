from PIL import Image
import os
import hashlib
import time
from .. import photos

def image_thumbnail(infile):
    #thumbnail size
    size = (480, 270)

    outfile = os.path.splitext(photos.path(infile))[0] + '_t.jpg'
    if infile != outfile:
        # try:
        im = Image.open(photos.path(infile))
        im.thumbnail(size)
        im.save(outfile, "JPEG")
        filename, ext = os.path.splitext(infile)
        # filename, ext = os.path.splitext(photos.url(infile))
        url_t = filename + '_t.jpg'
        return url_t
        # except IOError:
        #     print("cannot create thumbnail for", infile)

def save_image(files):
    # photo_amount = len(files)
    # if photo_amount > 50:
    #     flash(u'抱歉，测试阶段每次上传不超过50张！', 'warning')
    #     return redirect(url_for('.new_album'))

    images = []
    for img in files:
        filename = hashlib.md5(str(time.time()).encode()).hexdigest()[:10]
        image = photos.save(img, name=filename + '.')
        file_url = photos.url(image)
        url_t = image_thumbnail(image)
        images.append((image, url_t))
        # print(images)
    return images

