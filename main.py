#Import des modules nécessaires
from tkinter import *
from tkinter import filedialog 
from shutil import *
from ntpath import *
from os import *
from PIL import Image, ImageTk
from StyleTransfert.style_transfert import apply_style
from TitleGen.gen_title_from_keywords import predict
from TitleGen.object_recognition import detect

#Import des fichiers du projets.


#Variables du fichier à prédéfinir  
filedatapath = "Interface/data/"
imagefilepath = "Interface/images/"
styleimagefilepath = "Interface/style/"
resultimagefilepath = "Interface/result/"
styleselected = ""
listfilename = listdir(imagefilepath)
liststyle = ["style1", "style2", "style3", "style4"]
width = 300
height = 180
widthR = 180
heightR = 130
padxf1 = 50
padyf1 = 10
path_list = []
images_reference_list = []
project_name="Générateur de peintures"
color1="#ebeeb0"
color2="#92001f"
resultitle = ""
style = ["test, 10%","Test2, 50%","test3, 95%"]


def New():
    for i in range(0, len(listfilename)):
        listfilename.pop()
    l = listdir(imagefilepath)
    for i in l:
        remove(imagefilepath + i)
    RefreshWindow()

   
def browseFiles(): 
    filepath = filedialog.askopenfilename(initialdir = "./", 
                                          title = "Select a File", 
                                          filetypes = (("all files","*.*"), ("Text files", "*.txt*")))
    # im = Image.open(filepath)
    # im.save(imagefilepath)
    filename = basename(filepath)
    target = imagefilepath+filename
    copyfile(filepath, target)
    if filename not in listfilename:
        listfilename.append(filename)
    RefreshWindow()

def DeleteStyleImage():
    listimagestyle = listdir(styleimagefilepath)
    n = len(listimagestyle)
    if n > 0:
        for i in listimagestyle:
            remove(styleimagefilepath + i)
    else:
        return True

def browseFilesStyle(): 
    DeleteStyleImage()
    filepath = filedialog.askopenfilename(initialdir = "./", 
                                          title = "Select a File", 
                                          filetypes = (("all files","*.*"), ("Text files", "*.txt*")))
    filename = basename(filepath)
    target = styleimagefilepath+"style.jpg"
    copyfile(filepath, target)
    RefreshWindow()

def DeleteImage(event):
    w = event.widget
    index = int(w.curselection()[0])
    value = w.get(index)
    remove(imagefilepath+value)
    del listfilename[index]
    RefreshWindow()

def RefreshWindow():
    #Affiche la listbox à gauche et ses éléments
    button_delete.delete(0, button_delete.size())   
    for i in range(0, len(listfilename)):
        button_delete.insert(i, listfilename[i])

    #Affiche les image du milieu
    listimage = listdir(imagefilepath)
    listcanvas = [canvas1, canvas2, canvas3, canvas4, canvas5, canvas6]
    i = 0
    for i in range(0, len(listimage)) :
        file_path = imagefilepath + listfilename[-i-1]
        img = Image.open(file_path)
        #On resize l'image afin d'avoir un meilleur affichage
        resized_img= img.resize((width+20,height+20), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(resized_img)
        listcanvas[i].itemconfigure(listrefimage[i], image=photo)
        listcanvas[i].image = photo
        i = i+1
    if i <= 5:
        for j in range(i, 6):
            listcanvas[j].itemconfigure(listrefimage[j], image=bgphoto)
            listcanvas[j].image = bgphoto
    #Affiche l'image de style  à droite
    listimagestyle = listdir(styleimagefilepath)
    n = len(listimagestyle)
    if n > 0 :
        file_path = styleimagefilepath + listimagestyle[0]
        img = Image.open(file_path)
        resized_img= img.resize((widthR+20,heightR+20), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(resized_img)
        canvas_right.itemconfigure(refstyleimage, image=photo)
        canvas_right.image = photo
    elif n == 0:
        canvas_right.itemconfigure(refstyleimage, image=bgphoto)
        canvas_right.image = bgphoto



def SelectStyle(event):
    global styleselected
    w = event.widget
    index = int(w.curselection()[0])
    value = w.get(index)
    styleselected = value
    RefreshWindow()

def Fusion():
    # fusion d'élements
    os.system('python PaintingFusion/painting_fusion.py') 

    # application du style
    style = "Interface/style/style.jpg"
    content = "Interface/result/fusion.jpg"
    img_result = "Interface/result/final.jpg"
    apply_style(content, style, img_result)

    # titre sur img_result
    w, p = detect(img_result)
    title = predict(w)

    # TODO what you want from title
    
    return True

def SaveResult():

    folder = filedialog.askdirectory(initialdir = "/", 
                                          title = "Choisissez un dossier")
    listresult = listdir(resultimagefilepath)
    if len(listresult) > 0:
        filename = listresult[0]
        filepath = resultimagefilepath + listresult[0]
        print(filepath)
        target = folder+"/"+filename
        print(target)
        copyfile(filepath, target)
    else:
        return True

    




window = Tk()
#bar de nav
menu_bar = Menu(window)
menu_file = Menu(menu_bar, tearoff = 0)
menu_file.add_command(label="Nouveau", command=New)
menu_file.add_command(label="Sauvegarder le résultats", command=SaveResult)
menu_file.add_command(label="Quitter", command=window.quit)

menu_edit = Menu(menu_bar, tearoff = 0)
menu_edit.add_command(label="Fusion", command=Fusion)

menu_bar.add_cascade(label="File", menu=menu_file)
menu_bar.add_cascade(label="Edit", menu=menu_edit)
window.config(menu=menu_bar)

#Personalisation
window.title(project_name)
window.config(background=color1)
window.geometry("1920x1080")
window.minsize(480,360)
img= (Image.open(filedatapath + "background.png"))
resized_image= img.resize((1920,1080), Image.ANTIALIAS)
bg = ImageTk.PhotoImage(resized_image)  
label1 = Label( window, image = bg)
label1.place(x = 0, y = 0)

#Frame : 

frame_top = Frame(window, padx = padxf1, pady = padyf1, bg = color1, highlightbackground=color2, highlightthickness=5)
frame_left = Frame(window, bg = color1, highlightbackground=color2, highlightcolor=color2, highlightthickness=5)
frame_right = Frame(window, bg = color1, highlightbackground=color2, highlightcolor=color2, highlightthickness=5)
frame_middle = Frame(window, bg = color1, highlightbackground=color2, highlightthickness=5, padx=5, pady=5)
frame_bottom = Frame(window, bg = color1, highlightbackground=color2, highlightthickness=5, padx=5, pady=5)
frame_listbox=Frame(frame_left, bg = color1, highlightbackground=color2, highlightcolor=color2, highlightthickness=5)
frame_listbox_right=Frame(frame_right, bg = color1, highlightbackground=color2, highlightcolor=color2, highlightthickness=5)

#frame top :

label_top = Label(frame_top, text="Veuillez ajouter des images : ", font=("Arial black", 20, 'bold'), bg=color1, fg=color2)
label_top.grid(column = 0, row = 0)
button_explore = Button(frame_top, text = "Ajouter une image", command = browseFiles, bd = 5, bg=color1, fg=color2)
button_explore.grid(column = 1, row = 0)

#frame left :

label_left = Label(frame_left, text="Suppression", font=("Arial black", 20, 'bold'), padx=5, bd = 5, bg=color1, fg=color2, highlightbackground=color2, highlightthickness=5)
label_left.grid(column = 0, row = 0, columnspan=2, padx=20, pady=(23,0))

#frame listbox:

yDefilB = Scrollbar(frame_listbox, orient='vertical')
yDefilB.grid(row=0, column=1, sticky='ns')
button_delete = Listbox(frame_listbox, height=15, yscrollcommand=yDefilB.set)
button_delete.bind("<Double-1>", DeleteImage)
yDefilB['command'] = button_delete.yview
button_delete.grid(column=0, row=0)

#frame middle

listrefimage = []

bgimage = Image.open(filedatapath + "background_canvas.png")
bgphoto = ImageTk.PhotoImage(bgimage)
canvas1 = Canvas(frame_middle, width=width, height=height, highlightbackground=color2, highlightthickness=5)
ioc1 = canvas1.create_image(0,0, anchor=NW, image=bgphoto)
listrefimage.append(ioc1)
canvas1.grid(column=0, row=0, padx=5, pady=5)

canvas2 = Canvas(frame_middle, width=width, height=height, highlightbackground=color2, highlightthickness=5)
ioc2 = canvas2.create_image(0,0, anchor=NW, image=bgphoto)
listrefimage.append(ioc2)
canvas2.grid(column=1, row=0, padx=5, pady=5)

canvas3 = Canvas(frame_middle, width=width, height=height, highlightbackground=color2, highlightthickness=5)
ioc3 = canvas3.create_image(0,0, anchor=NW, image=bgphoto)
listrefimage.append(ioc3)
canvas3.grid(column=2, row=0, padx=5, pady=5)

canvas4 = Canvas(frame_middle, width=width, height=height, highlightbackground=color2, highlightthickness=5)
ioc4 = canvas4.create_image(0,0, anchor=NW, image=bgphoto)
listrefimage.append(ioc4)
canvas4.grid(column=0, row=1, padx=5, pady=5)

canvas5 = Canvas(frame_middle, width=width, height=height, highlightbackground=color2, highlightthickness=5)
ioc5 = canvas5.create_image(0,0, anchor=NW, image=bgphoto)
listrefimage.append(ioc5)
canvas5.grid(column=1, row=1, padx=5, pady=5)

canvas6 = Canvas(frame_middle, width=width, height=height, highlightbackground=color2, highlightthickness=5)
ioc6 = canvas6.create_image(0,0, anchor=NW, image=bgphoto)
listrefimage.append(ioc6)
canvas6.grid(column=2, row=1, padx=5, pady=5)

#frame right

label_right1 = Label(frame_right, text="Style", font=("Arial black", 20, 'bold'), padx=10, bd = 5, bg=color1, fg=color2, highlightbackground=color2, highlightthickness=5)
label_right1.grid(column = 0, row = 0, padx=20, pady=(23,0))

button_explore_right = Button(frame_right, text = "Choisir un style", command = browseFilesStyle, bd = 5, bg=color1, fg=color2)
button_explore_right.grid(column = 0, row = 1, pady=(20,0))

canvas_right = Canvas(frame_right, width=widthR, height=heightR, highlightbackground=color2, highlightthickness=5)
refstyleimage = canvas_right.create_image(0,0, anchor=NW, image=bgphoto)
canvas_right.grid(column = 0, row = 2, pady=20)

label_right2 = Label(frame_right, text="Style 1 :"+style[0]+"\nStyle 2 :"+style[1]+"\nStyle 3 :"+style[2], font=("Arial black", 8, 'bold'), padx=10, bd = 5, bg=color1, fg=color2)
label_right2.grid(column=0, row=3)

button_fusion = Button(frame_right, text = "Fusionner", font=("Arial black", 20, 'bold'), bd = 5, command = Fusion, bg=color1, fg=color2, highlightbackground=color2, highlightcolor=color2, highlightthickness=5)
button_fusion.grid(column=0, row=4, padx=15, pady=10)

# frame bottom

canvas_bottom = Canvas(frame_bottom, width=940, height=350, bg="#ffb592", highlightbackground=color2, highlightthickness=5)
canvas_bottom.create_image(0,0, anchor=NW, image=bgphoto)
canvas_bottom.grid(column=0, row=0, padx=5, pady=5)

photosave = PhotoImage(file = filedatapath + "logo_save.png")
photosave = photosave.subsample(10,10)
save_button = Button(frame_bottom, image=photosave, command=SaveResult)
save_button.grid(column=0, row=1, sticky=NW)

label_bottom = Label(frame_bottom, text=resultitle, font=("Arial black", 8, 'bold'), pady=5, bg=color1, fg=color2)
label_bottom.grid(column=1, row=1)


frame_top.grid(column = 1, row = 0, pady=(30,0))
frame_left.grid(column = 0, row = 1, padx=(120,57))
frame_right.grid(column = 2, row = 1, padx=(57,0))
frame_middle.grid(column = 1, row = 1, pady=20, padx=5)
frame_bottom.grid(column = 1, row = 2)
frame_listbox.grid(column=0, row=1,  padx=15, pady=23)
frame_listbox_right.grid(column=0, row=1, pady=(23,0))

# frame_left.grid(column = 0, row = 0, sticky=W)
# frame_right.grid(column = 1, row = 0, sticky=W)
window.after(0,DeleteStyleImage)
window.after(0, RefreshWindow)

window.mainloop()



