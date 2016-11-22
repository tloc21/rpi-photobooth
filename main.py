#!/usr/bin/env python

import multiprocessing
import os
import subprocess
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, NumericProperty


class PhotoBoothScreenManager(ScreenManager):
    pass


class StartScreen(Screen):

    def start_button_click(self):
        Clock.schedule_once(self.goto_photo_screen, -1)
        Clock.schedule_once(self.parent.ids.photo_screen.take_photo_countdown, 1)

    def restart_button_click(self):
        App.get_running_app().stop()

    def reboot_button_click(self):
        os.system('sudo reboot')

    def goto_photo_screen(self, *args):
        self.manager.current = 'take_photo_screen'

    def preview_button_click(self, *args):
        self.manager.current = 'preview_screen'


class ErrorPopup(Popup):
    def __init__(self, **kwargs):
        super(ErrorPopup, self).__init__(**kwargs)
        self.title = 'ERROR'
        self.title_align = 'center'
        self.title_size = 30
        self.content = Label(text = 'Error Text', font_size = 100)
        self.dismiss_time = 3

    def on_open(self, **kwargs):
        Clock.schedule_once(self.dismiss, self.dismiss_time)

    def on_dismiss(self):
        self.dismiss_time = 3


class TakePhotoScreen(Screen):

    take_photo_title = StringProperty(' ')
    take_photo_label = StringProperty('GET READY!')
    take_photo_label_size = NumericProperty(100)

    def __init__(self, **kwargs):
        super(TakePhotoScreen, self).__init__(**kwargs)
        self.timer_counter = 5
        self.iteration_counter = 1
        self.photo_error = False
        self.camera_error = False
        self.error_popup = ErrorPopup()


    def on_pre_enter(self, *args):
        super(TakePhotoScreen, self).on_pre_enter(*args)
        self.timer_counter = 6
        self.iteration_counter = 1
        self.take_photo_label_size = 100
        self.take_photo_label = 'GET READY'
        self.take_photo_title = ' '

    def goto_start_screen(self, *args):
        self.manager.current = 'start_screen'

    def goto_preview_screen(self, *args):
        self.manager.current = 'preview_screen'

    def show_photo_error(self, *args):
        self.take_photo_label = 'CAMERA ERROR, RETRYING'

    def take_photo_countdown(self, *args):
        self.timer_counter -= 1
        if not self.camera_error:
            if self.timer_counter > 0 and self.iteration_counter <= 4:
                if self.photo_error:
                    self.take_photo_title = 'Retrying Picture ' + str(self.iteration_counter) + ' of 4'
                else:
                    self.take_photo_title = 'Picture ' + str(self.iteration_counter) + ' of 4'
                if self.timer_counter == 1:
                    self.take_photo_label = 'POSE'
                else:
                    self.take_photo_label = str(self.timer_counter)
                Clock.schedule_once(self.take_photo_countdown, 1)
            elif self.timer_counter == 0:
                self.camera_error = self.snap_photo()
                self.iteration_counter += 1
                self.timer_counter = 4
                Clock.schedule_once(self.take_photo_countdown, 1)
            if self.iteration_counter > 4:
                self.error_popup.title = 'PLEASE WAIT'
                self.error_popup.content.text = 'PROCESSING'
                self.error_popup.open()
                Clock.schedule_once(self.process_photos)
        else:
            self.error_popup.content.text = 'CAMERA ERROR'
            self.error_popup.open()
            Clock.schedule_once(self.goto_start_screen, 3)
            self.camera_error = False
            self.photo_error = False

    def snap_photo(self):
        try:
            gpout = subprocess.check_output("sudo gphoto2 --capture-image-and-download --filename \
                                            /home/pi/photobooth_images/temp_photo" + str(self.iteration_counter)
                                            + ".jpg --force-overwrite", stderr=subprocess.STDOUT, shell=True)
            print gpout
            if 'ERROR' in gpout and self.photo_error:
                return True
            elif 'ERROR' in gpout and not self.photo_error:
                self.timer_counter = 5
                self.iteration_counter -= 1
                self.photo_error = True
                return False
            else:
                self.photo_error = False
                return False




        except subprocess.CalledProcessError as e:
            print e.output
            return True

    def process_photos(self, *args):
        subprocess.check_output("sudo /home/pi/share/rpi-photobooth/process_photos", stderr=subprocess.STDOUT, shell=True)
        Clock.schedule_once(self.goto_preview_screen)


class PreviewScreen(Screen):

    def __init__(self, **kwargs):
        super(PreviewScreen, self).__init__(**kwargs)
        self.popup = ErrorPopup()
        self.popup.title = 'PLEASE WAIT'
        self.popup.content.text = 'PRINTING'

    def on_pre_enter(self, *args):
        super(PreviewScreen, self).on_pre_enter(*args)
        self.ids.pic1.reload()
        self.ids.pic2.reload()
        self.ids.pic3.reload()
        self.ids.pic4.reload()

    def goto_start(self):
        self.manager.current = 'start_screen'

    def print_photos(self):
        self.popup.open()
        subprocess.check_output("/home/pi/share/rpi-photobooth/print_photos", stderr=subprocess.STDOUT, shell=True)


class PhotoBoothApp(App):
    pass

def run_things():
    PhotoBoothApp().run()


def monitor():
    while 1:
        proc = multiprocessing.Process(target=run_things)
        proc.start()
        proc.join()
        #TODO: Change this back to !=
        if proc.exitcode != 0:
            print('something went wrong... terminating')
            exit(proc.exitcode)


if __name__ == '__main__':
    monitor()
