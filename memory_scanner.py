import ctypes
from time import sleep


from mem_edit import Process


from my_thread import MyThread




def getStruct(initial_value):
    class MyStruct(ctypes.Structure):
        _fields_ = [
            ('map_id', ctypes.c_int),
        ]

        def change_id(self, value):
            self.map_id = value

        def get_cvalue(self):
            return ctypes.c_int(self.map_id)

    s = MyStruct()
    s.map_id = initial_value
    return s




class MemoryScanner:
    def __init__(self, s, get_process_name, found_function, reset_function, update_adress_function, update_value_function):
        self.data = s
        self.addrs = []
        self.get_process_name = get_process_name
        self.th = None
        self.found_function = found_function
        self.reset_function = reset_function
        self.update_adress_function = update_adress_function
        self.update_value_function = update_value_function

    def hardcodingValue(self, value):
        self.addrs = [int(value, 0)]

    def set_memory_value(self, value):
        self.data.change_id(value)

    def searchFirstMap(self):
        with self.getProcess() as p:
            self.addrs = p.search_all_memory(self.data.get_cvalue())
        self.update_adress_function()

    def searchMapId(self):
        p = self.getProcess()
        with self.getProcess() as p:
            self.addrs = p.search_addresses(self.addrs, self.data.get_cvalue())

    def searchMapIdMultiple(self, num):
        # if (len(self.addrs) == 1):
        #    print(hex(self.addrs[0]))
        #    self.startSynchronising()
        if (len(self.addrs) == 0):
            self.searchFirstMap()
        else:
            for i in range(num):
                self.searchMapId()
            self.update_adress_function()
            if (len(self.addrs) == 1):
                # self.searchMapIdMultiple(1)
                print(hex(self.addrs[0]))
                self.startSynchronising()
        self.update_adress_function()

    def startSynchronising(self):
        self.stopSynchronising()
        self.th = MyThread(self.print_loop)
        self.th.start()
        self.found_function()

    def stopSynchronising(self):
        if (self.th):
            self.th.raise_exception()
            self.th = None
        self.reset_function()

    def resetSearch(self):
        self.stopSynchronising()
        self.addrs = []
        self.update_adress_function()

    def print_loop(self):
        with self.getProcess() as p:
            val = ctypes.c_int(99999)
            while len(self.addrs) == 1:
                prev = val.value
                p.read_memory(self.addrs[0], val)
                if (prev != val.value):
                    self.update_value_function(val.value)
                sleep(1)


    def getProcess(self):
        process_name = self.get_process_name()
        pid = Process.get_pid_by_name(process_name)
        p = Process.open_process(pid)
        return p
