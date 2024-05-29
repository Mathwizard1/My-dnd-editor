# Import Modules
import os
import pickle as pk
import random as rd
import tkinter as tk
import tkinter.scrolledtext as st
import tkinter.filedialog as tk_fd
import tkinter.colorchooser as tk_color
from PIL import Image, ImageTk

mode = ""

img_fol_path = "data\\img"
set_dir_path = "data\\terrains.dat"
data_dir_path = "data\\monster.dat"
characs_dir_path = "data\\characters.dat"
obj_dir_path = "data\\objects.dat"
maps_dir_path = "data\\maps.txt"

Dnd_data = {}
loop_window = True
Nature = ["friend", "enemy", "neutral"]

map_grid = {}
Lines_order = []
Lines_backup = []
map_object_order = {}
block_img = {}
point_exist = 0

scr_width, scr_height, ratio = 0, 0, 0

# classes of objects, characters, monsters
class dnd_object():
    def __init__(self, obj_name, obj_type = "objects", obj_size = 1):
        self.object_type = obj_type
        self.obj_name = obj_name
        self.obj_size = obj_size 

    def add_image(self, img_path):
        self.img = img_path

    def save_object(self):
        with open(r"data/"+self.object_type+".dat", "ab+") as fp:
            db = {}
            db[self.obj_name] = vars(self)
            pk.dump(db, fp)
            fp.close()

class dnd_charac(dnd_object):
    def __init__(self, charac_name, charac_hp, charac_AC, shape_change = 0, nature = "friend"):
        super().__init__(charac_name, "characters", 1)
        self.max_hp = charac_hp
        self.ac = charac_AC
        self.shape_change = shape_change
        self.nature = nature

class dnd_monster(dnd_object):
    def __init__(self, monster_name, monster_hp, monster_AC, monster_size = 1, nature = "enemy"):
        super().__init__(monster_name, "monster", monster_size)
        self.hp = monster_hp
        self.ac = monster_AC
        self.nature = nature

# helper functions
def folder_exists(folpath):
    fol = os.path.isdir(folpath)
    if(not fol):
        os.mkdir(folpath)  

def file_exists(fpath, create = False):
    file_pres = os.path.isfile(fpath)
    if(not file_pres and create):
        fp = open(fpath, "wb")
        fp.close
    return file_pres

def setup_editor():
    folder_exists("data")
    folder_exists(img_fol_path)
    file_exists(set_dir_path, True)
    file_exists(data_dir_path, True)
    file_exists(characs_dir_path, True)
    file_exists(maps_dir_path, True)
    file_exists(obj_dir_path, True)

def on_enter(event, obj, cursor = "target"):
    obj.config(cursor = cursor, highlightthickness=2, highlightbackground="white")
def on_leave(event, obj, cursor = "spider"):
    obj.config(cursor = cursor, highlightthickness=1, highlightbackground="black")

def looped_window(curr_window):
    global loop_window 
    loop_window = True
    curr_window.destroy()

def unpickle_object_class(obj_type, obj_name = "All"):
    db = {}
    if(obj_type != "terrains" and obj_name != "All"):
        with open(r"data/"+obj_type+".dat", "rb") as fp:
            try:
                while(1):
                    db.update(pk.load(fp))
                    if(obj_name in list(db.keys())):
                        db = db[obj_name]
                        break
            except EOFError:
                pass
            fp.close()
    elif(obj_type == "terrains"):
        with open(r"data/"+obj_type+".dat", "rb") as fp:
            try:
                while(1):
                    db.update(pk.load(fp))
            except EOFError:
                pass
            fp.close()
    return db

def fill_Dnd_data(Dnd_data):
    Dnd_data = {
        "objects": [],
        "characters": [],
        "monster": [],
        "terrains": []
    }

    dkeys = list(Dnd_data.keys())
    for val in dkeys:
        with open(r"data/"+val+".dat", "rb") as fp:
            try:
                while(True):
                    db = pk.load(fp)
                    Dnd_data[val].extend(list(db.keys()))
            except EOFError:
                pass
            fp.close()

    return Dnd_data


def find_snap_grid(x,y, grid_size, w, h):
    x0, y0 = int(x / grid_size) , int(y / grid_size) 
    w, h = int(w / grid_size) , int(h / grid_size) 

    if(x0 >= w):
        x0 = w
    elif(x0 <= 0):
        x0 = 0
    else:
        x0 = x0 if (x / grid_size - x0 <= 1 / 2) else x0 + 1 

    if(y0 >= h):
        y0 = h
    elif(y0 <= 0):
        y0 = 0
    else:
        y0 = y0 if (y / grid_size - y0 <= 1 / 2) else y0 + 1 

    return (x0 * grid_size, y0 * grid_size)

def lastpoint2cursor_line(canv_obj, lastpoint, mousecursor, r, last_color = "black"):
    canv_obj.delete('line2cursor') # Will update cursor line
    canv_obj.create_line(*lastpoint, *mousecursor, tag = 'line2cursor', fill= last_color, width = 2)
    canv_obj.create_oval(mousecursor[0] - r, mousecursor[1] - r, mousecursor[0] + r, mousecursor[1] + r, fill= last_color, tag = 'line2cursor')

def find_min_distance(posxy, pos_s, unit_size):
    min = unit_size
    pos_f = posxy
    for pos1 in pos_s:
        dis = ((posxy[0] - pos1[0]) ** 2 + (posxy[1] - pos1[1]) ** 2) ** 0.5
        if(dis < min):
            min = dis
            pos_f = pos1
    return pos_f

def lastcharac2cursor(pxy, x, y, r, canv_obj, cha_rect):
    canv_obj.delete("hover_image")

    s = int(cha_rect["obj_size"])
    offsxy = (s % 2) * r * 2
    charac_base_color = "red" if(cha_rect["object_type"] == "monster") else ("green" if (cha_rect["object_type"] == "characters" and cha_rect["nature"] == "friend") else "brown")
    charac_txt = cha_rect["obj_name"] if(len(cha_rect["obj_name"]) <= 4) else cha_rect["obj_name"][:2] + cha_rect["obj_name"][-2:]

    canv_obj.create_rectangle(x + offsxy - int(1.7 * r) * s, y + offsxy - int(1.7 * r) * s, x + offsxy + int(1.7 * r) * s, y + offsxy + int(1.7 * r) * s, fill = charac_base_color, tag = "hover_image")
    
    if(pxy in list(block_img.keys())): 
        canv_obj.create_image(x + offsxy, y + offsxy, image = block_img[pxy], anchor = "center", tag = "hover_image")
    else:
        canv_obj.create_text(x + offsxy, y + offsxy, text = charac_txt, font = "Pursia", tag = "hover_image")

# check if the set of lines form a polygon or
def check_if_polygon(mp, canv_obj):
    if(len(Lines_order) > 2 and canv_obj.focus_get() and (type(mp) != int) and not mp.get()):
        canv_obj.delete("area_polygon")
        area_fields = []

        i = 0
        while(i < len(Lines_order)):
            lines_area = []
            lines_area.extend(Lines_order[i][:2])
            for j in range(i + 1, len(Lines_order)):
                if(Lines_order[j][:2] == Lines_order[j - 1][2:] and map_grid[tuple(Lines_order[j][:2])] == map_grid[tuple(Lines_order[j - 1][:2])]):
                    lines_area.extend(Lines_order[j][:2])
                else:
                    lines_area.extend(Lines_order[j - 1][-2:])
                    i = j - 1
                    break
            if(len(lines_area) > 5 and lines_area[:2] == lines_area[-2:]):
                area_fields.append(lines_area)
            i = i + 1    
        for lines_area in area_fields:
            canv_obj.create_polygon(*lines_area, fill = map_grid[tuple(lines_area[:2])], stipple = "gray50", tag = "area_polygon")

# windows
def Dnd_editor():
    # create root window
    Dnd_window = tk.Tk()

    global scr_width, scr_height, ratio
    scr_width = int(3/40 * Dnd_window.winfo_screenwidth()) * 10
    scr_height = int(3/40 * Dnd_window.winfo_screenheight()) * 10
    ratio = scr_width/scr_height

    # root window title and dimension
    Dnd_window.title("DND-editor v2.0")

    # Set geometry (widthxheight)
    Dnd_window.geometry("%dx%d" % (scr_width, scr_height))

    # Not resize-able
    Dnd_window.resizable(0,0)

    # set icon
    if(file_exists("icon.png")):
        iphoto = tk.PhotoImage(file="icon.png")
        Dnd_window.iconphoto(True, iphoto)
    else:
        bphoto = tk.PhotoImage(height = 16, width = 16)
        bphoto.blank()
        Dnd_window.iconphoto(True, bphoto)

    # all widgets will be here
    # Create Frame 
    bg_canvas = tk.Canvas(Dnd_window)
    bg_canvas.pack(fill="both", expand= True)
    bg_canvas.config(cursor = "spider")

    # back ground image
    if(file_exists("bg.png")):
        img = Image.open("bg.png")
        r_size = 2/3
        resized_img = img.resize((int(img.size[0] * ratio * r_size), int(img.size[1] * r_size)))
        bg_image = ImageTk.PhotoImage(resized_img)
        bg_canvas.create_image(int(scr_width/2),int(scr_height/2.05), image = bg_image, anchor = "center")
    else:
        bg_canvas.config(bg = "#0044FF")

    # Welcome text
    bg_canvas.create_text(int(scr_width/2),int(scr_height/7), text = "Welcome to Dnd editor", font = ("Old English Text MT", int(scr_height / 12), "underline"), anchor = "center")

    btn_padx = int(scr_width / 25)
    btn_height, btn_width = int(scr_height/ 3), int(scr_width / 4)

    # button functions
    def btn_f(event, msg):
        global mode
        mode = msg
        Dnd_window.destroy()

    txt_color = "red"

    # add buttons
    btn1 = tk.Canvas(bg_canvas, width = btn_width, height = btn_height, highlightthickness=1, highlightbackground="black")
    btn1.pack(padx = btn_padx, side="left", anchor= "e") 
    btn1.bind("<Button-1>", lambda eff: btn_f(eff, "Dm_setup_mode"))
    # back ground image
    if(file_exists("Dm_setup_mode.png")):
        img = Image.open("Dm_setup_mode.png")
        r_size = 1/3
        resized_img = img.resize((int(img.size[0] * r_size), int(img.size[1] * r_size)))
        bg_img1 = ImageTk.PhotoImage(resized_img)
        btn1.create_image(int(scr_width/8),int(scr_height/7), image = bg_img1, anchor = "center")
    else:
        btn1.config(bg = "#11CC22")
    btn1.create_text(int(scr_width/8),int(scr_height/7), text = "Setup mode", font = ("Algerian", int(scr_height/ 17)), anchor = "center", fill=txt_color)
    '''
    btn2 = tk.Canvas(bg_canvas, width = btn_width, height = btn_height, highlightthickness=1, highlightbackground="black")
    btn2.pack(padx = btn_padx, side="left", anchor= "center") 
    btn2.bind("<Button-1>", lambda eff: btn_f(eff, "Dm_mode"))

    # back ground image
    if(file_exists("Dm_mode.png")):
        img = Image.open("Dm_mode.png")
        r_size = 1/3
        resized_img = img.resize((int(img.size[0] * r_size), int(img.size[1] * r_size)))
        bg_img2 = ImageTk.PhotoImage(resized_img)
        btn2.create_image(int(scr_width/8),int(scr_height/7), image = bg_img2, anchor = "center")
    else:
        btn2.config(bg = "#11CC22")
    btn2.create_text(int(scr_width/8),int(scr_height/7), text = "Dm mode", font = ("Algerian", int(scr_height/ 17)), anchor = "center", fill=txt_color)
    '''

    btn3 = tk.Canvas(bg_canvas, width = btn_width, height = btn_height, highlightthickness=1, highlightbackground="black")
    btn3.pack(padx = btn_padx, side="left", anchor= "w") 
    btn3.bind("<Button-1>", lambda eff: btn_f(eff, "Map_mode"))

    # back ground image
    if(file_exists("Map_mode.png")):
        img = Image.open("Map_mode.png")
        r_size = 1/3
        resized_img = img.resize((int(img.size[0] * r_size), int(img.size[1] * r_size)))
        bg_img3 = ImageTk.PhotoImage(resized_img)
        btn3.create_image(int(scr_width/8),int(scr_height/7), image = bg_img3, anchor = "center")
    else:
        btn3.config(bg = "#11CC22")
    btn3.create_text(int(scr_width/8),int(scr_height/7), text = "Map mode", font = ("Algerian", int(scr_height/ 17)), anchor = "center", fill=txt_color)

    btn1.bind("<Enter>", lambda eff: on_enter(eff, btn1))
    btn1.bind("<Leave>", lambda eff: on_leave(eff, btn1))
    #btn2.bind("<Enter>", lambda eff: on_enter(eff, btn2))
    #btn2.bind("<Leave>", lambda eff: on_leave(eff, btn2))
    btn3.bind("<Enter>", lambda eff: on_enter(eff, btn3))
    btn3.bind("<Leave>", lambda eff: on_leave(eff, btn3))

    # Execute Tkinter
    Dnd_window.mainloop()

def Dm_setup_mode():
# create root window
    setup_window = tk.Tk()

    # root window title and dimension
    setup_window.title("Setup v2.0")

    #global values
    global scr_width, scr_height, ratio
    offs = int(scr_width / 8)

    # Set geometry (widthxheight)
    setup_window.geometry("%dx%d" % (scr_width + offs, scr_height))

    # Not resize-able
    setup_window.resizable(0,0)

    # set icon
    if(file_exists("icon.png")):
        iphoto = tk.PhotoImage(file="icon.png")
        setup_window.iconphoto(True, iphoto)
    else:
        bphoto = tk.PhotoImage(height = 16, width = 16)
        bphoto.blank()
        setup_window.iconphoto(True, bphoto)

    # all toplevels here
    def obj_change(m, objtype, txt_b):
        # top level size
        r = 2/3 if (m > 0) else 1/3
        top_level_size = (int(scr_width * r), int(scr_height * r))

        # toplevel
        top = tk.Toplevel()
        top.geometry("%dx%d" % top_level_size)

        # text settings
        txt = f"Add {objtype}" if(m > 0) else f"Remove {objtype}"
        btn_txt = "Add" if(m > 0) else "Remove"

        # title and no resize
        top.title(txt)
        top.resizable(0,0)

        #font
        font = ("Harlow Solid Italic", int(scr_height/ 30))
        norm_font = ("Arial", int(scr_height/ 50))

        # common variables
        obj_opt = tk.StringVar(top, value = "None")
        shape_check = tk.IntVar(top, value = 0)
        nature_val = tk.StringVar(top, value = "neutral")
        image_field = tk.StringVar(top, value = "")
        color_field = tk.StringVar(top, value = "")
        name_field, hp_field, size_field, AC_field = None, None, None, None
        terrain_field = None

        def locate_image(m):
            if(m == 0):
                val = tk_fd.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
                cur_folder = os.path.basename(os.getcwd())
                if(val != None and f"{cur_folder}/" in val):
                    image_field.set(str(val.split(f"{cur_folder}/")[1]))
            else:
                lb = tk.Label(top, text=str(image_field.get()), font = norm_font)
                lb.pack(anchor="center")
                lb.after(5000, lambda: lb.destroy())

        def choose_color(m):
            if(m == 0):
                # variable to store hexadecimal code of color
                val = tk_color.askcolor(title ="Choose color")
                if(val != None):
                    color_field.set(str(val[1]))
            else:
                tk.Label(top, text= "COLORED TEXT", font = (*font,"italic"), fg=color_field.get()).pack(anchor="center") 

        # common parameters
        spin_box_param = {"width": int(scr_width / 100), "state" : "readonly", "relief":"sunken", "repeatdelay": 500, "repeatinterval":100,"font" : norm_font}

        # add object
        if(m > 0):
            l2 = tk.Label(top, text = f"Enter the {objtype} info", font = font)
            l2.pack(side="top", pady=(int(scr_height/40), 0))
            if(objtype == "characters" or objtype == "monster" or objtype == "objects"):
                tk.Label(top, text = "Name", font = norm_font).pack()
                name_field = tk.Entry(top)
                name_field.pack()

                tk.Label(top, text = "max_hp", font = norm_font).pack()
                if(objtype == "characters"):
                    hp_field = tk.Spinbox(top, from_ = 1, to = 100, **spin_box_param)
                elif(objtype == "monster"):
                    hp_field = tk.Entry(top)
                    hp_field.insert(0, "1d1+1")
                else:
                    hp_field = tk.Entry(top)
                    hp_field.insert(0, "-1")
                    hp_field.config(state="disabled")
                hp_field.pack()

                tk.Label(top, text = "size", font = norm_font).pack()
                size_field = tk.Spinbox(top, from_ = 1, to = 5, **spin_box_param)
                size_field.pack()
                if(objtype == "characters"):
                    size_field.config(state="disabled")

                tk.Label(top, text = "base AC", font = norm_font).pack()
                AC_field = tk.Spinbox(top, from_ = 1, to = 100, **spin_box_param)
                AC_field.pack()
                if(objtype == "objects"):
                    AC_field.config(state="disabled")

                shape_chng_field = tk.Checkbutton(top, text="shape change", variable= shape_check, onvalue=1, offvalue=0, font = norm_font)
                shape_chng_field.pack()
                if(objtype != "characters"):
                    shape_chng_field.config(state="disabled")                

                tk.Label(top, text = "Nature", font = norm_font).pack()
                if(objtype == "monster"):
                    nature_val.set("enemy")
                nature_field = tk.OptionMenu(top, nature_val, *Nature)
                nature_field.pack()
                if(objtype == "objects" or objtype == "monster"):
                    nature_field.config(state="disabled")

                tk.Button(top, text = "Add Image", font = norm_font, command= lambda: locate_image(0)).pack(side = "left")
                image_field.trace_add("write", lambda *args: locate_image(1))

            else:
                if(len(Dnd_data[objtype]) < 8):
                    tk.Label(top, text = "Terrain", font = norm_font).pack()
                    terrain_field = tk.Entry(top)
                    terrain_field.pack()

                    tk.Button(top, text = "Choose color", font = norm_font, command= lambda: choose_color(0)).pack()
                    color_field.trace_add("write", lambda *args: choose_color(1))                    
                else:
                    tk.Label(top, text = "Maximum 8 terrains possible", font = font).pack(pady= int(scr_height/10) , anchor="center")
        # remove object
        else:
            l2 = tk.Label(top, text = f"Choose the {objtype}", font = font)
            l2.pack(side="top", pady=(int(scr_height/40), 0))
            options = []

            if(len(Dnd_data[objtype]) == 0):
                options.append("None")
            else:
                options = list(Dnd_data[objtype])

            display_menu = tk.OptionMenu(top, obj_opt, *options)
            display_menu.config(font=font) 
            display_menu.pack(anchor="center") 

        # file update function
        def changes(m, btn):
            flag = False
            global Dnd_data

            if(m > 0):
                if((objtype == "characters" or objtype == "monster" or objtype == "objects") and len(name_field.get()) != 0):
                    obj_class = None
                    if(objtype =="characters"):
                        obj_class = dnd_charac(name_field.get(), hp_field.get(), AC_field.get(), shape_check.get(), nature_val.get())
                    elif(objtype =="monster" and len(hp_field.get()) != 0 and not (hp_field.get().isalpha())):
                        hp_check = hp_field.get().split("d")
                        if(hp_check[0].isnumeric()):
                            if(len(hp_check) == 1):
                                obj_class = dnd_monster(name_field.get(), hp_check, AC_field.get(), size_field.get())
                            elif(len(hp_check) == 2):
                                hp_check = hp_check[1].split("+")
                                if((len(hp_check) == 1 and hp_check[0].isnumeric()) or (len(hp_check) == 2 and hp_check[0].isnumeric() and hp_check[1].isnumeric())):
                                    obj_class = dnd_monster(name_field.get(), hp_field.get(), AC_field.get(), size_field.get())
                                else:
                                    flag = 1
                            else:
                                flag = 1
                        else:
                            flag = 1

                    elif(objtype == "objects"):
                        obj_class = dnd_object(name_field.get(), obj_size= size_field.get())                
                    else:
                        flag = 1

                    if(len(image_field.get()) != 0 and not flag):
                        obj_class.add_image(image_field.get())

                    if(not flag):
                        obj_class.save_object()

                elif(objtype == "terrains" and len(Dnd_data[objtype]) < 8 and len(terrain_field.get()) != 0 and len(color_field.get()) != 0):
                    with open(r"data/"+objtype+".dat", "ab+") as fp:
                        db = {}
                        db[terrain_field.get()] = color_field.get()
                        pk.dump(db, fp)
                        fp.close()
                else:
                    flag = True
            elif(obj_opt.get() != "None"):
                db = {}
                with open(r"data/"+objtype+".dat", "rb") as fp:
                    try:
                        while(1):
                            db.update(pk.load(fp))
                    except EOFError:
                        pass
                    fp.close()

                if(obj_opt.get() in list(db.keys())):
                    db.pop(obj_opt.get(), "nothing")
                    with open(r"data/"+objtype+".dat", "wb") as fp:
                        pk.dump(db, fp)
                        fp.close()
                else:
                    flag = True
            else:
                flag = True

            if(not flag):
                # update Dnd data
                Dnd_data = fill_Dnd_data(Dnd_data)

                # update the text box
                txt_b.config(state = "normal")
                txt_b.delete(1.0, "end")
                for c in Dnd_data[objtype]:
                    txt_b.insert("insert", c+"\n", ("centered",))
                    txt_b.tag_configure("centered", justify="center")
                txt_b.config(state="disabled")

                top.destroy()
            else:
                btn.config(fg = "red")

        # submit button
        submit_btn = tk.Button(top, text = btn_txt, font = font, command= lambda: changes(m, submit_btn))
        submit_btn.pack(side = "bottom")
        top.mainloop()

    # all widgets will be here
    # Creating Menubar 
    menubar = tk.Menu(setup_window)

    # Adding setting Menu and commands 
    set_menu = tk.Menu(menubar, tearoff = 0) 
    set_menu.add_command(label ='help', command = None) 
    set_menu.add_separator() 
    set_menu.add_command(label ='Go back', command = lambda: looped_window(setup_window))
    menubar.add_cascade(label ='Settings', menu = set_menu) 

    # display Menu 
    setup_window.config(menu = menubar)

    # Create Canvas
    bg_canvas = tk.Canvas(setup_window, bg = "black")
    bg_canvas.pack(side = "left",fill="both", expand= True)
    bg_canvas.config(cursor = "circle")

    if(file_exists("Dm_setup_mode.png")):
        img = Image.open("Dm_setup_mode.png")
        r_size = 1/2
        resized_img = img.resize((int(img.size[0] * ratio * r_size), int(img.size[1] * r_size)))
        bg_image = ImageTk.PhotoImage(resized_img)
        bg_canvas.create_image(int(scr_width/2.25),int(scr_height/3.45), image = bg_image, anchor = "center")
    else:
        bg_canvas.config(bg = "black")

    # Welcome text
    bg_canvas.create_text(int(scr_width/2.5),int(scr_height/10), text = "Dungeon master's setup", font = ("Old English Text MT", int(scr_height / 12), "underline"), anchor = "center", fill="brown")

    # all buttons
    btn_param = {"font": ("Ariel"), "bg" : "green"}
    btn_grid_param = {"padx" : int(scr_width/ 50), "pady" : (int(scr_height/ 5), 0)}

    add_character_btn = tk.Button(bg_canvas, text="Add character", **btn_param, command= lambda: obj_change(1, "characters", display_character))
    add_character_btn.grid(row=0, column=0, **btn_grid_param)

    add_object_btn = tk.Button(bg_canvas, text="Add object", **btn_param, command= lambda: obj_change(1, "objects", display_obj ))
    add_object_btn.grid(row = 0, column=1, **btn_grid_param)

    add_monster_btn = tk.Button(bg_canvas, text="Add monster", **btn_param, command= lambda: obj_change(1, "monster", display_monster))
    add_monster_btn.grid(row= 0, column= 2, **btn_grid_param)

    add_terrain_btn = tk.Button(bg_canvas, text="Add terrain", **btn_param, command= lambda: obj_change(1, "terrains", display_terrain))
    add_terrain_btn.grid(row= 0, column= 3, **btn_grid_param)

    btn_param["bg"] = "red"
    btn_grid_param["pady"] = (int(scr_height/ 40),0)

    remove_character_btn = tk.Button(bg_canvas, text="remove character", **btn_param, command= lambda: obj_change(-1, "characters", display_character))
    remove_character_btn.grid(row= 1, column= 0, **btn_grid_param)

    remove_object_btn = tk.Button(bg_canvas, text="remove object", **btn_param, command= lambda: obj_change(-1, "objects", display_obj ))
    remove_object_btn.grid(row= 1, column= 1, **btn_grid_param)

    remove_monster_btn = tk.Button(bg_canvas, text="remove monster", **btn_param, command= lambda: obj_change(-1, "monster", display_monster))
    remove_monster_btn.grid(row= 1, column= 2, **btn_grid_param)

    remove_terrain_btn = tk.Button(bg_canvas, text="remove terrain", **btn_param, command= lambda: obj_change(-1, "terrains", display_terrain))
    remove_terrain_btn.grid(row= 1, column= 3, **btn_grid_param)

    # display texts
    scroll_text_param = {"wrap" : tk.WORD, "width": 20, "height": int(scr_height/ 50), "foreground" : "white" ,"bg" : "black", "font": ("Harlow Solid Italic", int(scr_height / 40))}
    scroll_grid_param = {"row" : 2, "padx": (int(scr_width / 200),0), "pady": (int(scr_height / 7), 0)}

    display_character = st.ScrolledText(bg_canvas, **scroll_text_param)
    display_character.grid(column = 0, **scroll_grid_param)
    for c in Dnd_data["characters"]:
        display_character.insert("insert", c+"\n", ("centered",))
    display_character.tag_configure("centered", justify="center")
    display_character.config(state="disabled")

    display_obj = st.ScrolledText(bg_canvas, **scroll_text_param)
    display_obj.grid(column = 1, **scroll_grid_param)
    for o in Dnd_data["objects"]:
        display_obj.insert("insert", o+"\n", ("centered",))
    display_obj.tag_configure("centered", justify="center")
    display_obj.config(state="disabled")

    display_monster = st.ScrolledText(bg_canvas, **scroll_text_param)
    display_monster.grid(column = 2, **scroll_grid_param)
    for m in Dnd_data["monster"]:
        display_monster.insert("insert", m+"\n", ("centered",))
    display_monster.tag_configure("centered", justify="center")
    display_monster.config(state="disabled")

    display_terrain = st.ScrolledText(bg_canvas, **scroll_text_param)
    display_terrain.grid(column = 3, **scroll_grid_param)
    for t in Dnd_data["terrains"]:
        display_terrain.insert("insert", t+"\n", ("centered",))
    display_terrain.tag_configure("centered", justify="center")
    display_terrain.config(state="disabled")

    # display stats
    txt_params = {"font": ("Arial", int(scr_height / 30))}
    txt_grid_params = {"column" : 6, "padx": int(scr_height / 20)}

    object_label = tk.Label(bg_canvas, text="Object:", **txt_params)
    object_label.grid(row= 0, **txt_grid_params)

    # Create the list of options 
    options_list = list(Dnd_data.keys()) 
    options_list2 = ["None"]

    # update the option menu 1
    def callback(call, num, arr = 0, varr = 0):
        if(num == 1 and call != "Select an Object"):
            # empty the menu
            omenu = arr["menu"]
            omenu.delete(0, "end")

            # check new stuff
            if(len(Dnd_data[call]) == 0):
                omenu.add_command(label = "None", command=tk._setit(varr, "None"))
                varr.set("None")
            else:
                # add stuff
                for option in Dnd_data[call]:
                    omenu.add_command(label = option, command=tk._setit(varr, option))

    # info display
    def info_display(val_name, val_obj, canv_obj):
        global t_image
        canv_obj.config(bg = "black")
        canv_obj.delete("all")
        if((val_name != "None" or val_name != "Select its name") and val_obj != "Select an Object"):
            if(val_name in Dnd_data[val_obj]):
                db = {}
                with open(r"Data/"+val_obj+".dat", "rb") as fp:
                    while(1):
                        db = pk.load(fp)
                        if(val_name in list(db.keys())):
                            db = db[val_name]
                            break
                    fp.close()
                # special terrains
                if(val_obj == "terrains"):
                    canv_obj.config(bg = db)
                    return

                # data adjustments
                oimg = "" if ("img" not in list(db.keys())) else db["img"]
                db.pop("object_type", "nothing")
                db.pop("obj_name", "nothing")

                if(oimg != ""):
                    db.pop("img", "nothing")
                if(val_obj == "monster"):
                    db.pop("nature", "nothing")

                # image
                if(oimg != "" and file_exists(oimg)):
                    temp_img = Image.open(oimg)
                    oresized_img = temp_img.resize((int(canv_obj.winfo_width()), int(canv_obj.winfo_height())))
                    t_image = ImageTk.PhotoImage(oresized_img)
                    canv_obj.create_image(0, 0, image = t_image, anchor = "nw")
                else:
                    canv_obj.config(bg = "black") 

                # rest print out data
                txcolor = "red" if(val_obj == "monster") else ("green" if (val_obj == "characters" and db["nature"] == "friend") else "yellow")
                i = 0
                for k in db:
                    canv_obj.create_text(int(scr_width / 10), int(scr_height/ 35 * i + scr_height/3), text = str(f"{k}:{db[k]}"), font = ("Algerian", int(scr_height / 40)), fill = txcolor)
                    i += 1

    # Variable to keep track of the option 
    # selected in OptionMenu 
    obj_inside = tk.StringVar(setup_window) 
    obj_name = tk.StringVar(setup_window)

    # Set the default value of the variable 
    obj_inside.set("Select an Object") 
    obj_name.set("Select its name")     

    # Create the optionmenu widget and passing  
    # the options_list and obj_inside to it. 
    question1_menu = tk.OptionMenu(bg_canvas, obj_inside, *options_list, command= lambda sel: callback(sel, 1, question2_menu, obj_name)) 
    question1_menu.grid(row= 0, column= 9, sticky="w") 

    name_label = tk.Label(bg_canvas, text="Name:", **txt_params)
    name_label.grid(row= 1, **txt_grid_params)

    question2_menu = tk.OptionMenu(bg_canvas, obj_name, *options_list2) 
    question2_menu.grid(row= 1, column= 9, sticky="w") 

    info_canvas = tk.Canvas(bg_canvas, width=int(scr_width / 5.5), bg = "black", height=int(scr_height / 2), bd=0, highlightthickness=0, relief='ridge')
    info_canvas.grid(row = 2, column= 9, sticky="w")

    obj_name.trace_add('write', lambda *args: info_display(obj_name.get(), obj_inside.get(), info_canvas))

    # Execute Tkinter
    setup_window.mainloop()

def Dm_mode():
# create root window
    Dm_window = tk.Tk()

    # root window title and dimension
    Dm_window.title("Dm v2.0")

    global scr_width, scr_height, ratio

    # Set geometry (widthxheight)
    Dm_window.geometry("%dx%d" % (scr_width, scr_height))

    # Not resize-able
    Dm_window.resizable(0,0)

    # set icon
    if(file_exists("icon.png")):
        iphoto = tk.PhotoImage(file="icon.png")
        Dm_window.iconphoto(True, iphoto)
    else:
        bphoto = tk.PhotoImage(height = 16, width = 16)
        bphoto.blank()
        Dm_window.iconphoto(True, bphoto)

    # settings
    charac_order = {}

    # all toplevels here


    # all widgets will be here
    # Creating Menubar 
    menubar = tk.Menu(Dm_window)

    # Adding setting Menu and commands 
    set_menu = tk.Menu(menubar, tearoff = 0) 
    set_menu.add_command(label ='Load', command = None) 
    set_menu.add_command(label ='help', command = None) 
    set_menu.add_separator()
    set_menu.add_command(label ='clear', command = None) 
    set_menu.add_command(label ='Go back', command = lambda: looped_window(Dm_window))
    menubar.add_cascade(label ='Settings', menu = set_menu) 

    # display Menu 
    Dm_window.config(menu = menubar)

    # create buttons frame
    btn_frame = tk.Frame(Dm_window, bg = "green")
    btn_frame.pack(side = "top", fill="x")
    frame_btns = []



    # Execute Tkinter
    Dm_window.mainloop()

def Map_mode():
    # create root window
    Map_window = tk.Tk()

    # root window title and dimension
    Map_window.title("Map v2.0")

    #global
    global scr_width, scr_height, ratio
    offy = int(scr_height / 11.25)

    # unit size if 31 for 1150x640 screen and lower
    unit_size = int((scr_width ** 2 + scr_height ** 2) ** 0.5 / 35)

    # Set geometry (widthxheight)
    Map_window.geometry("%dx%d" % (scr_width, scr_height + offy))

    # Not resize-able
    Map_window.resizable(0,0)

    # set icon
    if(file_exists("icon.png")):
        iphoto = tk.PhotoImage(file="icon.png")
        Map_window.iconphoto(True, iphoto)
    else:
        bphoto = tk.PhotoImage(height = 16, width = 16)
        bphoto.blank()
        Map_window.iconphoto(True, bphoto)

    # Map variables
    Dnd_terrains = unpickle_object_class("terrains")
    Dnd_data.pop("terrains", "nothing")

    color_var = tk.StringVar(Map_window, value="", name="color_var")
    dim_var = tk.IntVar(Map_window, value = 10, name ="dim_var")
    cursor_holding_point = tk.BooleanVar(Map_window, value= 0, name="cursor_state")
    cursor_holding_character = tk.BooleanVar(Map_window, value= 0, name="cursor_character")
    world_color = tk.StringVar(Map_window, value = "yellow")

    temp_move_obj = tk.StringVar(Map_window, value = "")

    # fonts
    norm_font = ("Ariel", int(scr_height/ 50), "bold")

    # all toplevels here
    def save_load(mouse_prop_point, mouse_prop_charac, state):
        if(not (mouse_prop_point.get() or mouse_prop_charac.get())):
            # top level size
            r = 1/3.5
            top_level_size = (int(scr_width * r), int(scr_height * r * 0.55))
        
            top = tk.Toplevel()
            top.geometry("%dx%d" % top_level_size)
            txt = f"Save map" if(state) else "Load map"

            top.title(txt)
            l2 = tk.Label(top, text = txt, font = norm_font)
            l2.pack()
            save_name = tk.Label(top, text = "name of save: ")
            save_name.pack(side="left")

            option_list = ["None"]
            obj_selection = tk.StringVar(top, value = "None")
            all_lines = []

            with open(maps_dir_path, "r") as fp:
                all_lines = fp.readlines()
                if(len(all_lines) > 0):
                    option_list = []
                    for line in all_lines:
                        if("**~" in line):
                            option_list.append(line)
                fp.close()

            if(state):
                save_entry = tk.Entry(top)
                save_entry.pack(side="left")
            else:
                reduction_menu = tk.OptionMenu(top, obj_selection, *option_list, command= lambda sel: sav_load_chg(top, sel)) 
                reduction_menu.pack(side="left") 

            def sav_load_chg(top, sel = "None"):
                global map_grid, Lines_order, map_object_order, block_img, Lines_backup
                
                if(state and len(save_entry.get()) != 0):
                    with open(maps_dir_path, "a") as fp:
                        fp.writelines([f"**~{save_entry.get()}\n", str(map_grid)+"\n", str(Lines_order)+"\n", str(map_object_order)+"\n"])
                        fp.close()
                elif(not state and sel != "None"):
                    # empty all
                    map_grid, block_img, map_object_order = {}, {}, {}
                    Lines_order, Lines_backup = [], []

                    # load data
                    line_index = all_lines.index(sel)
                    map_grid = eval(all_lines[line_index + 1].rstrip("\n"))
                    Lines_order = eval(all_lines[line_index + 2].rstrip("\n"))
                    map_object_order = eval(all_lines[line_index + 3].rstrip("\n"))

                top.destroy()

            # submit button
            submit_btn = tk.Button(top, text = "submit", font = norm_font, command= lambda: sav_load_chg(top))
            submit_btn.pack(side = "bottom")
            top.mainloop()

    # sub function for top level
    def add_it(event, obj_type, coords, canv_obj, top_window):
        if(event != "None" and event in Dnd_data[obj_type]):
            unpickled_data = unpickle_object_class(obj_type, event)
            if(unpickled_data != {}):
                name_count =  0
                for v in list(map_object_order.values()):
                    if(unpickled_data["obj_name"] in v["obj_name"]):
                        name_count += 1

                unpickled_data["obj_name"] = unpickled_data["obj_name"] + str(name_count + 1)
                s = int(unpickled_data["obj_size"])
                done = False
                for i in range(s * unit_size, coords[0] - s * unit_size, unit_size):
                    for j in range(s * unit_size, coords[1] - s * unit_size, unit_size):
                        if((i,j) not in list(map_object_order.keys())):
                            map_object_order[(i,j)] = unpickled_data
                            done = True
                            break
                    if(done):
                        break
                canv_obj.event_generate("<Configure>")
        top_window.destroy()

    def remove_it(event, canv_obj, top_window):
        if(event != "None"):
            for k in map_object_order: 
                if(event == map_object_order[k]["obj_name"]):
                    map_object_order.pop(k, "nothing")
                    break
            canv_obj.event_generate("<Configure>")
        top_window.destroy()

    def obj_in_out_map(state, mouse_prop_point, mouse_prop_charac, obj_type, canv_obj):
        if(not (mouse_prop_point.get() or mouse_prop_charac.get())):
            # top level size
            r = 1/3.5
            top_level_size = (int(scr_width * r), int(scr_height * r * 0.55))
        
            top = tk.Toplevel()
            top.geometry("%dx%d" % top_level_size)
            txt = f"Add {obj_type}" if(state > 0) else "Remove an object"

            l2 = tk.Label(top, text = txt, font = norm_font)
            l2.pack()
            option_list = ["None"]

            obj_selection = tk.StringVar(top, value = "None")

            if(state > 0):
                top.title(f"add {obj_type} in map")

                if(len(Dnd_data[obj_type]) > 0):
                    option_list = Dnd_data[obj_type]

                addition_menu = tk.OptionMenu(top, obj_selection, *option_list, command= lambda sel: add_it(sel, obj_type, (int(canv_obj.winfo_width() / unit_size) * unit_size, int(canv_obj.winfo_height() / unit_size) * unit_size), canv_obj, top)) 
                addition_menu.pack() 
            else:
                top.title(f"Remove an object from map")

                if(len(map_object_order) > 0):
                    option_list = []
                    for v in list(map_object_order.values()):
                        option_list.append(v["obj_name"])

                reduction_menu = tk.OptionMenu(top, obj_selection, *option_list, command= lambda sel: remove_it(sel, canv_obj, top)) 
                reduction_menu.pack() 
            top.mainloop()

    def show_image(mouse_prop_point, mouse_prop_charac, curr_obj):
        if(not (mouse_prop_point.get() or mouse_prop_charac.get())):
            pass

    def shape_chg_btn(mouse_prop_point, mouse_prop_charac, curr_obj, canv_obj):
        if(not (mouse_prop_point.get() or mouse_prop_charac.get())):
            pass

    # all functions here
    def line_color(curr_color):
        color_var.set(curr_color)

    def clear(mouse_prop_point, mouse_prop_charac, canv_obj):
        if(not (mouse_prop_point.get() or mouse_prop_charac.get())):
            map_grid.clear()
            Lines_order.clear()
            Lines_backup.clear()
            map_object_order.clear()
            canv_obj.event_generate("<Configure>")

    def clear_lines(mouse_prop_point, mouse_prop_charac, canv_obj):
        if(not (mouse_prop_point.get() or mouse_prop_charac.get())):
            map_grid.clear()
            Lines_order.clear()
            Lines_backup.clear()
            canv_obj.event_generate("<Configure>")

    def un_redo(mouse_prop_point, mouse_prop_charac, state, canv_obj):
        if(not (mouse_prop_point.get() or mouse_prop_charac.get())):
            if(state):
                if(len(Lines_backup) > 0):
                    temp_val = Lines_backup.pop()
                    for i in range(len(temp_val)):
                        if(i == 0):
                            Lines_order.append(temp_val[i])
                        else:
                            map_grid.update(temp_val[i])
            else:
                if(len(Lines_order) > 0):
                    coord1 = Lines_order.pop()
                    temp_val = [coord1]

                    # check to remove points or not
                    coord2 = coord1[2:4]
                    coord1 = coord1[0:2]

                    # to delete points
                    y1, y2 = 0, 0
                    for line in Lines_order:
                        p1, p2 = line[0:2], line[2:4]
                        if(coord1 == p1 or coord1 == p2):
                            y1 = 1
                        if(coord2 == p1 or coord2 == p2):
                            y2 = 1
                        if(y1 and y2):
                            Lines_backup.append(temp_val)
                            canv_obj.event_generate("<Configure>")
                            return
                    if(y1 == 0):
                        k1 = tuple(coord1)
                        temp_val.append({k1: map_grid.pop(k1, "black")})
                    if(y2 == 0):
                        k2 = tuple(coord2)
                        temp_val.append({k2: map_grid.pop(k2, "black")})
                    Lines_backup.append(temp_val)
            canv_obj.event_generate("<Configure>")

    def dimensioning(mouse_prop_point, mouse_prop_charac, canv_obj, unit_size):
        if(not (mouse_prop_point.get() or mouse_prop_charac.get())):
            for line in Lines_order:
                dis_del = int(max(abs(line[0] - line[2]) , abs(line[1] - line[3])) / unit_size) * dim_var.get()
                x_coord, y_coord = int((line[0] + line[2]) / 2), int((line[1] + line[3]) / 2)
                canv_obj.create_text(x_coord, y_coord, text = str(dis_del), fill = "darkblue", font="Times 20 italic bold", tag= "text_dim")
            for map_dim_obj in map_object_order:
                shift_y = int(int(map_object_order[map_dim_obj]["obj_size"]) * unit_size / 2)
                canv_obj.create_text(map_dim_obj[0], map_dim_obj[1] - shift_y, text = map_object_order[map_dim_obj]["obj_name"], fill = "darkblue", font="Times 20 italic bold", tag= "text_dim")

            canv_obj.after(7500, lambda: canv_obj.delete("text_dim"))

    def next_btn(mouse_prop_point, mouse_prop_charac):
        if(not (mouse_prop_point.get() or mouse_prop_charac.get())):
            pass

    # all widgets will be here
    # Creating Menubar 
    menubar = tk.Menu(Map_window)

    # Adding setting Menu and commands 
    set_menu = tk.Menu(menubar, tearoff = 0) 
    set_menu.add_command(label ='Save', command = lambda : save_load(cursor_holding_point, cursor_holding_character, 1)) 
    set_menu.add_command(label ='Load', command = lambda : save_load(cursor_holding_point, cursor_holding_character, 0)) 
    set_menu.add_command(label ='help', command = None) 
    set_menu.add_separator()
    set_menu.add_command(label ='clear', command = lambda: clear(cursor_holding_point, cursor_holding_character, map_canvas)) 
    set_menu.add_command(label ='Go back', command = lambda: [looped_window(Map_window)])
    menubar.add_cascade(label ='Settings', menu = set_menu) 

    Dim_menu = tk.Menu(menubar, tearoff= 0)
    Dim_menu.add_radiobutton(label="5", value= 5, variable= dim_var)
    Dim_menu.add_radiobutton(label="10", value= 10, variable= dim_var)
    Dim_menu.add_radiobutton(label="20", value= 20, variable= dim_var)
    Dim_menu.add_radiobutton(label="30", value= 30, variable= dim_var)
    menubar.add_cascade(label="Dimension", menu = Dim_menu)

    Change_menu = tk.Menu(menubar, tearoff= 0)
    Change_menu.add_command(label ='Undo', command = lambda: un_redo(cursor_holding_point, cursor_holding_character, 0, map_canvas)) 
    Change_menu.add_command(label ='Redo', command = lambda: un_redo(cursor_holding_point, cursor_holding_character, 1, map_canvas)) 
    menubar.add_cascade(label="Edit lines", menu = Change_menu)

    # display Menu 
    Map_window.config(menu = menubar)

    # Background canvas
    bg_canvas = tk.Canvas(Map_window)
    bg_canvas.pack(fill="both", expand= True)
    bg_canvas.config(cursor = "arrow")

    #background image
    if(file_exists("Map_mode.png")):
        img = Image.open("Map_mode.png")
        r_size = 5/7
        resized_img = img.resize((int(img.size[0] * ratio * r_size), int(img.size[1] * r_size)))
        bg_image = ImageTk.PhotoImage(resized_img)
        bg_canvas.create_image(int(scr_width/2),int(scr_height/2), image = bg_image, anchor = "center")
    else:
        bg_canvas.config(bg = "cyan")

    # create terrain and addition buttons frame
    # terrain  button frame parameters
    btn_fram_param = {"bg":""}
    pack_common_params = {"side": "top", "pady":0}

    btn_upr_frame = tk.Frame(bg_canvas, **btn_fram_param)
    btn_upr_frame.pack(fill="both", **pack_common_params)

    btn_side_frame = tk.Frame(btn_upr_frame, **btn_fram_param)
    btn_side_frame.pack(side= "right", fill="y", expand=True)

    btn_lwr_frame = tk.Frame(bg_canvas, **btn_fram_param)
    btn_lwr_frame.pack(fill="both", **pack_common_params)

    btn_clr_frame = tk.Frame(btn_lwr_frame, **btn_fram_param)
    btn_clr_frame.pack(side="right", fill="y" , expand=True)

    # terrain button params
    font_param = {"font": norm_font} 
    btn_pack_params = {"padx": (int(scr_width/100), 0), "pady": (0, int(scr_height/120))}
    btns = {}

    # terrains buttons
    btn_i = 0
    for ti in Dnd_terrains:
        # button action
        def action(c = Dnd_terrains[ti], val = cursor_holding_point, val1 = cursor_holding_character):
            if(not (val.get() or val1.get())):
                line_color(c)

        def set_world_color(eff, wc = Dnd_terrains[ti]):
            world_color.set(wc)

        # button definitions
        if(btn_i < 4):
            btns[Dnd_terrains[ti]] = tk.Button(btn_upr_frame, text= ti, fg="white", bg=Dnd_terrains[ti], **font_param, command= action)
            btns[Dnd_terrains[ti]].pack(side="left", **btn_pack_params)
            btns[Dnd_terrains[ti]].bind("<Double-Button-1>", set_world_color)
        else:
            btns[Dnd_terrains[ti]] = tk.Button(btn_lwr_frame, text= ti, fg="white", bg=Dnd_terrains[ti], **font_param, command= action)
            btns[Dnd_terrains[ti]].pack(side="left", **btn_pack_params)
            btns[Dnd_terrains[ti]].bind("<Double-Button-1>", set_world_color)
        btn_i += 1

    # addition buttons
    for k in Dnd_data:
        # addition button action
        def obj_action(mp = cursor_holding_point, cp = cursor_holding_character , c = k):
            obj_in_out_map(1, mp, cp, c, map_canvas)
        # all addition except terrains
        btns[k] = tk.Button(btn_side_frame, text= f"Add {k}" , bg="black", fg="white", **font_param, command= obj_action)
        btns[k].pack(side="left", **btn_pack_params)

    # other buttons
    btns["clear_lines"] = tk.Button(btn_clr_frame, text= "clear lines" , bg="white", fg="black", **font_param, command= lambda: clear_lines(cursor_holding_point, cursor_holding_character, map_canvas))
    btns["clear_lines"].pack(side="right", **btn_pack_params)

    btns["remove"] = tk.Button(btn_clr_frame, text= "remove" , bg="white", fg="black", **font_param, command= lambda : obj_in_out_map(-1, cursor_holding_point, cursor_holding_character, "", map_canvas))
    btns["remove"].pack(side="right", **btn_pack_params)

    btns["Dimension"] = tk.Button(btn_clr_frame, text= "Dimension" , bg="white", fg="black", **font_param, command= lambda: dimensioning(cursor_holding_point, cursor_holding_character, map_canvas, unit_size))
    btns["Dimension"].pack(side="right", **btn_pack_params)

    # Create map Canvas
    map_canvas = tk.Canvas(bg_canvas, bg ="yellow")
    map_canvas.pack(fill="both", expand=True, **pack_common_params)
    map_canvas.config(cursor = "spider")

    # for manually updating character position
    def object_position_update(event, canv_obj, mp, cp, move_obj):
        #Basic params
        global map_object_order
        r = unit_size / 4
        x,y = int(event.x), int(event.y)

        if(int(event.type) == 4 and not mp.get()):
            if(cp.get() and len(move_obj.get()) != 0):
                x, y = find_snap_grid(x, y, unit_size, int(canv_obj.winfo_width()), int(canv_obj.winfo_height()))
                if((x,y) not in list(map_object_order.keys())):
                    cha_rec = eval(move_obj.get().split("~")[1])
                    map_object_order[(x,y)] = cha_rec
                    cp.set(0)
                    move_obj.set("")
                    canv_obj.unbind("<Motion>")

            else:
                pxy = find_min_distance((x,y), list(map_object_order.keys()), unit_size)
                cha_rec = map_object_order.pop(pxy, "nothing")
                if(cha_rec != "nothing"):
                    move_obj.set(f"{pxy}~{cha_rec}")
                    cp.set(1)
                    canv_obj.bind("<Motion>", lambda eff: lastcharac2cursor(pxy, int(eff.x), int(eff.y), r, canv_obj, cha_rec))

    #fill canvas with grids, lines, points etc
    def create_grid(event, canv_obj, cursor_data, mouse_btn = "l"):
        #global block_img
        w = canv_obj.winfo_width() # Get current width of canvas
        h = canv_obj.winfo_height() # Get current height of canvas

        canv_obj.delete('grid_comp') # Will only remove the grid components
        canv_obj.delete('photo_comp') # Will only remove the photo components
        canv_obj.delete('line2cursor') # Will update cursor line
        canv_obj.delete("hover_image") # if any hover object
        canv_obj.delete("area_polygon")

        global point_exist, Lines_order, Lines_backup, block_img
        del_w = del_h = unit_size #unit rectangle size

        #Basic params
        set_color, r = "", unit_size / 4
        if(len(color_var.get()) != 0):
            set_color = color_var.get()
        else:
            set_color = "black"
        x, y = find_snap_grid(int(event.x), int(event.y), unit_size, w, h)

        # add circle heads to map if left mouse click and circle point laid
        if(int(event.type) == 4 and not cursor_holding_character.get()):
            if(mouse_btn == "l"):
                if((x,y) not in list(map_grid.keys())):
                    map_grid[(x,y)] = set_color
                else:
                    point_exist = 1

                # line drag animation
                if(not cursor_data.get()):
                    Lines_order.append([x,y])
                    cursor_data.set(1)
                    canv_obj.bind("<Motion>", lambda eff: lastpoint2cursor_line(canv_obj, (x,y), (int(eff.x), int(eff.y)), r, set_color))
                else:
                    cursor_data.set(0)
                    canv_obj.unbind("<Motion>")
                    point_exist = 0

                    # empty backup
                    Lines_backup.clear()

                    # automatic no map grid used
                    temp_point = Lines_order.pop()
                    temp_point.extend([x, y])
                    Lines_order.append(temp_point)

        if(int(event.type) == 2 and not cursor_holding_character.get()):                                     
            if(cursor_data.get()):     
                if(len(Lines_order) != 0):
                    temp_point = Lines_order.pop()        
                    if(not point_exist):
                        map_grid.pop(tuple(temp_point), "nothing")
                    point_exist = 0    
                cursor_data.set(0)
                canv_obj.unbind("<Motion>")  

        # remove more copies from 3x onwards from lines
        new_order_list = []
        [new_order_list.append(line) for line in Lines_order if (line not in new_order_list)]
        Lines_order = new_order_list

        # Creates all shapes
        for i in range(0, w, del_w):
            for j in range(0, h, del_h):
                canv_obj.create_rectangle(i , j, i + del_w, j + del_h, fill= world_color.get(), tag='grid_comp')

        check_if_polygon(cursor_data, canv_obj)

        for coord in map_grid:
            canv_obj.create_oval(coord[0] - r, coord[1] - r, coord[0] + r, coord[1] + r, fill= map_grid[coord], tag='grid_comp')

        for line in Lines_order:
            if(len(line) == 4):
                canv_obj.create_line(*line, fill= map_grid[(line[0], line[1])], width = 2, tag = "grid_comp")


        for map_objs in map_object_order:
            map_objs_img = "" if("img" not in list(map_object_order[map_objs].keys()) or not file_exists(map_object_order[map_objs]["img"])) else map_object_order[map_objs]["img"]
            
            s = int(map_object_order[map_objs]["obj_size"])
            offsxy = (s % 2) * int(unit_size / 2)
            charac_base_color = "red" if(map_object_order[map_objs]["object_type"] == "monster") else ("green" if (map_object_order[map_objs]["object_type"] == "characters" and map_object_order[map_objs]["nature"] == "friend") else "brown")
            charac_txt = map_object_order[map_objs]["obj_name"] if(len(map_object_order[map_objs]["obj_name"]) <= 4) else map_object_order[map_objs]["obj_name"][:2] + map_object_order[map_objs]["obj_name"][-2:]

            canv_obj.create_rectangle(map_objs[0] + offsxy - int(1.7 * r) * s, map_objs[1] + offsxy - int(1.7 * r) * s, map_objs[0] + offsxy + int(1.7 * r) * s, map_objs[1] + offsxy + int(1.7 * r) * s, fill = charac_base_color, tag = "photo_comp")

            if(map_objs_img != ""): 
                map_objs_img = Image.open(map_objs_img)
                presized_img = map_objs_img.resize((s * unit_size, s * unit_size))
                block_img[map_objs] = ImageTk.PhotoImage(presized_img)
                canv_obj.create_image(map_objs[0] + offsxy, map_objs[1] + offsxy, image = block_img[map_objs], anchor = "center", tag = "photo_comp")
            else:
                canv_obj.create_text(map_objs[0] + offsxy, map_objs[1] + offsxy, text = charac_txt, font = "Pursia", tag = "photo_comp")

    # first grid making
    map_canvas.bind('<Configure>', lambda eff: create_grid(eff, map_canvas, 0))

    # rest of map actions
    map_canvas.bind('<1>', lambda eff: create_grid(eff, map_canvas, cursor_holding_point))
    Map_window.bind('<Key>', lambda eff: create_grid(eff, map_canvas, cursor_holding_point))

    # specific action to move character
    map_canvas.bind('<3>', lambda eff: object_position_update(eff, map_canvas, cursor_holding_point, cursor_holding_character, temp_move_obj))

    # info frames
    info_lwr_frame = tk.Frame(bg_canvas,  **btn_fram_param)
    info_lwr_frame.pack(fill="x", side="bottom")

    info_upr_frame = tk.Frame(bg_canvas, **btn_fram_param)
    info_upr_frame.pack(fill="x", side="bottom")
    
    info_btns = {}

    # initiative frame
    tk.Label(info_upr_frame, text="Order: ", font = ("Ariel", int(scr_height/ 45), "bold")).pack(side="left", fill="both")

    # Next button
    info_btns["Next"] = tk.Button(info_upr_frame, text= "Next" , bg="white", fg="black", **font_param)
    info_btns["Next"].pack()

    #shape change
    info_btns["shape change"] = tk.Button(info_lwr_frame, text= "shape change" , bg="red", fg="white", **font_param)
    info_btns["shape change"].pack()

    #show image
    info_btns["show image"] = tk.Button(info_lwr_frame, text= "show image" , bg="white", fg="black", **font_param)
    info_btns["show image"].pack()

    # Execute Tkinter
    Map_window.mainloop()

def Home_screen():
    global loop_window, Dnd_data, mode

    loop_window = False
    mode = ""

    Dnd_editor()

    if(mode != ""):
        Dnd_data = fill_Dnd_data(Dnd_data)

    if(mode == "Dm_setup_mode"):
        Dm_setup_mode()
    #elif(mode == "Dm_mode"):
        #Dm_setup_mode()
    elif(mode == "Map_mode"):
        Map_mode()

def main():
    setup_editor()

    global scr_width, scr_height, ratio
    if(scr_width <= 1150):
        scr_width = 1150
    if(scr_height <= 640):
        scr_height = 640
    ratio = scr_width / scr_height

    while(loop_window):
        Home_screen()

main()