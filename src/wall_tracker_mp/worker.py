from wall_tracker_mp.domain import WallProfile
from thewall.settings import LOG_DIR

import multiprocessing as mp
import queue
import logging
import time
import os


class DayEvent:
    def __init__(self, day):
        self.__day = day

    def day(self):
        return self.__day

    def __str__(self):
        return f'Day {self.__day}'


class NewSectionEvent:
    def __init__(self, profile_id, section_id):
        self.__profile_id = profile_id
        self.__section_id = section_id

    def section_id(self):
        return self.__section_id

    def profile_id(self):
        return self.__profile_id

    def __str__(self):
        return f'New section: [profile id: {self.__profile_id}, section id: {self.__section_id}]'


class WorkerReadyEvent:
    def __init__(self, worker_id, section_ready, day):
        self.__worker_id = worker_id
        self.__section_ready = section_ready
        self.__day = day

    def workder_id(self):
        return self.__worker_id

    def section_ready(self):
        return self.__section_ready

    def __str__(self):
        return f'Worker is ready: [workder id: {self.__worker_id}, section done: {self.__section_ready}, day: {self.__day}]'


class ExitEvent:
    def __str__(self):
        return 'Exit'


LOG_FORMAT = '[%(asctime)s]:%(levelname)-5s:: %(message)s -- {%(filename)s:%(lineno)d:(%(funcName)s)}'
LOG_FORMATTER = logging.Formatter(LOG_FORMAT)


class Manager(mp.Process):
    def __init__(self, profiles, workers_num):
        if not profiles:
            raise ValueError('Empty profiles collection given')

        super().__init__()
        self.__profiles = { i: WallProfile(p, i) for i, p in enumerate(profiles, 1) }
        self.__workers_num = workers_num
        logging.basicConfig(format=LOG_FORMAT)
        logger = self.__logger = logging.getLogger(Manager.__name__)
        # logger.setLevel(os.environ.get('LOG_LEVEL', 'DEBUG'))
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(LOG_DIR / 'manager.log')
        handler.setFormatter(LOG_FORMATTER)
        logger.addHandler(handler)


    def profiles(self):
        return self.__profiles


    def is_completed(self):
        profiles = self.__profiles
        return all(p.is_completed() for _, p in profiles.items())


    def run(self):
        logger = self.__logger
        profiles = self.__profiles
        oq = self.__workers_output = mp.Queue()
        workers = self.__workers = { i: Worker(i, mp.Queue(), oq, profiles) for i in range(self.__workers_num) }

        logger.info('Manager started')

        def send_event_to_all(event):
            for wid, worker in workers.items():
                worker.send_event(event)

        def wait_all_exit():
            for wid, worker in workers.items():
                # for some reason join() blocks if process is already exited
                # it's seen in log that worker process function is finished
                # worker.join()
                # terminate sometimes doesn't make process exit
                # worker.terminate()
                # SIGKILL works always at least on linux
                worker.kill()

        for _, worker in workers.items():
            worker.start()

        day = 1
        oq = self.__workers_output

        while True:
            send_event_to_all(DayEvent(day))
            day += 1
            try:
                # don't wait for all workers, the first one that is ready triggers new day
                event = oq.get()
                if self.is_completed():
                    send_event_to_all(ExitEvent())
                    wait_all_exit()
                    logger.info(f'The wall is built')
                    return
            except BaseException as e:
                logger.debug(f'Unexpected error: [{e}]', exc_info=e)
                return


class Worker(mp.Process):
    def __init__(self, wid, input_queue, output_queue, profiles):
        super().__init__()
        self.__wid = wid
        self.__input = input_queue
        self.__output = output_queue
        self.__profiles = profiles


    def send_event(self, event):
        self.__input.put(event)


    def input_queue(self):
        return self.__input


    def output_queue(self):
        return self.__output


    def run(self):
        logging.basicConfig(format=LOG_FORMAT)
        logger = self.__logger = logging.getLogger(Worker.__name__)
        # logger.setLevel(os.environ.get('LOG_LEVEL', 'DEBUG'))
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(LOG_DIR / f'worker.{self.__wid}.log')
        handler.setFormatter(LOG_FORMATTER)
        logger.addHandler(handler)

        iq = self.__input
        oq = self.__output
        logger = self.__logger
        profiles = self.__profiles
        section = None
        logger.info('Worker started')

        def get_available_section():
            for _, p in profiles.items():
                sect = p.get_available_section()
                if sect is not None:
                    return sect

            return None
       
        def process_section(day):
            nonlocal section
            section.build_step(day)
            section_ready = section.is_completed()
            day = event.day()
            if section_ready:
                steps = section.steps()
                section_id = section.section_id()
                profile_id = section.profile_id()
                logger.info(f'Section is ready: [{day=}, {profile_id=}, {section_id=}, {steps=}]')
                section = None
            return section_ready

        while True:
            event = iq.get()
            logger.debug(f'Event: {event}, workder id: {self.__wid}')
            try:
                if isinstance(event, ExitEvent):
                    logger.info('Worker quit')
                    return
                elif isinstance(event, DayEvent):
                    day = event.day()
                    if section is None:
                        section = get_available_section()
                        if section is not None:
                            logger.debug(f'Pick up new section: [sect id: {section.section_id()}, profile id: {section.profile_id()}]')
                            section.set_busy()
                            section_ready = process_section(day)                            
                        else:
                            logger.info('Worker quit due to no section available')
                            return
                    else:
                        section_ready = process_section(day)

                    oq.put(WorkerReadyEvent(self.__wid, section_ready, day))
            except BaseException as e:
                logger.debug(f'Unexpected error: [{e}]', exc_info=e)
                return
