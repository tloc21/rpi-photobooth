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
        self.iteration_counter = 0
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

    def take_photos(self,*args):
        self.photo_popup.popup_title = 'Picture ' + str(self.iteration_counter +1 ) + ' of 4'
        self.photo_popup.popup_label = str(self.timer_counter)
        if self.timer_counter == 0:
            self.photo_popup.popup_label = 'POSE'
            Clock.unschedule(self.take_photos)
            try:
                subprocess.check_output("gphoto2 --capture-image-and-download --filename \
                                /home/wtb/photobooth_images/photobooth%H%M%S.jpg", stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError as e:
                print e.returncode, e.output

            #if 'ERROR' not in gpout:
            #    self.iteration_counter +=1
            #elif '-52: \'Could not find the requested device on the USB port\'' in gpout:
            #    print 'Could not detect USB camera'
            #    Clock.schedule_once(self.__init__())
            self.timer_counter = 6
            if self.iteration_counter < 4:
                Clock.schedule_interval(self.take_photos, 1)
            else:
                self.iteration_counter = 0
                self.timer_counter = 6
                self.photo_popup.dismiss()
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
