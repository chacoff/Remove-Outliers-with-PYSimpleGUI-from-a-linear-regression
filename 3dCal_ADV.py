import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
#  from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import tkinter as Tk
from os import listdir
import csv


def find_csv_filenames(path_to_dir, suffix=".csv"):
    filenames = listdir(path_to_dir)
    return [filename for filename in filenames if filename.endswith(suffix)]


def onpick1(evento):
    if isinstance(evento.artist, Line2D):
        thisline = evento.artist
        ind = evento.ind
        xp = np.take(thisline.get_xdata(), ind)[0]
        yp = np.take(thisline.get_ydata(), ind)[0]
        po = [int(xp), yp]
        element = [';'.join(str(n) for n in po)]
        point_to_remove.append(element)
        # print(point_to_remove)
        window["-POINT LIST-"].update(point_to_remove)


def draw_figure_w_toolbar(canvas, fig, canvas_toolbar):
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    if canvas_toolbar.children:
        for child in canvas_toolbar.winfo_children():
            child.destroy()

    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
    figure_canvas_agg.mpl_connect("pick_event", onpick1)  # picker = True on plots

    toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)
    toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)


def clear_drawing():
    plt.clf()
    plt.figure(1)
    fig = plt.gcf()
    DPI = fig.get_dpi()
    fig.set_size_inches(400 * 2 / float(DPI), 400 / float(DPI))
    draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)
    window["-POINT LIST-"].update('')


class Toolbar(NavigationToolbar2Tk):
    # only display the buttons we need
    toolitems = [t for t in NavigationToolbar2Tk.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom', 'Save')]  # possibility to add or remove buttons

    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)
# ---- ----


# ---- PySimpleGUI CODE ----
sg.ChangeLookAndFeel('Reddit')

control_column = [
    [sg.Text('Sensor', size=(11, 1), auto_size_text=False, justification='left'),
     sg.InputText('Browse CSV', size=(16, 1), enable_events=True, key="-FOLDER-"), sg.FolderBrowse()],
    [sg.Listbox(values=[], size=(37, 15), enable_events=True, key="-FILE LIST-")],
    [sg.B('Plot'), sg.B('Clear') , sg.B('Exit')],
    [sg.T('Controls:')],
    [sg.Canvas(key='controls_cv')],
]

plot_column = [
    [sg.T('Figure:')],
    [sg.Column(
        layout=[[sg.Canvas(key='fig_cv', size=(420 * 2, 420))]],  # it's important to set this size
        background_color='#DAE0E6', pad=(0, 0),
    )
    ],
]

points_column = [
    [sg.T('Points:')],
    [sg.Listbox(values=[], size=(18, 20), auto_size_text=True, enable_events=True, key="-POINT LIST-")],
    [sg.B('Delete'), sg.B('Update'), sg.B('Clean')],
]

layout = [
    [
        sg.Column(control_column),
        sg.VSeperator(),
        sg.Column(plot_column),
        sg.VSeperator(),
        sg.Column(points_column),
    ]
]

window = sg.Window(title='3D calibration', layout=layout, finalize=True)
clear_drawing()
point_to_remove = list()

while True:
    event, values = window.Read()
    # print(values)
    if event in [None, 'Exit']:  # always,  always give a way out!
        window.Close()
        break
    elif event is '-FOLDER-':
        folder = values["-FOLDER-"]
        try:  # Get list of files in folder
            file_list = find_csv_filenames(folder)
        except ImportError:
            file_list = []
        # print(file_list)
        window["-FILE LIST-"].update(file_list)
    elif event is 'Plot':
        try:
            plt.clf()
            point_to_remove = list()
            import_file_path = values["-FOLDER-"] + '/' + values['-FILE LIST-'][0]  # print(import_file_path)
            data = np.loadtxt(import_file_path, delimiter=';', skiprows=0)
            x = data[:, 0]
            y = data[:, 1]
            coR2 = np.corrcoef(x, y)  # R2 calculation
            co_xy = coR2[0, 1]
            r_squared = co_xy ** 2
            fig = plt.figure()  # could be Figure() but gets tricky with the plot labels
            DPI = fig.get_dpi()
            fig.set_size_inches(400 * 2 / float(DPI), 400 / float(DPI))  # for the canvas size
            fig.add_subplot(111).plot(x, y, 'o', picker=5)  # plt.scatter(x, y, picker=True)
            plt.xlabel("Gray Level")
            plt.ylabel("Resolution [mm/px]")
            plt.grid()
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            plt.plot(x, p(x), 'r--')
            text = f"$R^2 = {r_squared:0.3f}$"
            plt.gca().text(0.35, 0.95, text, transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
            # ---- Instead of plt.show()
            draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)
            # ---- windows['fig_cv'] = window.FindElement('fig_cv')
        except ImportError:
            pass
    elif event is 'Update':
        try:
            plt.clf()
            point_to_remove = list()
            import_file_path = values["-FOLDER-"] + '/' + values['-FILE LIST-'][0]  # print(import_file_path)
            data = np.loadtxt(import_file_path, delimiter=';', skiprows=0)
            x = data[:, 0]
            y = data[:, 1]
            coR2 = np.corrcoef(x, y)  # R2 calculation
            co_xy = coR2[0, 1]
            r_squared = co_xy ** 2
            fig = plt.figure()  # could be Figure() but gets tricky with the plot labels
            DPI = fig.get_dpi()
            fig.set_size_inches(400 * 2 / float(DPI), 400 / float(DPI))  # for the canvas size
            fig.add_subplot(111).plot(x, y, 'o', picker=5)  # plt.scatter(x, y, picker=True)
            plt.xlabel("Gray Level")
            plt.ylabel("Resolution [mm/px]")
            plt.grid()
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            plt.plot(x, p(x), 'r--')
            text = f"$R^2 = {r_squared:0.3f}$"
            plt.gca().text(0.35, 0.95, text, transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
            # ---- Instead of plt.show()
            draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)
            # ---- windows['fig_cv'] = window.FindElement('fig_cv')
        except ImportError:
            pass
    elif event is 'Clear':
        point_to_remove = list()
        clear_drawing()
    elif event is 'Clean':
        point_to_remove = list()
        window["-POINT LIST-"].update('')
    elif event is 'Delete':
        try:
            point = values["-POINT LIST-"][0]
            import2 = values["-FOLDER-"] + '/' + values['-FILE LIST-'][0]  # print(import_file_path)
            # print(point, import2)
            lines = list()
            with open(import2, 'r') as readFile:
                reader = csv.reader(readFile)
                for row in reader:
                    if row == point:
                        pass
                    else:
                        lines.append(row)
            # print(len(lines))
            with open(import2, 'w', newline='') as writeFile:
                writer = csv.writer(writeFile)
                writer.writerows(lines)
            point_to_remove = list()
            window["-POINT LIST-"].update('')
        except ImportError:
            pass
