from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
import subprocess


class PhotoBoothScreenManager(ScreenManager):
    pass

class StartScreen(Screen):
    photo_screen = ObjectProperty(None)
    def button_click(self):
        Clock.schedule_once(self.goto_photo_screen,-1)
        #print self.parent.ids.photo_screen
        Clock.schedule_interval(self.parent.ids.photo_screen.take_photos,1)

    def goto_photo_screen(self, *args):
        self.manager.current = 'take_photo_screen'


class TakePhotoScreen(Screen):

    take_photo_title = StringProperty('')
    take_photo_label = StringProperty('GET READY!')

    def __init__(self, **kwargs):
        super(TakePhotoScreen,self).__init__(**kwargs)
        self.timer_counter = 5
        self.iteration_counter = 1

    def goto_preview_screen(self, *args):
        self.manager.current = 'preview_screen'

    def take_photos(self,*args):
        self.take_photo_title = 'Picture ' + str(self.iteration_counter ) + ' of 4'
        self.take_photo_label = str(self.timer_counter)
        if self.timer_counter == 0:
            self.take_photo_label = 'POSE'
            Clock.unschedule(self.take_photos)

            try:
                gpout = subprocess.check_output("gphoto2 --capture-image-and-download --filename \
                                            /home/wtb/photobooth_images/temp_photo" + str(self.iteration_counter)
                                                + ".jpg", stderr=subprocess.STDOUT, shell=True)
                camera_error = False
            except subprocess.CalledProcessError as e:
                print e.output
                camera_error = True

            if not camera_error:
                print gpout

                if 'ERROR' in gpout:
                    # TODO: Handle camera found but couldn't capture photo errors, reset self.iteration_counter
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
    pass

class PhotoBoothApp(App):
    pass

if __name__ == '__main__':
    PhotoBoothApp().run()
