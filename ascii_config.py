import configparser
import json
import os

from asciimatics.widgets import Frame, TextBox, Layout, Label, Divider, Text, \
    CheckBox, RadioButtons, Button, PopUpDialog, TimePicker, DatePicker, Background, DropdownList, PopupMenu, ListBox
from asciimatics.event import MouseEvent
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication, InvalidFields
import sys
import re
import datetime


from config import cfc_general, cfg_network, cfg_loguru, cfg_debug, cfg_ftpcred, cfg_configinit, cfg_pyupdater

net_host, net_port = cfg_network()
ttac_usr, ttac_mas, ttac_rec, ttac_int = cfc_general()
logger_l = cfg_loguru()
debug_on = cfg_debug()
ftp_send, ftp_addr, ftp_user, ftp_pass, ftp_sess = cfg_ftpcred()
pyu_uchn, pyu_schn = cfg_pyupdater()
init_run = cfg_configinit()

# Initial data for the form
form_data = {
    "net_host": net_host,
    "net_port": net_port,
    "ttac_usr": ttac_usr,
    "ttac_mas": ttac_mas,
    "ttac_rec": ttac_rec,
    "ttac_int": ttac_int,
    "logger_l": logger_l,
    "debug_on": json.dumps(debug_on).capitalize(),
    "ftp_send": json.dumps(ftp_send).capitalize(),
    "ftp_addr": ftp_addr,
    "ftp_user": ftp_user,
    "ftp_pass": ftp_pass,
    "ftp_sess": ftp_sess,
    "pyu_uchn": pyu_uchn,
    "pyu_schn": json.dumps(pyu_schn).capitalize(),
    "init_run": "False",
}


class DemoFrame(Frame):
    def __init__(self, screen):
        # super(DemoFrame, self).__init__(screen, screen.height, screen.width, hover_focus=True, has_border=False,
        #                                 data=form_data)
        super(DemoFrame, self).__init__(screen, int(screen.height * 2 // 3), int(screen.width * 2 // 3),
                                        data=form_data, has_shadow=True, name="My Form", hover_focus=True, has_border=False)
        layout = Layout([1, 18, 1, 1])
        self.add_layout(layout)
        self.set_theme("bright")
        self._reset_button = Button("Reset", self._reset)
        layout.add_widget(Text(label="net_host:", name="net_host", on_change=self._on_change, validator=r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$|^localhost$"), 1)
        layout.add_widget(Text(label="net_port:", name="net_port", on_change=self._on_change, validator="^[0-9]{4,5}$"), 1)
        layout.add_widget(Text(label="ttac_usr:", name="ttac_usr", on_change=self._on_change, validator="^[a-zA-Z0-9\\-\\_]{4,16}$", max_length=16), 1)
        layout.add_widget(Text(label="ttac_mas:", name="ttac_mas", on_change=self._on_change), 1)
        layout.add_widget(Text(label="ttac_rec:", name="ttac_rec", on_change=self._on_change), 1)
        layout.add_widget(Text(label="ttac_int:", name="ttac_int", on_change=self._on_change), 1)
        layout.add_widget(Text(label="debug_on:", name="debug_on", on_change=self._on_change, validator="^True$|^False$"), 1)
        # layout.add_widget(ListBox(height=4, options=[("INFO", 1), ("DEBUG", 2), ("WARNING", 3), ("CRITICAL", 4)], label="logger_l", name="logger_l", on_change=self._on_change), 1)
        # layout.add_widget(RadioButtons(label="idk", name="idk", options=[("True", 1), ("False", 2)], on_change=self._on_change), 1)
        layout.add_widget(Text(label="logger_l:", name="logger_l", on_change=self._on_change, validator="^INFO$|^DEBUG$|^WARNING$|^CRITICAL$"), 1)
        layout.add_widget(Text(label="ftp_send:", name="ftp_send", on_change=self._on_change, validator="^True$|^False$"), 1)
        layout.add_widget(Text(label="ftp_addr:", name="ftp_addr", on_change=self._on_change), 1)
        layout.add_widget(Text(label="ftp_user:", name="ftp_user", on_change=self._on_change), 1)
        layout.add_widget(Text(label="ftp_pass:", name="ftp_pass", on_change=self._on_change, hide_char="*"), 1)
        layout.add_widget(Text(label="ftp_sess:", name="ftp_sess", on_change=self._on_change), 1)
        layout.add_widget(Text(label="pyu_uchn:", name="pyu_uchn", on_change=self._on_change, validator="^alpha|^beta$|^stable$"), 1)
        layout.add_widget(Text(label="pyu_schn:", name="pyu_schn", on_change=self._on_change, validator="^True$|^False$"), 1)
        layout.add_widget(Text(label="init_run:", name="init_run", on_change=self._on_change, validator="^True$|^False$"), 1)
        layout2 = Layout([10, 10, 10, 10])
        self.add_layout(layout2)
        layout2.add_widget(self._reset_button, 0)
        layout2.add_widget(Button("Help", self._help), 1)
        layout2.add_widget(Button("Save", self._save), 2)
        layout2.add_widget(Button("Quit", self._quit), 3)
        self.fix()

    def process_event(self, event):
        # Handle dynamic pop-ups now.
        if (event is not None and isinstance(event, MouseEvent) and
                event.buttons == MouseEvent.DOUBLE_CLICK):
            # By processing the double-click before Frame handling, we have absolute coordinates.
            options = [
                ("Default", self._set_default),
                ("Green", self._set_green),
                ("Monochrome", self._set_mono),
                ("Bright", self._set_bright),
            ]
            if self.screen.colours >= 256:
                options.append(("Red/white", self._set_tlj))
            self._scene.add_effect(PopupMenu(self.screen, options, event.x, event.y))
            event = None

        # Pass any other event on to the Frame and contained widgets.
        return super(DemoFrame, self).process_event(event)

    def _set_default(self):
        self.set_theme("default")

    def _set_green(self):
        self.set_theme("green")

    def _set_mono(self):
        self.set_theme("monochrome")

    def _set_bright(self):
        self.set_theme("bright")

    def _set_tlj(self):
        self.set_theme("tlj256")

    def _on_change(self):
        changed = False
        self.save()
        for key, value in self.data.items():
            if key not in form_data or form_data[key] != value:
                changed = True
                break
        self._reset_button.disabled = not changed

    def _reset(self):
        self.reset()
        raise NextScene()

    def _help(self):
        message = "net_host: Change if telemetry originates from source other than this machine (PS4, XBO, 2nd PC)*. \n"
        message += "net_port: This likely will never change, but the option was provided (HOSTSFILE, PORTFORWARDING). \n"
        message += "ttac_usr: This is the name that your object will display in tacview. (Best to keep it your Alias. \n"
        message += "ttac_mas: Session leader, starts the synced recorder for multiple clients. (MATCH IN-GAME NAME)*. \n"
        message += "ttac_rec: Command issued by leader to start synced recordings. This must match the session hosts. \n"
        message += "ttac_int: Timeout adjustment. Will affect the time between each frame (data snapshot).            \n"
        message += "debug_on: Force start recordings of online matches. Test flights automatically start recording.   \n"
        message += "logger_l: Logging level displayed to stdout. Partially Implemented. (INFO|DEBUG|WARNING|CRITICAL) \n"
        message += "ftp_send: Enable or disable automatic FTP submission post-flight (soon to be deprecated).         \n"
        message += "ftp_addr: Address of automatic FTP submission                                                     \n"
        message += "ftp_user: Username for automatic FTP submission                                                   \n"
        message += "ftp_pass: Password for automatic FTP submission                                                   \n"
        message += "ftp_sess: Subfolder in remote FTP directory (used to isolate sessions)                            \n"
        message += "pyu_uchn: Automatic updates channel that you will recieve (alpha|beta|stable)                     \n"
        message += "pyu_schn: Strict channel (stay only on set channel)                                               \n"
        message += "init_run: True on first run only. This configuration dialog will not be shown after*              \n"
        message += "\n\n"
        message += "*ThunderTac runs on laptop or 2nd PC recording data from a PS4, XBO, or a second computer*        \n"
        message += "*Must match session host, case sensitive. (NO SQUADRON TAGS!)*                                    \n"
        message += "*thundertac -c to call this dialog in the future, or simply run the configuration shortcut*       \n"

        self._scene.add_effect(
            PopUpDialog(self._screen, message, ["OK"]))

    def _save(self):
        # Build result of this form and display it.
        try:
            self.save(validate=True)
            message = "  Values entered are:  \n\n"
            passed = True
            for key, value in self.data.items():
                if key == "ftp_pass":
                    message += "  - {} : PASS : {}  \n".format(key, "*" * len(value))
                else:
                    message += "  - {} : PASS : {}  \n".format(key, value)
        except InvalidFields as exc:
            message = "  The following fields are invalid:  \n\n"
            for field in exc.fields:
                message += "  - {}  \n".format(field)
                passed = False
        if passed:
            config_file = "config.ini"
            config_root = f"{os.environ['LOCALAPPDATA']}\\WarThunderApps\\ThunderTac"
            config_path = f"{config_root}\\{config_file}"
            config = configparser.ConfigParser()
            config.read(config_path)
            for key, value in self.data.items():
                if key in ["net_host", "net_port"]:
                    config['network'][key] = value
                elif key in ["ttac_usr", "ttac_mas", "ttac_rec", "ttac_int"]:
                    config['general'][key] = value
                elif key in ["logger_l"]:
                    config['loguru'][key] = value
                elif key in ["debug_on"]:
                    config['debug'][key] = value
                elif key in ["ftp_send", "ftp_addr", "ftp_user", "ftp_pass", "ftp_sess"]:
                    config['ftpcred'][key] = value
                elif key in ["pyu_uchn", "pyu_schn"]:
                    config['pyupdater'][key] = value
                elif key in ["init_run"]:
                    config['configinit'][key] = value
                with open(config_path, 'w') as f:
                    config.write(f)

            # config['network']['net_host'] = net_host
            # config['network']['net_port'] = net_port
            # config['general']['ttac_usr'] = str(ttac_usr)
            # config['general']['ttac_mas'] = ttac_mas
            # config['general']['ttac_rec'] = ttac_rec
            # config['general']['ttac_int'] = ttac_int
            # config['loguru']['logger_l'] = logger_l
            # config['debug']['debug_on'] = str(debug_on)
            # config['ftpcred']['ftp_send'] = str(ftp_send)
            # config['ftpcred']['ftp_addr'] = ftp_addr
            # config['ftpcred']['ftp_user'] = ftp_user
            # config['ftpcred']['ftp_pass'] = ftp_pass
            # config['ftpcred']['ftp_sess'] = ftp_sess
            # config['pyupdater']['pyu_uchn'] = pyu_uchn
            # config['pyupdater']['pyu_schn'] = str(pyu_schn)
            # config['configinit']['init_run'] = str(init_run)
            # with open(config_path, 'w') as f:
            #     config.write(f)
        self._scene.add_effect(
            PopUpDialog(self._screen, message, ["OK"]))


    def _quit(self):
        self._scene.add_effect(
            PopUpDialog(self._screen,
                        "Are you sure?",
                        ["Yes", "No"],
                        has_shadow=True,
                        on_close=self._quit_on_yes))

    @staticmethod
    def _check_email(value):
        m = re.match(r"^[a-zA-Z0-9_\-.]+@[a-zA-Z0-9_\-.]+\.[a-zA-Z0-9_\-.]+$",
                     value)
        return len(value) == 0 or m is not None

    @staticmethod
    def _quit_on_yes(selected):
        # Yes is the first button
        if selected == 0:
            raise StopApplication("User requested exit")



def demo(screen, scene):
    screen.play([Scene([
        Background(screen),
        DemoFrame(screen)
    ], -1)], stop_on_resize=True, start_scene=scene, allow_int=True)


last_scene = None
while True:
    try:
        Screen.wrapper(demo, catch_interrupt=False, arguments=[last_scene])
        sys.exit(0)
    except ResizeScreenError as e:
        last_scene = e.scene




#     def process_event(self, event):
#         # Handle dynamic pop-ups now.
#         if (event is not None and isinstance(event, MouseEvent) and
#                 event.buttons == MouseEvent.DOUBLE_CLICK):
#             # By processing the double-click before Frame handling, we have absolute coordinates.
#             options = [
#                 ("Default", self._set_default),
#                 ("Green", self._set_green),
#                 ("Monochrome", self._set_mono),
#                 ("Bright", self._set_bright),
#             ]
#             if self.screen.colours >= 256:
#                 options.append(("Red/white", self._set_tlj))
#             self._scene.add_effect(PopupMenu(self.screen, options, event.x, event.y))
#             event = None
#
#         # Pass any other event on to the Frame and contained widgets.
#         return super(DemoFrame, self).process_event(event)
#
#     def _set_default(self):
#         self.set_theme("default")
#
#     def _set_green(self):
#         self.set_theme("green")
#
#     def _set_mono(self):
#         self.set_theme("monochrome")
#
#     def _set_bright(self):
#         self.set_theme("bright")
#
#     def _set_tlj(self):
#         self.set_theme("tlj256")
#
#     def _on_change(self):
#         changed = False
#         self.save()
#         for key, value in self.data.items():
#             if key not in form_data or form_data[key] != value:
#                 changed = True
#                 break
#         self._reset_button.disabled = not changed
#
#     def _reset(self):
#         self.reset()
#         raise NextScene()
#
#     def _verify(self):
#         you_shall_not_pass = True
#         try:
#             self.save(validate=True)
#             you_shall_not_pass = False
#         except InvalidFields as exc:
#             message = "The following fields are invalid:  \n\n"
#             note = ""
#             for field in exc.fields:
#                 message += "  - {}\n".format(field)
#                 if field == "net_host":
#                     message += "   VALID:     Valid Intranet IP Address  \n"
#                     message += "   EX(s):     127.0.0.1, localhost, see *  \n"
#                     note += "  * PS4 \\ XB0:     Get IP Address from your network settings in the console menu.  \n" \
#                             "                   99% of the time will look something like '192.168.1.xxx'  \n" \
#                             "                   There are instructions provided in the readme.  \n"
#                 elif field == "net_port":
#                     message += "   VALID:     Valid Port  \n"
#                     message += "   EX(s):     8111, 42069, 1337  \n"
#                 elif field == "ttac_usr":
#                     message += "   VALID:     Valid WarThunder Alias  \n"
#                     message += "   EX(s):     CleanUpOnIL2, Enola_Straight, hairypaulsack  \n"
#                 elif field == "logger_l":
#                     message += "   VALID:     Any Valid Python Logging logger_l  \n"
#                     message += "   EX(s):     INFO, DEBUG ,WARNING, CRITICAL  \n"
#             self._scene.add_effect(
#                 PopUpDialog(self._screen,
#                             message + '\n\n\n' + note,
#                             ["Okay"],
#                             has_shadow=True))
#             you_shall_not_pass = True
#         finally:
#             return you_shall_not_pass
#
#         # try:
#         #     self.save(validate=True)
#         #     message = "Entry Validation:  \n\n"
#         #     for key, value in self.data.items():
#         #         if key == "ftp_pass":
#         #             message += "  - {}: {}  \n".format(key, "*" * len(value))
#         #         else:
#         #             message += "  - {}: {}  \n".format(key, "PASS")
#         # except InvalidFields as exc:
#         #     message = "The following fields are invalid:  \n\n"
#         #     for field in exc.fields:
#         #         message += "  - {}  \n".format(field)
#         # self._scene.add_effect(
#         #     PopUpDialog(self._screen, message, ["OK"]))
#
#     def _quit(self):
#         bad_entry = self._verify()
#         if not bad_entry:
#             self._scene.add_effect(
#                 PopUpDialog(self._screen,
#                             "Are you sure?",
#                             ["Yes", "No"],
#                             has_shadow=True))
#         else:
#             self._scene.add_effect(
#                 PopUpDialog(self._screen,
#                             "Are you sure?",
#                             ["Yes", "No"],
#                             has_shadow=True))
#
#     def _ttac(self):
#         bad_entry = self._verify()
#         if not bad_entry:
#             self._scene.add_effect(
#                 PopUpDialog(self._screen,
#                             "Are you sure?",
#                             ["Yes", "No"],
#                             has_shadow=True,
#                             on_close=self._proceed_to_ttac))
#
#     @staticmethod
#     def _proceed_to_ttac():
#         pass
#
#     @staticmethod
#     def _quit_on_yes(selected):
#         # Yes is the first button
#         if selected == 0:
#             pass
#             raise StopApplication("User requested exit")
#
#
# def demo(screen, scene):
#     screen.play([Scene([
#         Background(screen),
#         DemoFrame(screen)
#     ], -1)], stop_on_resize=True, start_scene=scene, allow_int=True)
#
#
# last_scene = None
# while True:
#     try:
#         Screen.wrapper(demo, catch_interrupt=False, arguments=[last_scene])
#         sys.exit(0)
#     except ResizeScreenError as e:
#         last_scene = e.scene
