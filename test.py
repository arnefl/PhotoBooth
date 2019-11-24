from app.Camera import CameraConnection

pp = '/Users/wedding/desktop/'
lp = '/Users/wedding/desktop/preview.jpg'


c = CameraConnection(lp,pp)
c._capture_preview()
c._capture_photo()

c._photo_namer()


#c.release()
