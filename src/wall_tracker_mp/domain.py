import multiprocessing as mp
import ctypes

from wall_tracker.models import MAX_WALL_HEIGHT


class WallSection:
    def __init__(self, initial_height, section_id, profile_id):
        # self.__initial_height = initial_height
        assert initial_height <= MAX_WALL_HEIGHT
        self.__size = MAX_WALL_HEIGHT - initial_height + 1
        self.__steps = mp.Array(ctypes.c_uint8, self.__size)
        self.__days = mp.Array(ctypes.c_uint16, self.__size)
        self.__index = mp.Value(ctypes.c_uint8, 1)
        self.__steps[0] = initial_height
        self.__busy = mp.Value(ctypes.c_uint8, 0)
        self.__sid = section_id
        self.__pid = profile_id


    def section_id(self):
        return self.__sid


    def profile_id(self):
        return self.__pid


    def set_busy(self):
        with self.__busy.get_lock():
            self.__busy.value = 1


    def is_busy(self):
        with self.__busy.get_lock():
            return bool(self.__busy.value)


    def is_completed(self):
        steps = self.__steps
        with steps.get_lock():
            return steps[-1] == MAX_WALL_HEIGHT

    
    def build_step(self, day):
        index = self.__index        
        steps = self.__steps
        days = self.__days

        if not self.is_completed():
            with steps.get_lock():
                if index.value >= len(steps):
                    return

                steps[index.value] = steps[index.value - 1] + 1
                days[index.value] = day
                index.value += 1


    def steps(self):
        return list(self.__steps)


    def steps_num(self):
        return len(self.__steps) - 1


    def days(self):
        return list(self.__days)


    def __len__(self):
        return self.steps_num()


class WallProfile:
    def __init__(self, sections, profile_id):
        self.__sections = tuple(WallSection(sect, i, profile_id) for i, sect in enumerate(sections))
        self.__profile_id = profile_id


    def profile_id(self):
        return self.__profile_id


    def sections(self):
        return self.__sections


    def sections_num(self):
        return len(self.__sections)


    def __len__(self):
        return self.sections_num()


    def is_completed(self):
        return all(s.is_completed() for s in self.__sections)


    def get_available_section(self):
        for sect in self.__sections:
            if not sect.is_busy():
                return sect

        return None


    def get_uncompleted_section(self):
        for sect in self.__sections:
            if not sect.is_completed():
                return sect

        return None
