#!/usr/bin/env python
#   pipescaler/processors/gigapixel_ai_processor.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Upscales image using [Gigapixel AI](https://www.topazlabs.com/gigapixel-ai)"""
from __future__ import annotations

from os import system
from os.path import basename, dirname, splitext
from typing import Any, Optional

from PIL import Image

from pipescaler.common import validate_executable
from pipescaler.core import Processor, validate_image

if system() == "Windows":
    from pywinauto.application import (
        Application,
        ProcessNotFoundError,
        WindowSpecification,
    )
else:
    Application = None
    ProcessNotFoundError = None
    WindowSpecification = None


class GigapixelAiProcessor(Processor):
    """Upscales image using [Gigapixel AI](https://www.topazlabs.com/gigapixel-ai)"""

    def __init__(
        self,
        command: Optional[
            str
        ] = "C:\Program Files\Topaz Labs LLC\Topaz Gigapixel AI\Topaz Gigapixel AI.exe",
        match_input_mode: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        Validate and store configuration

        Arguments:
            command: Path to Gigapixel AI executable
            match_input_mode: Ensure output image mode matches input image mode
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.command = command
        self.match_input_mode = match_input_mode
        self._application = None
        self._window = None

    def __call__(self, infile: str, outfile: str) -> None:
        """
        Read image from infile, process it, and save to outfile

        Arguments:
            infile: Input file path
            outfile: Output file path
        """
        command = validate_executable(self.command, {"Windows"})

        input_image = validate_image(infile, ["L", "LA", "RGB", "RGBA"])

        # Launch application
        # TODO: Streamline window selection using regex
        self.window = self.application.window(best_match="Topaz Gigapixel AI")

        # Load image
        self.click_button(self.window.BrowseButton)
        self.complete_open_file_dialog(self.window.OpenImagesDialog, infile)
        self.window = self.application.window(
            best_match=f"{basename(infile)} - Topaz Gigapixel AI"
        )

        # TODO: Configure scale
        # TODO: Configure model

        # Save image
        self.window = self.application.window(
            best_match=f"{basename(infile)} - Topaz Gigapixel AI"
        )
        self.click_button(self.window.SaveImageButton)
        self.window.Edit4.set_text(splitext(basename(outfile))[0])  # Set outfile name
        # TODO: Check if directory actually needs to be changed
        self.click_button(self.window.ChangeButton)  # Set outfile directory
        self.complete_select_folder_dialog(
            self.window.SelectOutputFolderDialog, dirname(outfile)
        )
        self.click_button(self.window.SaveButton)
        self.window = self.application.window(
            best_match="Processing Complete - Topaz Gigapixel AI"
        )

        # Close image
        self.click_button(self.window.Pane0.Button2)
        self.window = self.application.window(best_match="Topaz Gigapixel AI")

        # Convert output image format, if necessary
        output_image = Image.open(outfile)
        if output_image.mode != input_image.mode:
            output_image = output_image.convert(input_image.mode)
            output_image.save(outfile)

        # Close application
        # TODO: Decide what to do here
        # self.close_application()

    @property
    def application(self) -> Application:
        """Gigapixel AI application"""
        if self._application is None:
            try:
                self._application = Application(backend="uia").connect(
                    path=self.command
                )
            except ProcessNotFoundError:
                self._application = Application(backend="uia").start(self.command)
        return self._application

    @property
    def window(self) -> WindowSpecification:
        """Gigapixel AI window"""
        return self._window

    @window.setter
    def window(self, value: WindowSpecification) -> None:
        self._window = value

    def click_button(self, button: WindowSpecification) -> None:
        """
        Click a provided button; uses click_input rather than click, which doesn't
        seem to work for this application

        Arguments:
            button: Button to click
        """
        self.window.set_focus()
        rectangle = button.rectangle()
        coords = (
            rectangle.left + (rectangle.right - rectangle.left) // 2,
            rectangle.top + (rectangle.bottom - rectangle.top) // 2,
        )
        button.click_input(coords=coords, absolute=True)

    def close_application(self) -> None:
        """Click 'X' to close application"""
        self.click_button(self.window.TitleBar.CloseButton)
        self._application = None

    def complete_open_file_dialog(
        self, dialog: WindowSpecification, filename: str
    ) -> None:
        """
        Completes an open file dialog with a provided filename

        Arguments:
            dialog: Open file dialog to complete
            filename: Filename with which to complete open file dialog
        """
        dialog.FileNameComboBox.Edit.set_text(filename)
        dialog.OpenButton3.click()

    def complete_select_folder_dialog(
        self, dialog: WindowSpecification, directory: str
    ) -> None:
        """
        Completes a select folder dialog

        Arguments:
            dialog: Select folder dialog to complete
            directory: Directory which which to complete select folder dialog
        """
        dialog.FolderEdit.set_text(directory)
        dialog.SelectFolderButton.click()


if __name__ == "__main__":
    GigapixelAiProcessor.main()
