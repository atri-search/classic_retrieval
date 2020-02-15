import os
import abc

SUPPORTED_EXTENSIONS = ['.txt', '.pdf']
TEMP_SUFFIX = "_temp.txt"


class ExtensionNotSupported(RuntimeError):
    ...


def get_extension(filename: str) -> str:
    extension = -1
    return os.path.splitext(filename)[extension]


def get_base_name(filename: str) -> str:
    basename = 0
    return os.path.splitext(filename)[basename]


def get_file(file_path: str) -> "AbstractFile":
    extension = get_extension(file_path)

    if extension not in SUPPORTED_EXTENSIONS:
        raise ExtensionNotSupported(f"{extension} is not supported.")

    if extension == '.txt':
        return Txt(file_path)
    elif extension == '.pdf':
        return Pdf(file_path)


class AbstractFile(abc.ABC):

    @abc.abstractmethod
    def open(self):
        """
        Define the mode to open the file based in its extension.
        :return: text file object
        """
        ...

    @abc.abstractmethod
    def close(self) -> None:
        """
            Just close the file on a security way.
        :return: None
        """
        ...


class Txt(AbstractFile):

    def __init__(self, file_path):
        self._file_path = file_path
        self._file = None

    def open(self):
        self._file = open(self._file_path, mode='r', encoding='utf-8')
        return self._file

    def close(self):
        self._file.close()


class Pdf(AbstractFile):

    def __init__(self, file_path):
        self._file_path = file_path
        self._file = None

    def open(self):
        from .Cast import convert_pdf_to_txt
        text = convert_pdf_to_txt(self._file_path)
        self._file = open(get_base_name(self._file_path) + TEMP_SUFFIX, mode='w+', encoding='utf-8')
        self._file.write(text)
        self._file.seek(0)
        return self._file

    def close(self):
        file_path = self._file.name
        self._file.close()
        os.remove(file_path)


