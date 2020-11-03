import threading

from scrappybara.utils.mutables import divide_list


class _Thread(threading.Thread):

    def __init__(self, thread_id, input_items, process):
        threading.Thread.__init__(self)
        self.__thread_id = thread_id
        self.__input_items = input_items
        self.__process = process
        self.output_items = []

    def run(self):
        if isinstance(self.__input_items[0], tuple):
            self.output_items = [self.__process(*item) for item in self.__input_items]
        else:
            self.output_items = [self.__process(item) for item in self.__input_items]


def run_multithreads(items, process, nb_threads):
    """Items can be packs of arguments (a tuple), or a single var"""
    items_lists = divide_list(items, nb_threads)
    nb_threads = []
    output_items = []
    for idx, items_list in enumerate(items_lists):
        nb_threads.append(_Thread(idx, items_list, process))
        nb_threads[idx].start()
    for idx, _ in enumerate(items_lists):
        nb_threads[idx].join()
        output_items.extend(nb_threads[idx].output_items)
    return output_items
