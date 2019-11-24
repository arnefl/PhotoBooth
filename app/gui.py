import time
import re

import tkinter as tk

from os import getcwd
from tkinter import messagebox
from tkinter import simpledialog
from PIL import ImageTk, Image
from app.EmailManager import SendEMail


# GUI manager
class PhotoBoothGUI():
    def __init__(self, camera, config):
        self.ErrorState = False
        self.config = config
        
        # Init tk root
        self.root = tk.Tk()
        self.root.title("Photobooth")
        self.root.geometry("1000x900+0+0") # width x height +x +y
        self.root.configure(background='black')
        self.root.resizable(0,0)

        # Fullscreen
        self.StateFullScreen = True
        self.root.attributes('-fullscreen', True)
        self.root.bind("<Control-slash>", self.toggle_fullscreen)
        #self.root.bind("<Escape>", self.toggle_fullscreen)

        # Centering
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(4, weight=1)

        # Save camera object for later
        self.camera = camera

        ############################
        # Heading
        self.RootHeading = tk.Label(self.root, text="Photo booth")
        self.RootHeading.grid(row=0, column=1)
        self.RootHeading.config(height=2,
                           bg="black",
                           font=("Stylish Calligraphy Demo", 80),
                           foreground="white")

        #############################
        # Take photo button
        self.RootTakePhotoButton = tk.Label(self.root)
        #RootTakePhotoButton.config(bg="red", foreground="black")
        self.RootTakePhotoButton.bind('<Button-1>', self._capture_photo)

        self.buttonfile = 'icons/camera_icon.png'
        self.photo = Image.open(self.buttonfile)
        self.photo = self.photo.convert("RGBA") # transparency
        self.photo = self.photo.resize((90,90), Image.ANTIALIAS) # 1024x680
        self.photo = ImageTk.PhotoImage(self.photo)
        self.RootTakePhotoButton.config(borderwidth=0,
                                   background='black',
                                   fg='black',
                                   image=self.photo,
                                   width="90",
                                   height="90")
        self.RootTakePhotoButton.grid(row=2,column=1,pady=20)


        ##############################
        # Prepare the live view label
        self.scaleFactor = 1.2
        self.RootLiveViewPanelWidth = int(1024/self.scaleFactor)
        self.RootLiveViewPanelHeight = int(680/self.scaleFactor)

        self.RootLiveViewPanel = tk.Label(self.root, borderwidth=0)
        self.RootLiveViewPanel.grid(row=1, column=1, pady=0)

        # Start live view updater
        self._updateLiveView()

    def toggle_fullscreen(self, event=None):
        self.StateFullScreen = not self.StateFullScreen
        self.root.attributes('-fullscreen', self.StateFullScreen)

    def _cancel_after(self, job_id):
        if job_id is not None:
            self.root.after_cancel(job_id)
            job_id = None

    def _updateLiveView(self):
        # Take new photo and update the GUI
        try:
            self.camera._capture_preview()
            self._set_root_photo(self.camera.preview_path)

            # Repeat in n milliseconds
            self._live_view_job = self.root.after(80, self._updateLiveView) # Run function in mainloop every n milliseconds
        except:
            self.ErrorState = True
            self.root.quit()

    def _set_root_photo(self, photo):
        self.img = Image.open(photo)
        self.img = self.img.transpose(Image.FLIP_LEFT_RIGHT)
        self.img = self.img.resize((self.RootLiveViewPanelWidth,self.RootLiveViewPanelHeight), Image.ANTIALIAS)
        self.img = ImageTk.PhotoImage(self.img)
        self.RootLiveViewPanel.configure(image=self.img)
        self.RootLiveViewPanel.image = self.img

    def _capture_photo(self, event=None):
        # Count to three
        self.counter = 3
        self.StartTime = time.time()

        # Init counter
        self.RootCountDown = tk.Label(self.root, text=self.counter)
        self.RootCountDown.grid(row=2, column=1, sticky="WENS")
        self.RootCountDown.config(height=2,
                             bg="black",
                             font=("Stylish Calligraphy Demo", 60),
                             foreground="red")

        while self.counter >= 0:
            self.RootCountDown.config(text=self.counter)
            self.root.update()

            if self.counter > 0:
                time.sleep(1/20)

            # Update counter
            self.counter = 3 + int(self.StartTime - time.time())

        self.root.update()

        # Take photo
        try:
            MailPhotoTarget = self.camera._capture_photo()
            self.RootCountDown.destroy()

            # Handle complete photo
            self._process_new_photo(MailPhotoTarget)
        except:
            self.ErrorState = True
            self.root.quit()

        return(1)

    def _process_new_photo(self, MailPhotoTarget):
        # Stop the live view
        self._cancel_after(self._live_view_job)
        self._set_root_photo(MailPhotoTarget)
        self.MailPhotoTarget = MailPhotoTarget

        # Make a frame for two new buttons
        self.RootProcessPhotoFrame = tk.Frame(height=2, bd=0, bg='black')
        self.RootProcessPhotoFrame.grid(row=2, column=1, sticky="WENS")

        self.RootProcessPhotoFrame.grid_columnconfigure(0, weight=2)
        self.RootProcessPhotoFrame.grid_columnconfigure(2, weight=1)
        self.RootProcessPhotoFrame.grid_columnconfigure(4, weight=2)

        # Cancel button
        self.cancelbuttonfile = 'icons/cancel_icon.png'
        self.cancelphoto = Image.open(self.cancelbuttonfile)
        self.cancelphoto = self.cancelphoto.convert("RGBA") # transparency
        self.cancelphoto = self.cancelphoto.resize((70,70), Image.ANTIALIAS) # 1024x680
        self.cancelphoto = ImageTk.PhotoImage(self.cancelphoto)

        self.RootProcessPhotoCancel = tk.Label(self.RootProcessPhotoFrame)
        self.RootProcessPhotoCancel.grid(row=0, column=1, pady=20)
        self.RootProcessPhotoCancel.config(width="70",
                                           height="70",
                                           image=self.cancelphoto,
                                           bg='black')
        self.RootProcessPhotoCancel.bind('<Button-1>', self._process_new_photo_cancel)

        # Make button to send email
        self.mailbuttonfile = 'icons/email_icon.png'
        self.mailphoto = Image.open(self.mailbuttonfile)
        self.mailphoto = self.mailphoto.convert("RGBA") # transparency
        self.mailphoto = self.mailphoto.resize((70,70), Image.ANTIALIAS) # 1024x680
        self.mailphoto = ImageTk.PhotoImage(self.mailphoto)

        self.RootProcessPhotoMail = tk.Label(self.RootProcessPhotoFrame)
        self.RootProcessPhotoMail.grid(row=0, column=3, pady=20)
        self.RootProcessPhotoMail.config(width="70",
                                         height="70",
                                         image=self.mailphoto,
                                         bg='black')
        self.RootProcessPhotoMail.bind('<Button-1>', self._process_new_photo_mail)
        
    def _process_new_photo_cancel(self, event=None):
        # Delete the two buttons
        self.RootProcessPhotoFrame.destroy()

        # Start live view updater
        self._updateLiveView()

    def _process_new_photo_mail(self, event=None):
        # Try to get an email from the user
        emailVerifier = None
        emailCancel = False

        while emailVerifier is None and not emailCancel:
            # Get email adr
            email = simpledialog.askstring("Email", "Enter your email address")

            if email is None:
                # User cancelled
                emailCancel = True
            else:
                # Verify email input
                emailVerifier = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)

                if emailVerifier is None:
                    if messagebox.askretrycancel("Error", "There was something wrong with the email address. Try again?"):
                        pass
                    else:
                        emailCancel = True

        # Send email unless user opted to cancel
        if not emailCancel:
            # Make a small version of image (6000 × 4000)
            size = (1500, 1000)
            NewImagePath = self.MailPhotoTarget.replace('.jpg', '_mail.jpg')
            img = Image.open(self.MailPhotoTarget)
            img = img.convert('RGB')
            img = img.resize(size, Image.ANTIALIAS)
            img.save(NewImagePath)


            # Send it!
            SendEMail(email,
                     self.config['email']['subject'],
                     self.config['email']['text'],
                     NewImagePath,
                     self.config['email']['user'],
                     self.config['email']['password'],
                     self.config['email']['smtp_server'],
                     self.config['email']['smtp_port'])

            # Delete the two buttons
            self.RootProcessPhotoFrame.destroy()

            # Start live view updater
            self._updateLiveView()
