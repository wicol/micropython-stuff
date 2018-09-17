import utime


class Scheduler:
    def __init__(self, sleep_ms, tasks):
        self.sleep_ms = sleep_ms
        self.interval_tasks = tasks
        self.scheduled_tasks = []

    def run(self):
        while True:
            iteration_start = utime.ticks_ms()
            self.perform_tasks()
            time_spent_on_tasks = utime.ticks_diff(utime.ticks_ms(), iteration_start)
            if time_spent_on_tasks < self.sleep_ms:
                utime.sleep_ms(utime.ticks_diff(self.sleep_ms, time_spent_on_tasks))
            else:
                print('Skipping sleep - spent {}ms on tasks'.format(time_spent_on_tasks))

    def perform_tasks(self):
        for t in self.interval_tasks:
            now = utime.ticks_ms()
            if not t['last_called'] or \
                    utime.ticks_diff(now, t['last_called']) >= t['interval']:
                t['last_called'] = now
                t['callback']()

    def set_interval(self, callback, interval_ms):
        self.interval_tasks.append(
            {
                'callback': callback,
                'interval': interval_ms,
                'last_called': None
            }
        )
