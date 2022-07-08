import abc


class AbstractDictionary(abc.ABC):
    @abc.abstractmethod
    def find_umamusume_name(self, kind: int) -> str:
        ...

    @abc.abstractmethod
    def find_unique_skill_name(self, kind: int) -> str:
        ...

    @abc.abstractmethod
    def find_umamusume_image_url(self, kind: int) -> str:
        ...


class FakeDictionary(AbstractDictionary):
    def find_umamusume_name(self, kind: int) -> str:
        return "라이스 샤워"

    def find_unique_skill_name(self, kind: int) -> str:
        return "블루 로즈 체이서"

    def find_umamusume_image_url(self, kind: int) -> str:
        return "https://w.namu.la/s/5f210caa3468b8fc0ed5ec34c0b03996ca89637f24ef9f0f0bbde2a43ab9848a1ae5a5b2758f7f9513ed5df1d4f783b7556d378c243dbc2a9272463d222fd70920b77763dca18351aa01330b28989becf2d28b12d98d2b02ddd0eead6989e40b7d016597228d6daf5c505ca9dbfaec5b"
