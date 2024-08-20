from wall_tracker_mp.domain import WallProfile
from thewall.settings import LOG_DIR

import multiprocessing as mp
import queue
import logging
import time
import os
from collections import Counter


class DayEvent:
    def __init__(self, day):
        self.__day = day

    def day(self):
        return self.__day

    def __str__(self):
        return f'Day {self.__day}'


class NewSectionEvent:
    def __init__(self, section):
        section.set_busy()
        self.__section = section

    def section(self):
        return self.__section

    def __str__(self):
        return f'New section: [profile id: {self.__section.profile_id()}, section id: {self.__section.section_id()}]'


class WorkerReadyEvent:
    def __init__(self, worker_id, day, section=None):
        self.__worker_id = worker_id
        self.__section = section
        self.__day = day

    def workder_id(self):
        return self.__worker_id

    def section(self):
        return self.__section

    def day(self):
        return self.__day

    def __str__(self):
        return f'Worker is ready: [workder id: {self.__worker_id}, section done: {self.__section}, day: {self.__day}]'


class ExitEvent:
    def __str__(self):
        return 'Exit'


LOG_FORMAT = '[%(asctime)s]:%(levelname)-5s:: %(message)s -- {%(filename)s:%(lineno)d:(%(funcName)s)}'
LOG_FORMATTER = logging.Formatter(LOG_FORMAT)
LOG_LEVEL = logging.INFO


class Manager(mp.Process):
    def __init__(self, profiles, workers_num):
        if not profiles:
            raise ValueError('Empty profiles collection given')

        super().__init__()
        self.__profiles = { i: WallProfile(p, i) for i, p in enumerate(profiles, 1) }
        self.__workers_num = workers_num
        self.__output_queue = mp.Queue()
        logging.basicConfig(format=LOG_FORMAT)
        logger = self.__logger = logging.getLogger(Manager.__name__)
        logger.setLevel(LOG_LEVEL)
        handler = logging.FileHandler(LOG_DIR / 'manager.log')
        handler.setFormatter(LOG_FORMATTER)
        logger.addHandler(handler)


    def profiles(self):
        return self.__profiles


    def output_queue(self):
        return self.__output_queue


    def is_completed(self):
        profiles = self.__profiles
        return all(p.is_completed() for _, p in profiles.items())


    def run(self):
        logger = self.__logger
        profiles = self.__profiles
        oq = self.__workers_output = mp.Queue()
        workers = self.__workers = { i: Worker(i, mp.Queue(), oq) for i in range(self.__workers_num) }

        logger.info('Manager started')

        def get_available_section():
            for _, p in profiles.items():
                sect = p.get_available_section()
                if sect is not None:
                    return sect

            return None

        def send_event_to_all(event):
            for worker in started_workers:
                worker.send_event(event)

        def wait_all_exit():
            for worker in started_workers:
                worker.send_event(ExitEvent())
                worker.join()

        day = 1
        oq = self.__workers_output
        started_workers = list()

        for _, worker in workers.items():
            sect = get_available_section()
            if sect is not None:
                worker.send_event(NewSectionEvent(sect))
                worker.start()
                started_workers.append(worker)

        counter = Counter()
        send_event_to_all(DayEvent(day))
        day += 1

        while True:
            try:
                event = oq.get()

                sect = event.section()
                if sect is not None:
                    profiles[sect.profile_id()].sections()[sect.section_id()] = sect
                    sect = get_available_section()
                    if sect is not None:
                        workers[event.workder_id()].send_event(NewSectionEvent(sect))

                ready_day = event.day()
                counter[ready_day] += 1
                if counter[ready_day] == len(started_workers):
                    send_event_to_all(DayEvent(day))
                    day += 1

                if self.is_completed():
                    wait_all_exit()
                    self.__output_queue.put(profiles)
                    logger.info(f'The wall is built')
                    return
            except BaseException as e:
                logger.error(f'Unexpected error: [{e}]', exc_info=e)
                return


class Worker(mp.Process):
    def __init__(self, wid, input_queue, output_queue):
        super().__init__()
        self.__wid = wid
        self.__input = input_queue
        self.__output = output_queue


    def send_event(self, event):
        self.__input.put(event)


    def input_queue(self):
        return self.__input


    def output_queue(self):
        return self.__output


    def run(self):
        logging.basicConfig(format=LOG_FORMAT)
        logger = self.__logger = logging.getLogger(Worker.__name__)
        logger.setLevel(LOG_LEVEL)
        handler = logging.FileHandler(LOG_DIR / f'worker.{self.__wid}.log')
        handler.setFormatter(LOG_FORMATTER)
        logger.addHandler(handler)

        iq = self.__input
        oq = self.__output
        logger = self.__logger
        section = None
        logger.info('Worker started')
       
        while True:
            event = iq.get()
            logger.debug(f'Event: {event}, workder id: {self.__wid}')
            try:
                if isinstance(event, ExitEvent):
                    logger.info('Worker quit')
                    return
                if isinstance(event, NewSectionEvent):
                    section = event.section()
                    logger.debug(f'Pick up new section: [sect id: {section.section_id()}, profile id: {section.profile_id()}]')
                elif isinstance(event, DayEvent):
                    day = event.day()
                    if section is None:
                        logger.debug('No section available')
                        oq.put(WorkerReadyEvent(self.__wid, day))
                        continue

                    section.build_step(day)
                    if section.is_completed():
                        steps = section.steps()
                        section_id = section.section_id()
                        profile_id = section.profile_id()
                        logger.info(f'Section is ready: [{day=}, {profile_id=}, {section_id=}, {steps=}]')
                        oq.put(WorkerReadyEvent(self.__wid, day, section))
                        section = None
                        continue

                    oq.put(WorkerReadyEvent(self.__wid, day))
            except BaseException as e:
                logger.error(f'Unexpected error: [{e}]', exc_info=e)
                return
