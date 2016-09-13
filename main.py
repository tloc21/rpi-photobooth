#!/usr/bin/env python

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen
import os, sys, subprocess, multiprocessing, time, traceback


class PhotoBoothScreenManager(ScreenManager):
    pass

class StartScreen(Screen):

    def start_button_click(self):
        Clock.schedule_once(self.goto_photo_screen,-1)
        Clock.schedule_interval(self.parent.ids.photo_screen.take_photos,1)

    def restart_button_click(self):
#        os.execv(__file__, sys.argv)
        App.get_running_app().stop()

    def reboot_button_click(self):
        os.system('sudo reboot')

    def goto_photo_screen(self, *args):
        self.manager.current = 'take_photo_screen'


class TakePhotoScreen(Screen):

    take_photo_title = StringProperty(' ')
    take_photo_label = StringProperty('GET READY!')
    take_photo_label_size = NumericProperty(100)

    def __init__(self, **kwargs):
        super(TakePhotoScreen,self).__init__(**kwargs)
        self.timer_counter = 5
        self.iteration_counter = 1
        self.photo_error = False

    def on_pre_enter(self, *args):
        super(TakePhotoScreen, self).on_pre_enter(*args)
        self.timer_counter = 5
        self.iteration_counter = 1
        self.take_photo_label_size = 100
        self.take_photo_label = 'GET READY'
        self.take_photo_title = ' '


    def goto_start_screen(self, *args):
        self.manager.current = 'start_screen'

    def goto_preview_screen(self, *args):
        self.manager.current = 'preview_screen'

    def pose_label(self,  *args):
        self.take_photo_label = 'POSE'

    def show_camera_error(self, *args):
        self.take_photo_label_size = 65
        self.take_photo_label = 'Camera Not Found'
		
	def take_photo_countdown(self, *args):
		if self.timer_counter > 0:
			self.take_photo_label = str(self.timer_counter)
			Clock.schedule_once(self.take_photo_countdown, 1)
		elif self.timer_counter == 0:
			self.take_photo_label = 'POSE'
			self.snap_photo(self.photo_error)
		self.timer_counter -= 1
		
	def take_four_photos(self, *args):
		self.take_photo_title = 'Picture ' + str(self.iteration_counter ) + ' of 4'
		self.take_photo_label = 'GET READY'
		self.timer_counter = 3
		Clock.schedule_once(self.take_photo_countdown)
		if self.iteration_counter < 4:
			self.iteration_counter += 1
			Clock.schedule_once(self.take_four_photos,1)
	
	def snap_photo(self, photo_error):
		try:
            gpout = subprocess.check_output("sudo gphoto2 --capture-image-and-download --filename \
                                            /home/pi/photobooth_images/temp_photo" + str(self.iteration_counter)
                                            + ".jpg --force-overwrite", stderr=subprocess.STDOUT, shell=True)
			if 'ERROR' in gpout and photo_error:
				Clock.schedule_once(self.show_camera_error)
				Clock.schedule_once(self.goto_start_screen, 3)
			else:
				self.timer_counter = 5
				self.photo_error = True
            return False
        except subprocess.CalledProcessError as e:
            print e.output
            Clock.schedule_once(self.show_camera_error)
            Clock.schedule_once(self.goto_start_screen, 3)
            return True

    def take_photos(self,*args):
        self.take_photo_title = 'Picture ' + str(self.iteration_counter ) + ' of 4'

        if self.timer_counter > 0:
            self.take_photo_label = str(self.timer_counter)
        elif self.timer_counter == 0:
            self.take_photo_label = 'POSE'
        else:
            Clock.unschedule(self.take_photos)

            try:
                gpout = subprocess.check_output("sudo gphoto2 --capture-image-and-download --filename \
                                            /home/pi/photobooth_images/temp_photo" + str(self.iteration_counter)
                                                + ".jpg --force-overwrite", stderr=subprocess.STDOUT, shell=True)
                camera_error = False
            except subprocess.CalledProcessError as e:
                print e.output
                camera_error = True
                Clock.schedule_once(self.show_camera_error)
                Clock.schedule_once(self.goto_start_screen, 3)
                return

            if not camera_error:
                print gpout

                if 'ERROR' in gpout:
                    if self.photo_error == True:
                        Clock.schedule_once(self.show_camera_error)
                        Clock.schedule_once(self.goto_start_screen, 3)
                        return
                    else:
                        self.timer_counter = 5
                        Clock.schedule_interval(self.take_photos, 1)
                        # TODO: Handle camera found but couldn't capture photo errors, reset self.iteration_counter
                        self.photo_error = True
                        return
            # reset timer, will be 3 seconds after finishing loop
            self.timer_counter = 4

            if self.iteration_counter < 4:
                Clock.schedule_interval(self.take_photos, 1)
                self.iteration_counter += 1
            else:
                self.iteration_counter = 1
                self.timer_counter = 5
                # TODO: Process photos
                Clock.schedule_once(self.goto_preview_screen, 3)

        self.timer_counter -= 1

class PreviewScreen(Screen):

    def on_pre_enter(self, *args):
        super(PreviewScreen, self).on_pre_enter(*args)
        self.ids.pic1.reload()
        self.ids.pic2.reload()
        self.ids.pic3.reload()
        self.ids.pic4.reload()

    def goto_start(self):
        self.manager.current = 'start_screen'

    def print_photos(self):
        pass

class PhotoBoothApp(App):
    pass

def run_things():
    PhotoBoothApp().run()

def monitor(sleep_time):
    while 1:
        proc = multiprocessing.Process(target=run_things)
        proc.start()
        proc.join()
        if proc.exitcode != 0:
            print('something went wrong... terminating')
            exit(proc.exitcode)

if __name__ == '__main__':
#    PhotoBoothApp().run()
    try:
        sleep_time = int(sys.argv[1])
        monitor(sleep_time)
    except(KeyError,ValueError):
        print('usage: main.py sleeptime')
        exit(1)
