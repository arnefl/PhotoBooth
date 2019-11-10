#!/Users/wedding/opt/miniconda3/envs/photobooth/bin/python

import os
import time

from app.Configuration import configuration
from app.gui import PhotoBoothGUI
from app.Camera import CameraConnection
from app.SystemProcess import ProcessKillAndWait, CheckIfProcessExists


class Application():
    def __init__(self):
        # Some params
        self.config = configuration()
        self.photos_path = self.config['capture']['photo_path']
        self.liveview_path = self.config['capture']['live_photo_path']

        # Check if camera connected
        print('Looking for a camera.')

        try:
            # 1) Check if connected and PTPCamera not blocking
            self.sony = CameraConnection(self.liveview_path, self.photos_path)
        except:
            # 2) Not connected or 3) connected: wait PTPCamera to show up
            # and kill.
            print('Looking harder.')

            while not CheckIfProcessExists('PTPCamera'):
                time.sleep(1)

            # PTPCamera has showed up. Kill with fire.
            print('Grabbing camera connection.')
            ProcessKillAndWait('PTPCamera')

            # Connect to camera
            self.sony = CameraConnection(self.liveview_path, self.photos_path)

        print('Starting GUI.')
        time.sleep(2)
        self.start_GUI()


    def start_GUI(self):
        self.gui = PhotoBoothGUI(self.sony, self.config)
        self.gui.root.mainloop()

        # Try to close connection
        try:
            self.sony.release()
        except:
            pass


# Run application
if __name__ == '__main__':
    app = Application()

    if app.gui.ErrorState:
        print('An error has occurred.\nWaiting for restart.')

        time.sleep(1)
        del(app)

        print('Restarting.')
        time.sleep(1)
        os.execl('main.py',  'main.py')
