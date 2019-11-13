import tkinter
from osmviz.manager import PILImageManager, OSMManager
from PIL import ImageTk

imgr = PILImageManager('RGB')
osm = OSMManager(image_manager=imgr, server='https://a.tile.openstreetmap.de')
image,bnds = osm.createOSMImage( (47.5,48,12,14), 9 )

class Window(tkinter.Frame):
    def __init__(self, master=None):
        tkinter.Frame.__init__(self, master)
        self.master = master
        self.pack(fill=tkinter.BOTH, expand=1)
        
        render = ImageTk.PhotoImage(image)
        img = tkinter.Label(self, image=render)
        img.image = render
        img.place(x=0, y=0)

        
root = tkinter.Tk()
app = Window(root)
root.wm_title("Demo window")
root.geometry("1024x768")
root.mainloop()
