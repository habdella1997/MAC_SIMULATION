# timer.py

import time

class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""

class Timer:
    timer_pause_total = 0
    time_pause_start = 0
    time_pasue_stop  = 0 

    def __init__(self):
        self._start_time = None
        self.timer_status = None

    def start(self):
        """Start a new timer"""
        if self._start_time is not None:
            raise TimerError(f"Timer is running. Use .stop() to stop it")
        self._start_time = time.perf_counter()
        self.timer_status = "running"
        return self._start_time
    
    def elapsed_time(self):
        return int((time.perf_counter() - self._start_time - Timer.timer_pause_total) / 1e-3)
    
    def pause_time(self):
        if(self.timer_status == "running"):
            self.timer_status = "pause"
            Timer.time_pause_start = time.perf_counter()
        else:
            raise TimerError(f"A Timer Pause Action is invalid Since Timmer is not running")
    
    def continue_time(self):
        if(self.timer_status == "pause"):
            self.timer_status = "running"
            Timer.time_pause_stop = time.perf_counter()
            Timer.timer_pause_total = ((Timer.time_pause_stop - Timer.time_pause_start))
            

    def stop(self):
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start() to start it")

        elapsed_time = time.perf_counter() - self._start_time
        elapsed_time = int(elapsed_time / 1e-3)
        self._start_time = None
        print(f"Elapsed time: {elapsed_time} [ms]")