class ColorManager:
    def __init__(self):
        self.basic_color = {
            "red": "\033[31m", "yellow": "\033[33m", "green": "\033[32m", "blue": "\033[34m",
            "magenta": "\033[35m", "cyan": "\033[36m", "white": "\033[37m", "black": "\033[30m"
        }

        self.highlight_color = {
            "bright_black": "\033[90m", "gray": "\033[90m", "bright_red": "\033[91m",
            "bright_green": "\033[92m", "bright_yellow": "\033[93m", "bright_blue": "\033[94m",
            "bright_magenta": "\033[95m", "bright_cyan": "\033[96m", "bright_white": "\033[97m"
        }

        self.background_basic_color = {
            "black": "\033[40m", "red": "\033[41m", "green": "\033[42m", "yellow": "\033[43m",
            "blue": "\033[44m", "magenta": "\033[45m", "cyan": "\033[46m", "white": "\033[47m"
        }

        self.background_highlight_color = {
            "bright_black": "\033[100m", "bright_red": "\033[101m", "bright_green": "\033[102m",
            "bright_yellow": "\033[103m", "bright_blue": "\033[104m", "bright_magenta": "\033[105m",
            "bright_cyan": "\033[106m", "bright_white": "\033[107m"
        }

        # 0 => reset, 1 => bold, 2 => underline, 3 => reverse
        self.basic_text_style = {
            0: "\033[0m", 1: "\033[1m", 2: "\033[4m", 3: "\033[7m",
        }

    def color(self, msg: str, color: str, background: str = None):
        use_background = False
        text = f"{self.basic_text_style[1]}{msg}{self.basic_text_style[0]}"

        if background is not None:
            use_background = True

        if color.isspace() or not color:
            errmsg = "No color was specified."
            raise ValueError(errmsg)

        if color.isdigit():
            errmsg = f"{color} is a integer, not a color. "
            raise ValueError(errmsg)

        if color not in (self.basic_color | self.highlight_color):
            errmsg = f"Unsupported color {color}."
            raise ValueError(errmsg)

        if use_background:
            if background == color:
                errmsg = "You cannot use the same color twice between the text and the background."
                raise ValueError(errmsg)

            if background.isspace() or not background:
                errmsg = "No background color was specified."
                raise ValueError(errmsg)

            if background.isdigit():
                errmsg = f"{background} is a integer, not a color. "
                raise ValueError(errmsg)

            if background not in (self.background_basic_color | self.background_highlight_color):
                errmsg = f"Unsupported background color {background}."
                raise ValueError(errmsg)

            if background in self.background_basic_color:
                text = self.background_basic_color[background] + text
            elif background in self.background_highlight_color:
                text = self.background_highlight_color[background] + text

        if color in self.basic_color:
            text = self.basic_color[color] + text
        elif color in self.highlight_color:
            text = self.highlight_color[color] + text

        return text


if __name__ == "__main__":
    color_manager = ColorManager()
    print(color_manager.color(msg="Hello!", color="green", background="green"))
