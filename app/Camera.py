import datetime

import gphoto2 as gp

from os.path import join


class CameraConnection():
    def __init__(self, liveview_path, photos_path):
        # Connect to camera
        self.context = gp.gp_context_new()
        self.camera = gp.check_result(gp.gp_camera_new())
        gp.check_result(gp.gp_camera_init(self.camera, self.context))

        # Some params
        self.preview_path = liveview_path
        self.photos_path = photos_path
        
    def _clear_event_queue(self):
        while True:
            type_, data = self.camera.wait_for_event(10)
            if type == gp.GP_EVENT_TIMEOUT:
                return

    def _capture_preview(self):
        preview = gp.check_result(gp.gp_camera_capture_preview(self.camera, self.context))
        result = gp.check_result(gp.gp_file_save(preview, self.preview_path))
        return(result)


    def _capture_photo(self):
        file_path = gp.check_result(gp.gp_camera_capture(
            self.camera, gp.GP_CAPTURE_IMAGE, self.context))

        target = join(self.photos_path, self._photo_namer())

        camera_file = gp.check_result(gp.gp_camera_file_get(
                self.camera, file_path.folder, file_path.name,
                gp.GP_FILE_TYPE_NORMAL, self.context))
        
        # Get photo
        gp.check_result(gp.gp_file_save(camera_file, target))
        
        return(target)

    def _photo_namer(self):
        now = datetime.datetime.now()
        return('{}{}{}_{}_{}_{}.jpg'.format(
            now.year, now.month, now.day, now.hour, now.minute, now.second)
        )

    def release(self):
        gp.check_result(gp.gp_camera_exit(self.camera, self.context))
        return(1)
