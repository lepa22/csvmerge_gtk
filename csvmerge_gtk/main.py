import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf
import os
import glob
import csv
from datetime import datetime
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(
            title="Spectra CSV merger GTK (ENLIGHTEN spectroscopy software files)"
        )
        # Gtk.Settings.get_default().set_property("gtk-icon-theme-name", "Adwaita")
        self.set_default_size(1200, 700)
        hints = Gdk.Geometry()
        hints.min_width = 1000
        hints.min_height = 600
        self.set_geometry_hints(None, hints, Gdk.WindowHints.MIN_SIZE)

        self.set_border_width(5)
        self.connect("destroy", Gtk.main_quit)

        # Start setup GUI
        # Main structure of window widgets
        headerbar = Gtk.HeaderBar()
        main_vbox = Gtk.VBox(spacing=5)
        left_buttons_hbox = Gtk.HBox(spacing=5)
        right_buttons_hbox = Gtk.HBox(spacing=5)
        panes_hbox = Gtk.HBox(spacing=0)
        self.left_pane_vbox = Gtk.VBox(spacing=0)
        right_pane_vbox = Gtk.VBox(spacing=0)
        radio_hbox = Gtk.HBox(spacing=5)
        left_radio_vbox = Gtk.VBox(spacing=5)
        right_radio_vbox = Gtk.VBox(spacing=5)
        saveas_hbox = Gtk.HBox(spacing=5)
        merge_btn_hbox = Gtk.HBox(spacing=5)
        self.add(main_vbox)

        # # header buttons
        # open_btn = Gtk.Button.new_with_label("Open Folder...")
        # open_btn.connect("clicked", self.on_open_btn_click)
        # # buttons_hbox.pack_start(open_btn, False, False, 0)
        # headerbar.pack_start(open_btn)
        headerbar.set_show_close_button(True)
        headerbar.props.title = (
            "Spectra CSV merger GTK (ENLIGHTEN spectroscopy software files)"
        )

        hamburger_menu_btn = Gtk.Button()
        image = Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.BUTTON)
        hamburger_menu_btn.add(image)
        headerbar.pack_end(hamburger_menu_btn)
        self.set_titlebar(headerbar)

        hamburger_menu_btn.connect("clicked", self.on_hamburger_menu_btn_clicked)

        # top buttons
        open_btn = Gtk.Button.new_with_label("Open folder...")
        open_btn.connect("clicked", self.on_open_btn_click)
        left_buttons_hbox.pack_start(open_btn, False, False, 5)

        # assemble_btn = Gtk.Button.new_with_label("Assemble selected files > >")
        # assemble_btn.connect("clicked", self.on_assemble_btn_click)
        # left_buttons_hbox.pack_end(assemble_btn, False, False, 5)
        self.left_pane_vbox.pack_start(left_buttons_hbox, False, False, 5)

        self.total_n = 0
        num_selected_label = Gtk.Label()
        num_selected_label.set_text(f"Selected files: ")

        self.total_n_label = Gtk.Label()
        self.total_n_label.set_text("0")
        right_buttons_hbox.pack_start(num_selected_label, False, False, 5)
        right_buttons_hbox.pack_start(self.total_n_label, False, False, 5)

        preview_check = Gtk.CheckButton()
        preview_check.set_label("Preview")
        preview_check.connect("toggled", self.on_preview_check_toggle)
        right_buttons_hbox.pack_end(preview_check, False, False, 5)
        right_pane_vbox.pack_start(right_buttons_hbox, False, False, 10)

        # Treeview
        # Create a frame for the treeview
        tree_frame = Gtk.Frame()
        tree_frame.set_border_width(5)

        self.treeview = Gtk.TreeView()
        self.treeview.connect("row-activated", self.on_double_click)
        # Make treeview scrollable
        self.tree_scroll = Gtk.ScrolledWindow()
        self.tree_scroll.add(self.treeview)
        # self.tree_scroll.set_size_request(500, -1)

        tree_frame.add(self.tree_scroll)
        self.left_pane_vbox.pack_start(tree_frame, True, True, 0)
        self.left_pane_vbox.set_size_request(500, -1)

        # Listview
        # Create a frame for the listview
        list_frame = Gtk.Frame()
        list_frame.set_border_width(5)

        self.listview = Gtk.TreeView()
        self.listview.connect("key-press-event", self.on_key_press_event)
        self.listview.set_property("has-tooltip", True)
        self.listview.connect("query-tooltip", self.on_query_tooltip)

        # Make listview scrollable
        self.list_scroll = Gtk.ScrolledWindow()
        self.list_scroll.add(self.listview)
        self.list_scroll.set_size_request(500, -1)

        list_frame.add(self.list_scroll)
        right_pane_vbox.pack_start(list_frame, True, True, 0)

        # Radio buttons left
        left_radio_frame = Gtk.Frame()
        left_radio_frame.set_label("Export CSV header columns")
        left_radio_frame.set_border_width(5)

        self.radio1_left = Gtk.RadioButton.new_with_label_from_widget(
            None, "Path/Filename"
        )
        self.radio1_left.connect("toggled", self.on_radio_left_toggle, 1)
        left_radio_vbox.pack_start(self.radio1_left, False, False, 0)

        self.radio2_left = Gtk.RadioButton.new_from_widget(self.radio1_left)
        self.radio2_left.set_label("Filename (relative path)")
        self.radio2_left.set_active(True)
        self.radio2_left.connect("toggled", self.on_radio_left_toggle, 2)
        left_radio_vbox.pack_start(self.radio2_left, False, False, 0)

        self.radio3_left = Gtk.RadioButton.new_from_widget(self.radio1_left)
        self.radio3_left.set_label("Filename")
        self.radio3_left.connect("toggled", self.on_radio_left_toggle, 3)
        left_radio_vbox.pack_start(self.radio3_left, False, False, 0)

        left_radio_frame.add(left_radio_vbox)
        radio_hbox.pack_start(left_radio_frame, True, True, 0)

        # Radio buttons right
        right_radio_frame = Gtk.Frame()
        right_radio_frame.set_label("Export CSV columns")
        right_radio_frame.set_border_width(5)

        self.radio1_right = Gtk.RadioButton.new_with_label_from_widget(
            None, "X,Y,Y,Y format"
        )
        self.radio1_right.connect("toggled", self.on_radio_right_toggle, 1)
        right_radio_vbox.pack_start(self.radio1_right, False, False, 0)

        self.radio2_right = Gtk.RadioButton.new_from_widget(self.radio1_right)
        self.radio2_right.set_label("X,Y,X,Y format")
        self.radio2_right.connect("toggled", self.on_radio_right_toggle, 2)
        right_radio_vbox.pack_start(self.radio2_right, False, False, 0)

        self.legend_label = Gtk.Label()
        self.legend_label.set_label("X: Wavenumber, Y: Intensity")
        self.legend_label.set_xalign(0.05)
        right_radio_vbox.pack_start(self.legend_label, False, False, 0)

        right_radio_frame.add(right_radio_vbox)
        radio_hbox.pack_start(right_radio_frame, True, True, 0)

        right_pane_vbox.pack_start(radio_hbox, False, True, 0)

        # Text entry
        self.saveas_label = Gtk.Label()
        self.saveas_label.set_text("Output:")
        saveas_hbox.pack_start(self.saveas_label, False, True, 5)

        self.saveas_entry = Gtk.Entry()
        self.saveas_entry.set_text("")
        saveas_hbox.pack_start(self.saveas_entry, True, True, 5)

        self.saveas_btn = Gtk.Button(label="Save as...")
        self.saveas_btn.connect("clicked", self.on_save_btn_click)
        saveas_hbox.pack_start(self.saveas_btn, False, True, 5)
        right_pane_vbox.pack_start(saveas_hbox, False, True, 5)

        self.merge_btn = Gtk.Button(label="Merge CSV")
        self.merge_btn.connect("clicked", self.on_merge_btn_click)
        merge_btn_hbox.pack_start(self.merge_btn, True, True, 5)

        right_pane_vbox.pack_start(merge_btn_hbox, False, True, 5)

        panes_hbox.pack_start(self.left_pane_vbox, True, True, 0)
        panes_hbox.pack_start(right_pane_vbox, True, True, 0)

        main_vbox.pack_start(panes_hbox, True, True, 0)

        # self.listview.connect("query-tooltip", self.on_query_tooltip)

        # End setup GUI

        # Create new treestore with 2 columns (bool for checkbox)
        self.treestore = Gtk.TreeStore(str, bool)
        # Add the treestore to the treeview
        self.treeview.set_model(self.treestore)
        self.create_treeview_columns()

        # Create a new treestore with 1 column (string)
        self.liststore = Gtk.TreeStore(str)
        # # Add the treestore to the treeview
        self.listview.set_model(self.liststore)
        self.create_listview_columns()

        selection = self.listview.get_selection()
        selection.connect("changed", self.on_selection_changed)

        # # Show the window and all of its child widgets
        self.show_all()

        self.path = ""
        self.save_path = ""
        self.radio_left = 2
        self.radio_right = 1
        self.preview = False
        # self.selected_list_item = ""

    # class methods

    def on_hamburger_menu_btn_clicked(self, button):
        menu = Gtk.Menu()
        about_item = Gtk.MenuItem(label="About")
        about_item.connect("activate", self.on_about_item_activated)
        menu.append(about_item)
        menu.show_all()
        menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

    def on_about_item_activated(self, menu_item):
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_program_name("Spectra CSV merger GTK")
        about_dialog.set_version("1.0")
        about_dialog.set_copyright("Copyright (C) 2023 KRG University of Ioannina")
        about_dialog.set_comments(
            "A program for previewing and merging ENLIGHTEN spectroscopy software files."
        )
        about_dialog.set_website("https://myweb.uoi.gr/nkourkou/")
        about_dialog.set_website_label("Visit our website")

        # Add a link button to the about dialog
        link_button = Gtk.LinkButton(
            uri="https://myweb.uoi.gr/nkourkou/", label="Visit our website"
        )
        about_dialog.get_content_area().pack_start(link_button, False, False, 0)

        pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 1, 1)
        about_dialog.set_logo(pixbuf)
        about_dialog.set_authors(["Eleftherios Pavlou"])
        about_dialog.run()
        about_dialog.destroy()

    def on_query_tooltip(self, treeview, x, y, keyboard_mode, tooltip):
        # offset of 27 pixels is needed or else the activation area for the tooltips
        # starts at the list's header
        result = treeview.get_path_at_pos(x, y - 27)
        if result is None:
            return False
        path, column, cell_x, cell_y = result

        # Get the text of the item at the given path
        item = self.liststore[path][0]

        # Get the full path of the item
        full_path = []
        node = self.liststore.get_iter(path)
        while node is not None:
            full_path.append(self.liststore[node][0])
            node = self.liststore.iter_parent(node)

        # Show the full path in the tooltip
        full_path.reverse()
        tooltip.set_text(" / ".join(full_path))

        return True

    def on_key_press_event(self, treeview, event):
        if event.keyval == Gdk.KEY_Delete:
            # Get the selected row
            selection = treeview.get_selection()
            (model, treeiter) = selection.get_selected()
            if treeiter is not None:
                item_path = model[treeiter][0]
                treepath = self.get_treepath(self.paths_dict, item_path)
                self.toggle_item(treepath, self.treestore)
                model.remove(treeiter)
                self.total_n = len(self.get_list_items())
                self.total_n_label.set_text(str(self.total_n))

    def get_list_items(self):
        list_model = self.listview.get_model()
        list_items = []
        for item in list_model:
            list_items.append(item[0])
        return list_items

    def on_selection_changed(self, selection):
        selection = self.listview.get_selection()
        (model, pathlist) = selection.get_selected_rows()
        if pathlist:
            for path in pathlist:
                csv_file_path = self.liststore[path][0]
            if self.preview:
                x, y = self.process_csv(csv_file_path)
                self.remove_plot_box()
                self.add_plot_box(x=x, y=y)

        # else:
        # print("not plotting")

    def process_csv(self, filename):
        with open(filename, "r") as f:
            csv_reader = csv.reader(f, delimiter=",")
            for row in csv_reader:
                if "Pixel" in row:
                    break
            x = []
            y = []
            for row in csv_reader:
                x.append(float(row[2]))
                y.append(float(row[3]))
        return x, y

    def plot_data(self, x=[], y=[]):
        fig, ax = plt.subplots()
        ax.plot(x, y, color="mediumvioletred")
        ax.set_xlabel("Raman shift (cm$^{-1}$)")
        ax.set_ylabel("Intensity")
        ax.grid(linestyle=":", alpha=1)
        # ax.legend()
        # ax.set_title("ksgdfkljgdfsjljj")
        # plt.tight_layout()
        plt.close()
        return fig

    def add_plot_box(self, x=[], y=[]):
        # make padding constant
        def update_padding(event):
            fig_width, fig_height = fig.get_size_inches() * fig.dpi
            fig.subplots_adjust(
                left=80 / fig_width,
                right=1 - 10 / fig_width,
                bottom=50 / fig_height,
                top=1 - 10 / fig_height,
            )

        self.mpl_vbox = Gtk.VBox(spacing=0)
        self.mpl_frame = Gtk.Frame()
        # self.mpl_frame.set_label("Spectrum preview")
        self.mpl_frame.set_border_width(5)

        fig = self.plot_data(x, y)
        fig.subplots_adjust(left=0.15, bottom=0.2, right=0.95, top=0.95)

        # Add canvas to vbox
        self.canvas = FigureCanvas(fig)  # a Gtk.DrawingArea

        self.mpl_vbox.pack_start(self.canvas, True, True, 0)
        self.canvas.mpl_connect("resize_event", update_padding)
        update_padding(None)

        # # Create toolbar
        toolbar = NavigationToolbar(self.canvas)
        self.mpl_vbox.pack_start(toolbar, False, False, 0)
        self.mpl_frame.set_size_request(-1, 250)

        self.mpl_frame.add(self.mpl_vbox)
        self.left_pane_vbox.pack_start(self.mpl_frame, True, True, 0)

        self.left_pane_vbox.show_all()

    def remove_plot_box(self):
        self.mpl_frame.remove(self.mpl_vbox)
        self.mpl_vbox.destroy()
        self.mpl_frame.destroy()

    def on_preview_check_toggle(self, preview_check):
        # selection = self.listview.get_selection()
        # selection.unselect_all()
        is_active = preview_check.get_active()
        if is_active:
            # print("Preview enabled")
            self.preview = True
            # self.add_plot_box()


            selection = self.listview.get_selection()
            (model, pathlist) = selection.get_selected_rows()
            if pathlist:
                for path in pathlist:
                    csv_file_path = self.liststore[path][0]
                # if self.preview:
                    x, y = self.process_csv(csv_file_path)
                    # self.remove_plot_box()
                    self.add_plot_box(x=x, y=y)
            else:
                self.add_plot_box()
                self.mpl_frame.set_visible(False)
        else:
            # print("Preview disabled")
            self.preview = False
            self.remove_plot_box()

        self.listview.grab_focus()

    def create_treeview_columns(self):
        # Create a cell renderer for the checkbox
        self.checkbox_renderer = Gtk.CellRendererToggle()
        self.checkbox_renderer.set_property("active", False)
        self.checkbox_renderer.connect("toggled", self.checkbox_toggled, self.treestore)

        # Create a column for the text
        text_column = Gtk.TreeViewColumn("Tree view")
        self.treeview.append_column(text_column)
        text_column.pack_start(self.checkbox_renderer, expand=False)

        # Create a cell renderer for the text
        text_renderer = Gtk.CellRendererText()
        text_column.pack_start(text_renderer, expand=True)

        # Connect the checkbox column to the model's column
        text_column.add_attribute(self.checkbox_renderer, "active", 1)

        # Connect the text column to the model's column
        text_column.add_attribute(text_renderer, "text", 0)

    def create_listview_columns(self):
        # # Create a column for the text
        text_column = Gtk.TreeViewColumn("Selected files")
        self.listview.append_column(text_column)

        # Create a cell renderer for the text
        text_renderer = Gtk.CellRendererText()
        text_column.pack_start(text_renderer, expand=True)

        # Connect the text column to the model's column
        text_column.add_attribute(text_renderer, "text", 0)

    def populate_listview(self):
        for f in self.get_selected_filepaths():
            self.liststore.append(None, [f])

    def add_selected_items(self):
        # add selection to listview
        selection = self.listview.get_selection()
        selection.unselect_all()
        self.liststore.clear()
        self.populate_listview()
        self.total_n = len(self.get_list_items())
        self.total_n_label.set_text(str(self.total_n))




    def checkbox_toggled(self, renderer, path, model):
        def update_children(parent, value):
            child = self.treestore.iter_children(parent)
            while child is not None:
                self.treestore[child][1] = value
                update_children(child, value)
                child = self.treestore.iter_next(child)

        iter = model.get_iter(path)
        update_children(iter, model[iter][1])
        value = not model[iter][1]
        model[iter][1] = value
        update_children(iter, value)

        self.add_selected_items()



    def on_double_click(self, treeview, path, column):
        if treeview.row_expanded(path):
            treeview.collapse_row(path)
        else:
            treeview.expand_row(path, False)

    def get_selected_items(self):
        def get_child_items(parent_iter):
            iter = self.treestore.iter_children(parent_iter)
            while iter:
                if self.treestore.get_value(iter, 0):
                    selected_items.append(self.treestore.get_value(iter, 1))
                if self.treestore.iter_has_child(iter):
                    get_child_items(iter)
                iter = self.treestore.iter_next(iter)

        selected_items = []
        get_child_items(None)
        return selected_items

    def is_enlighten(self, f):
        try:
            with open(f, "r") as csvfile:
                reader = csv.reader(csvfile, delimiter=",")
                first_line = next(reader)
                if "ENLIGHTEN" in first_line[0]:
                    # print(f)
                    return True
                else:
                #     print('not')
                    return False
        except UnicodeDecodeError as e:
            print(f"UnicodeDecodeError on file:", f)
            print("   ", e)
            # return False

    def get_paths(self):
        csv_files = glob.glob(os.path.join(self.path, "**", "*.csv"), recursive=True)

        enlighten_files = []
        for f in csv_files:
            # print(f)
            if self.is_enlighten(f):
                # print(f)
                enlighten_files.append(f)
        return enlighten_files

    def paths_to_dict(self, paths_list):
        d = {}
        paths = [os.path.relpath(path, self.path) for path in paths_list]
        for path in paths:
            current_dict = d
            parts = path.split(os.sep)
            for part in parts:
                if part not in current_dict:
                    current_dict[part] = {}
                current_dict = current_dict[part]
        d = {self.path: d}
        return d

    def dict_to_paths(self, d, path=""):
        filepaths = []
        for key, value in d.items():
            new_path = os.path.join(path, key)
            if isinstance(value, dict):
                filepaths.append(new_path)
                filepaths.extend(self.dict_to_paths(value, path=new_path))
            else:
                filepaths.append(new_path)
        return filepaths

    def add_to_tree(self, paths_dict, parent=None):
        for path, sub_paths in paths_dict.items():
            if parent:
                current_iter = self.treestore.append(parent, [path, False])
            else:
                current_iter = self.treestore.append(None, [path, False])
            self.add_to_tree(sub_paths, current_iter)

    def get_selected_filepaths(self):
        paths = self.dict_to_paths(self.paths_to_dict(self.enlighten_paths))
        is_selected = self.get_selected_items()
        selected_filepaths = [
            i for i, j in zip(paths, is_selected) if j if os.path.isfile(i)
        ]
        return selected_filepaths

    def current_dtime(self):
        return datetime.now().strftime("%y%d%m_%H%M%S")

    def merge_files(self, input_files, output_file):
        # full paths as column names
        if self.radio_left == 1:
            colnames = [f for f in input_files]
        # filenames (relative paths) as column names
        elif self.radio_left == 2:
            colnames = [
                f"{os.path.basename(f)} ({os.path.relpath(os.path.dirname(f), self.path)})"
                for f in input_files
            ]
        # only filenames as column names
        elif self.radio_left == 3:
            colnames = [os.path.basename(f) for f in input_files]

        if self.radio_right == 1:
            col = -1
            colnames.insert(0, "Raman_shift")
        elif self.radio_right == 2:
            col = -2
            colnames = [i for col in colnames for i in ("Raman_shift", col)]

        rows = []
        for i, filename in enumerate(input_files):
            with open(filename, "r") as f:
                csv_reader = csv.reader(f, delimiter=",")
                for row in csv_reader:
                    if "Pixel" in row:
                        break
                for j, row in enumerate(csv_reader):
                    if i == 0:
                        rows.append(row[-2:])
                    else:
                        rows[j].extend(row[col:])

        with open(output_file, "w") as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(colnames)
            csv_writer.writerows(rows)

    # On buttons click
    def on_open_btn_click(self, open_btn):
        dialog = Gtk.FileChooserDialog(
            title="Please select a directory",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.treestore.clear()
            self.path = dialog.get_filename()
            self.enlighten_paths = self.get_paths()
            self.paths_dict = self.paths_to_dict(self.enlighten_paths)
            self.add_to_tree(self.paths_dict)
            self.save_path = os.path.join(
                self.path, f"Spectra_{self.current_dtime()}.csv"
            )
            self.saveas_entry.set_text(self.save_path)
            self.saveas_entry.set_position(-1)
        elif response == Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()

    # def on_assemble_btn_click(self, assemble_btn):
    #     selection = self.listview.get_selection()
    #     selection.unselect_all()
    #     self.liststore.clear()
    #     self.populate_listview()
    #     self.total_n = len(self.get_list_items())
    #     self.total_n_label.set_text(str(self.total_n))

    def toggle_item(self, path, model):
        iter = model.get_iter(path)
        # print(path)
        value = self.treestore[iter][1]
        self.treestore.set_value(iter, 1, not value)

    def get_treepath(self, paths_dict, item_path_string):
        paths_dict["a_random_name_fkaklfgld"] = paths_dict.pop(self.path)
        paths_dict_list = self.dict_to_paths(paths_dict)

        item_path_dict = self.paths_to_dict([item_path_string])
        item_path_dict["a_random_name_fkaklfgld"] = item_path_dict.pop(self.path)
        item_path_list = self.dict_to_paths(item_path_dict)

        klist = []
        for i, ipath in enumerate(item_path_list):
            k = 0
            parent_path = "/".join(map(str, ipath.split("/")[:-1]))
            for path in paths_dict_list:
                if (parent_path in path) and (path.count("/") == i):
                    if path == ipath:
                        klist.append(str(k))
                        # print(klist)
                    k += 1

        paths_dict[self.path] = paths_dict.pop("a_random_name_fkaklfgld")

        treepath = ":".join(klist)
        return treepath

    def on_radio_left_toggle(self, button, name):
        self.radio_left = 2
        if button.get_active():
            # if name == 1:
            # print("1 was pressed")
            # elif name == 2:
            # print("2 was pressed")
            # else:
            # print("3 was pressed")
            self.radio_left = name

    def on_radio_right_toggle(self, button, name):
        if button.get_active():
            # if name == 1:
            #     print("1 was pressed")
            # else:
            #     print("2 was pressed")
            self.radio_right = name

    def on_save_btn_click(self, save_btn):
        # print("Save as was pressed.")
        dialog = Gtk.FileChooserDialog(
            title="Save File",
            parent=self,
            action=Gtk.FileChooserAction.SAVE,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK,
            Gtk.ResponseType.OK,
        )

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.save_path = dialog.get_filename()
            self.saveas_entry.set_text(os.path.join(self.save_path))
            self.saveas_entry.set_position(-1)
        elif response == Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()

    def on_merge_btn_click(self, merge_btn):
        if self.get_list_items():
            if os.path.exists(self.save_path):
                overwrite_dialog = OverwriteDialog(self, self.save_path)
                response = overwrite_dialog.run()
                overwrite_dialog.destroy()
                if response == Gtk.ResponseType.OK:
                    # print("Overwriting file")
                    self.merge_files(
                        self.get_list_items(),
                        self.save_path,
                    )
                elif response == Gtk.ResponseType.CANCEL:
                    # print("Cancelled")
                    pass
            else:
                self.merge_files(self.get_list_items(), self.save_path)


class OverwriteDialog(Gtk.Dialog):
    def __init__(self, parent, file_name):
        super().__init__(title="Overwrite file?", transient_for=parent, flags=0)
        self.set_default_size(300, 150)

        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK
        )

        label = Gtk.Label()
        label.set_label(
            f"This folder already contains a file named '{os.path.basename(file_name)}'.\nDo you want to overwrite it?"
        )

        box = self.get_content_area()
        box.set_border_width(5)
        box.add(label)
        self.show_all()


def main():
    main_window = MainWindow()
    main_window.connect("destroy", Gtk.main_quit)
    Gtk.main()


if __name__ == "__main__":
    main()
