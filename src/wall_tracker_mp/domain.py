import multiprocessing as mp
import ctypes

from wall_tracker.models import MAX_WALL_HEIGHT


class WallSection:
    def __init__(self, initial_height, section_id, profile_id):
        assert initial_height <= MAX_WALL_HEIGHT
        size = MAX_WALL_HEIGHT - initial_height + 1
        self.__steps = [(0, initial_height)]
        self.__busy = False
        self.__sid = section_id
        self.__pid = profile_id


    def section_id(self):
        return self.__sid


    def profile_id(self):
        return self.__pid


    def set_busy(self):
        self.__busy = True


    def is_busy(self):
        return self.__busy


    def is_completed(self):
        return self.__steps[-1][1] == MAX_WALL_HEIGHT

    
    def build_step(self, day):
        if not self.is_completed():
            steps = self.__steps
            prev_step = len(steps) - 1
            steps.append((day, steps[prev_step][1] + 1))


    def steps(self):
        return list(self.__steps)


    def steps_num(self):
        return len(self.__steps) - 1


    def __len__(self):
        return self.steps_num()


class WallProfile:
    def __init__(self, sections, profile_id):
        self.__sections = list(WallSection(sect, i, profile_id) for i, sect in enumerate(sections))
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
