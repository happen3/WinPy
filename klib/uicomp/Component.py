from klib.uicomp.DrawWindow import *


class Component:
    def __init__(self, class_name, window_name, style, x, y, width, height, parent, instance):
        self.hwnd = user32.CreateWindowExW(
            0,
            to_lpcwstr(class_name),
            to_lpcwstr(window_name),
            style,
            x,
            y,
            width,
            height,
            parent,
            None,
            instance,
            None
        )
        if not self.hwnd:
            raise ctypes.WinError()

    def show(self):
        user32.ShowWindow(self.hwnd, 5)  # SW_SHOW
        user32.UpdateWindow(self.hwnd)


class Button(Component):
    def __init__(self, window_name, x, y, width, height, parent, instance):
        super().__init__(
            class_name="BUTTON",
            window_name=window_name,
            style=0x50010000,  # WS_VISIBLE | WS_CHILD | BS_PUSHBUTTON
            x=x,
            y=y,
            width=width,
            height=height,
            parent=parent,
            instance=instance
        )


class TextBox(Component):
    def __init__(self, window_name, x, y, width, height, parent, instance):
        super().__init__(
            class_name="EDIT",
            window_name=window_name,
            style=0x50010080,  # WS_VISIBLE | WS_CHILD | WS_BORDER
            x=x,
            y=y,
            width=width,
            height=height,
            parent=parent,
            instance=instance
        )


class CbBox(Component):
    def __init__(self, window_name, x, y, width, height, parent, instance):
        super().__init__(
            class_name="COMBOBOX",
            window_name=window_name,
            style=0x50010080,  # WS_VISIBLE | WS_CHILD | CBS_DROPDOWN
            x=x,
            y=y,
            width=width,
            height=height,
            parent=parent,
            instance=instance
        )


class StaticText(Component):
    def __init__(self, window_name, x, y, width, height, parent, instance):
        super().__init__(
            class_name="STATIC",
            window_name=window_name,
            style=0x50000000,  # WS_VISIBLE | WS_CHILD | SS_LEFT
            x=x,
            y=y,
            width=width,
            height=height,
            parent=parent,
            instance=instance
        )


class CheckBox(Component):
    def __init__(self, window_name, x, y, width, height, parent, instance):
        super().__init__(
            class_name="BUTTON",
            window_name=window_name,
            style=0x50000000 | 0x00000002,  # WS_VISIBLE | WS_CHILD | BS_CHECKBOX
            x=x,
            y=y,
            width=width,
            height=height,
            parent=parent,
            instance=instance
        )


class RadioButton(Component):
    def __init__(self, window_name, x, y, width, height, parent, instance):
        super().__init__(
            class_name="BUTTON",
            window_name=window_name,
            style=0x50000000 | 0x00000004,  # WS_VISIBLE | WS_CHILD | BS_RADIOBUTTON
            x=x,
            y=y,
            width=width,
            height=height,
            parent=parent,
            instance=instance
        )


class ListBox(Component):
    def __init__(self, window_name, x, y, width, height, parent, instance):
        super().__init__(
            class_name="LISTBOX",
            window_name=window_name,
            style=0x50010000,  # WS_VISIBLE | WS_CHILD | LBS_STANDARD
            x=x,
            y=y,
            width=width,
            height=height,
            parent=parent,
            instance=instance
        )


class GroupBox(Component):
    def __init__(self, window_name, x, y, width, height, parent, instance):
        super().__init__(
            class_name="BUTTON",
            window_name=window_name,
            style=0x50000000 | 0x00000008,  # WS_VISIBLE | WS_CHILD | BS_GROUPBOX
            x=x,
            y=y,
            width=width,
            height=height,
            parent=parent,
            instance=instance
        )
