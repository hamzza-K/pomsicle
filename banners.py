"""
This module provides utility classes for generating colored terminal messages
and creating terminal banners for process events. The `Colors` class contains
various predefined colors using the `colorama` library, and the `Banner` class
allows the user to create custom terminal banners with formatted and colored
output.

Classes:
    Colors: Provides ANSI color codes for terminal text using `colorama`.
    Banner: Provides methods for creating colored terminal banners for displaying
            process information.
"""

import colorama
from typing import Tuple
import shutil

colorama.init()

class Colors:
    """
    A class that defines color constants using the `colorama` library for terminal
    text formatting.

    Attributes:
        black (str): ANSI code for black text.
        red (str): ANSI code for red text.
        green (str): ANSI code for green text.
        yellow (str): ANSI code for yellow text.
        blue (str): ANSI code for blue text.
        magenta (str): ANSI code for magenta text.
        cyan (str): ANSI code for cyan text.
        white (str): ANSI code for white text.
        reset (str): ANSI code to reset text formatting to default.

    Methods:
        get_color(func_name: str) -> str:
            Returns the color associated with a given function name.
    """
    black   = colorama.Fore.BLACK
    red     = colorama.Fore.RED
    green   = colorama.Fore.GREEN
    yellow  = colorama.Fore.YELLOW
    blue    = colorama.Fore.BLUE
    magenta = colorama.Fore.MAGENTA
    cyan    = colorama.Fore.CYAN
    white   = colorama.Fore.WHITE
    reset   = colorama.Style.RESET_ALL

    @staticmethod
    def get_color(func_name: str) -> str:
        """
        Returns the color associated with a given function name based on the
        registered methods in the `Banner` class. If no color is registered, 
        defaults to white.

        Args:
            func_name (str): The name of the function to retrieve the color for.

        Returns:
            str: The ANSI color code for the specified function.
        """
        if func_name in Banner._registered_methods:
            return Banner._registered_methods[func_name]['color']
        if func_name == 'success':
            return Colors.green
        elif func_name == 'error':
            return Colors.red
        elif func_name == 'info':
            return Colors.yellow
        else:
            return Colors.white


class Banner:
    """
    A class that provides methods for creating simple, colored terminal banners
    to point out the events of your processes.

    Attributes:
        style (str): The character used for creating the banner lines (default is '-').
        _registered_methods (dict): A dictionary storing registered methods with their
                                    corresponding color and message.

    Methods:
        _fill_term(message: str) -> Tuple[str, str]:
            Returns the terminal-size-adjusted banner lines and formatted message.
        _format(func: function) -> function:
            A decorator that wraps the banner methods to format and print messages
            with banner lines.
        register(func_name: str, color: str, message: str):
            Registers a custom banner function with a specified color and message.
        success(message: str='SUCCESS') -> str:
            Displays a success banner with the given message.
        error(message: str='ERROR') -> str:
            Displays an error banner with the given message.
        info(message: str='INFO') -> str:
            Displays an info banner with the given message.
    """
    _registered_methods = {}

    def __init__(self, style: str = '-'):
        """
        Initializes a Banner instance.

        Args:
            style (str): The character used for creating banner lines (default is '-').
        """
        self.style = style

    def _fill_term(self, message: str) -> Tuple[str, str]:
        """
        Calculates the terminal width and fills the banner line with the `style` character
        while centering the given message.

        Args:
            message (str): The message to be displayed in the banner.

        Returns:
            Tuple[str, str]: The line string filled with `style` characters and the centered
                             message string.
        """
        term_size = shutil.get_terminal_size((80, 20)).columns
        style_count = (term_size - len(message))
        formatted_msg = message.center(style_count, ' ')
        lines = self.style * style_count
        return lines, formatted_msg

    def _format(func):
        """
        A decorator that formats the banner output by adding lines and colors to the
        message.

        Args:
            func (function): The function to be wrapped by the decorator.

        Returns:
            function: A wrapper function that prints the formatted banner with colors
                      and lines.
        """
        def wrapper(self, message: str = None):
            if message is None:
                message = func.__name__.upper()
            color = Colors.get_color(func.__name__)
            lines, msg = self._fill_term(message=message)
            formatted_lines = f'{color}{lines}{Colors.reset}'
            formatted_msg = f'{color}{msg}{Colors.reset}'
            print(f'{formatted_lines}\n{formatted_msg}\n{formatted_lines}')
        return wrapper

    # def register(self, func_name: str, color: str, message: str):
    #     """
    #     Registers a custom banner method with a specific name, color, and message.
    #     This allows the user to define and reuse custom banners.

    #     Args:
    #         func_name (str): The name of the custom banner method to be registered.
    #         color (str): The color to be used for the banner.
    #         message (str): The default message to be displayed by the custom banner method.
    #     """
    #     if not hasattr(Colors, color):
    #         color = Colors.white
    #     print('The color is', getattr(Colors, color) + 'abc' + Colors.reset)
    #     Banner._registered_methods[func_name] = {
    #         'color': color,
    #         'message': message
    #     }

    #     def registered_func(self, message=None):
    #         if message is None:
    #             message = message or Banner._registered_methods[func_name]['message']
    #         color = getattr(Colors, (Colors.get_color(func_name=func_name)))
    #         lines, msg = self._fill_term(message=message)
    #         formatted_lines = f'{color}{lines}{Colors.reset}'
    #         formatted_msg = f'{color}{msg}{Colors.reset}'
    #         print(f'{formatted_lines}\n{formatted_msg}\n{formatted_lines}')
    #     setattr(Banner, func_name, Banner._format(registered_func))

    @_format
    def success(self, message='SUCCESS'):
        """
        Displays a success banner with the default or specified message.

        Args:
            message (str, optional): The message to display (default is 'SUCCESS').
        
        Returns:
            str: The success message.
        """
        return message

    @_format
    def error(self, message='ERROR'):
        """
        Displays an error banner with the default or specified message.

        Args:
            message (str, optional): The message to display (default is 'ERROR').
        
        Returns:
            str: The error message.
        """
        return message
    
    @_format
    def info(self, message='INFO'):
        """
        Displays an info banner with the default or specified message.

        Args:
            message (str, optional): The message to display (default is 'INFO').
        
        Returns:
            str: The info message.
        """
        return message

