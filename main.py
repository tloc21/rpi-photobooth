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

    take_photo_title = StringProperty('Heyooo')
    take_photo_label = StringProperty('GET READY!')
    def __init__(self, **kwargs):
        super(TakePhotoScreen,self).__init__(**kwargs)
        self.timer_counter = 5
        self.iteration_counter = 0

    def take_photos(self,*args):
        self.take_photo_title = 'Picture ' + str(self.iteration_counter +1 ) + ' of 4'
        self.take_photo_label = str(self.timer_counter)
        if self.timer_counter == 0:
            self.take_photo_label = 'POSE'
            Clock.unschedule(self.take_photos)
            try:
                subprocess.check_output("gphoto2 --capture-image-and-download --filename \
                                /home/wtb/photobooth_images/photobooth%H%M%S.jpg", stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError as e:
                print e.returncode, e.output
                if '-52' in e.output:
                    print 'Could not find camera.'
                    #TODO: add error handling here

            self.timer_counter = 6
            if self.iteration_counter < 4:
                Clock.schedule_interval(self.take_photos, 1)
            else:
                self.iteration_counter = 0
                self.timer_counter = 6
                self.photo_popup.dismiss()
        self.timer_counter -= 1


class PreviewScreen(Screen):
    pass


class PhotoBoothApp(App):
    pass

if __name__ == '__main__':
    PhotoBoothApp().run()