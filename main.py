from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock
import subprocess


class PhotoBoothForm(BoxLayout):

    def __init__(self, **kwargs):
        super(PhotoBoothForm, self).__init__(**kwargs)
        self.timer_counter = 5
        self.iteration_counter = 1
        start_button = ObjectProperty()

    def button_click(self):
        print('You pressed the start button')
        self.photo_popup = self.PhotoTakerPopUp()
        self.photo_popup.open()
        Clock.schedule_once(self.disable_start_button,0)
        Clock.schedule_interval(self.take_photos,1)

    def disable_start_button(self,*args):
        self.start_button.text = 'PROCESSING...'
        self.start_button.disabled = True

    def enable_start_button(self, *args):
        self.start_button.text = 'Touch here to start'
        self.start_button.disabled = False

    def take_photos(self,*args):
        self.photo_popup.popup_title = 'Picture ' + str(self.iteration_counter ) + ' of 4'
        self.photo_popup.popup_label = str(self.timer_counter)
        if self.timer_counter == 1:
            self.photo_popup.popup_label = 'POSE'
        elif self.timer_counter==0:
            Clock.unschedule(self.take_photos)

            gpout = subprocess.check_output("gphoto2 --capture-image-and-download --filename \
                                            /home/wtb/photobooth_images/temp_photo" + str(self.iteration_counter)
                                            + ".jpg", stderr=subprocess.STDOUT, shell=True)
            print gpout
            if 'ERROR' not in gpout:
                self.iteration_counter += 1

            self.timer_counter = 4

            if self.iteration_counter < 5:
                Clock.schedule_interval(self.take_photos, 1)
            #    self.iteration_counter += 1
            else:
                self.iteration_counter = 1
                self.timer_counter = 5
                self.photo_popup.dismiss()
                Clock.schedule_once(self.enable_start_button,10)

        self.timer_counter -= 1

    def take_photo(self):
        print 'Taking picture'
        gpout = subprocess.check_output("gphoto2 --capture-image-and-download --filename \
                    /home/wtb/photobooth_images/photobooth%H%M%S.jpg", stderr=subprocess.STDOUT, shell=True)
        print gpout

    class PhotoTakerPopUp(Popup):
        popup_label = StringProperty('GET READY')
        popup_title = StringProperty()

class PhotoBoothApp(App):
    pass


if __name__ == '__main__':
    PhotoBoothApp().run()
