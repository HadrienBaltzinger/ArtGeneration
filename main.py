#Import des modules nécessaires
from tkinter import *
from tkinter import filedialog 
from shutil import *
from ntpath import *
from os import *
from PIL import Image, ImageTk

#Import des fichiers du projets.
from StyleTransfert.style_transfert import apply_style
from TitleGen.gen_title_from_keywords import predict
from TitleGen.object_recognition import detect
from reconnaissance_de_style.reconnaissance_de_style import predict_result

#Variables du fichier à prédéfinir  
filedatapath = "Interface/data/"
imagefilepath = "Interface/images/"
styleimagefilepath = "Interface/style/"
resultimagefilepath = "Interface/result/"
listfilename = listdir(imagefilepath)
width = 300
height = 180
widthR = 180
heightR = 130
widthB = 940
heightB = 350
padxf1 = 50
padyf1 = 10
path_list = []
images_reference_list = []
project_name="Générateur de peintures"
color1="#ebeeb0"
color2="#92001f"


def New():
    # global style
    style = ["", "", ""]
    # global resulttitle
    resulttitle.set("")
    for i in range(0, len(listfilename)):
        listfilename.pop()
    l = listdir(imagefilepath)
    for i in l:
        remove(imagefilepath + i)

    l = listdir(styleimagefilepath)
    for i in l:
        remove(styleimagefilepath + i)

    l = listdir(resultimagefilepath)
    for i in l:
        remove(resultimagefilepath + i)
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

def AffectStyle(target):
    liststyle = predict_result(target)
    global style
    style[0] = liststyle[0][0]+" à "+str(liststyle[0][1])[:4]+"%."
    style[1] = liststyle[1][0]+" à "+str(liststyle[1][1])[:4]+"%."
    style[2] = liststyle[2][0]+" à "+str(liststyle[1][1])[:4]+"%."
    global textStyle
    textStyle.set("Style 1 :"+style[0]+"\nStyle 2 :"+style[1]+"\nStyle 3 :"+style[2])

def browseFilesStyle(): 
    DeleteStyleImage()
    filepath = filedialog.askopenfilename(initialdir = "./", 
                                          title = "Select a File", 
                                          filetypes = (("all files","*.*"), ("Text files", "*.txt*")))
    target = styleimagefilepath+"style.jpg"
    copyfile(filepath, target)
    AffectStyle(target)
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
    #Affiche l'image de résultat en bas
    listimageresult = listdir(resultimagefilepath)
    n = len(listimageresult)
    if n > 0 :
        file_path = resultimagefilepath + "/final.jpg"
        img = Image.open(file_path)
        # mywidth = widthB
        # wpercent = (mywidth/float(img.size[0]))
        # hsize = int((float(img.size[1])*float(wpercent)))        
        w, h = img.size
        scalew = w / widthB
        scaleh = h / heightB
        if scalew <= 1 and scaleh <= 1 :
            scale = max(scalew, scaleh)
        if scalew <=1 and scaleh > 1:
            scale = scaleh
        if scalew > 1 and scaleh <= 1:
            scale = scalew
        if scalew > 1 and scaleh > 1 :
            scale = max(scalew, scaleh)
        resized_img = img.resize((w / scale,h / scale), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(resized_img)
        canvas_bottom.itemconfigure(refresultimage, image=photo)
        canvas_bottom.image = photo
    elif n == 0:
        canvas_bottom.itemconfigure(refresultimage, image=bgphoto)
        canvas_bottom.image = bgphoto

def SetTitle(img_result):
    print("Generation du titre en cours ...")
    w, p = detect(img_result)
    resulttitle.set(predict(w))
    RefreshWindow

def Fusion():
    # fusion d'élements
    system('python3 PaintingFusion/painting_fusion.py') 

    # application du style
    style = "Interface/style/style.jpg"
    content = "Interface/result/fusion.jpg"
    img_result = "Interface/result/final.jpg"
    apply_style(content, style, img_result)
    print("Generation terminée ... rechargement de la page")
    RefreshWindow()

    SetTitle(img_result)

def SaveResult():

    folder = filedialog.askdirectory(initialdir = "/", 
                                          title = "Choisissez un dossier")
    listresult = listdir(resultimagefilepath)
    if len(listresult) > 0:
        filepath = resultimagefilepath + "/final.jpg"
        target = folder+"/final.jpg"
        copyfile(filepath, target)
    else:
        return True

    




window = Tk()

#bar de nav
menu_bar = Menu(window)
menu_file = Menu(menu_bar, tearoff = 0)
menu_file.add_command(label="Nouveau", command=New)
menu_file.add_command(label="Fusion", command=Fusion)
menu_file.add_command(label="Sauvegarder le résultats", command=SaveResult)
menu_file.add_command(label="Quitter", command=window.quit)

menu_bar.add_cascade(label="File", menu=menu_file)
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

style = ["", "", ""]
textStyle = StringVar()
textStyle.set("Style 1 :"+style[0]+"\nStyle 2 :"+style[1]+"\nStyle 3 :"+style[2])
label_right2 = Label(frame_right, textvariable=textStyle, font=("Arial black", 8, 'bold'), padx=10, bd = 5, bg=color1, fg=color2)
label_right2.grid(column=0, row=3)

button_fusion = Button(frame_right, text = "Fusionner", font=("Arial black", 20, 'bold'), bd = 5, command = Fusion, bg=color1, fg=color2, highlightbackground=color2, highlightcolor=color2, highlightthickness=5)
button_fusion.grid(column=0, row=4, padx=15, pady=10)

# frame bottom

canvas_bottom = Canvas(frame_bottom, width=widthB, height=heightB, bg="#ffb592", highlightbackground=color2, highlightthickness=5)
refresultimage = canvas_bottom.create_image(0,0, anchor=NW, image=bgphoto)
canvas_bottom.grid(column=0, row=0, columnspan= 2, padx=5, pady=5)

photosave = PhotoImage(file = filedatapath + "logo_save.png")
photosave = photosave.subsample(10,10)
save_button = Button(frame_bottom, image=photosave, command=SaveResult)
save_button.grid(column=0, row=1, sticky=NW)


resulttitle = StringVar(window)
resulttitle.set("Titre de l'image")
label_bottom = Label(frame_bottom, textvariable=resulttitle, font=("Arial black", 8, 'bold'), pady=5, bg=color1, fg=color2)
label_bottom.grid(column=1, row=1, padx=15, sticky=NW)


frame_top.grid(column = 1, row = 0, pady=(30,0))
frame_left.grid(column = 0, row = 1, padx=(120,57))
frame_right.grid(column = 2, row = 1, padx=(57,0))
frame_middle.grid(column = 1, row = 1, pady=20, padx=5)
frame_bottom.grid(column = 1, row = 2)
frame_listbox.grid(column=0, row=1,  padx=15, pady=23)
frame_listbox_right.grid(column=0, row=1, pady=(23,0))

# frame_left.grid(column = 0, row = 0, sticky=W)
# frame_right.grid(column = 1, row = 0, sticky=W)

window.after(0, AffectStyle(styleimagefilepath + listdir(styleimagefilepath)[0]))
img_result_tmp = "Interface/result/final.jpg"
window.after(0, SetTitle(img_result_tmp))

window.mainloop()



