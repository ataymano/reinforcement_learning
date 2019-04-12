import os
import glob
import datetime

class cache_provider:
    def __init__(self, folder):
        self.folder = folder

    def get(self):
        pattern=os.path.join(self.folder, '*.cache')
        return sorted(list(glob.glob(pattern)))

class LogsExtractor:
    @staticmethod
    def _get_log_relative_path(date):
        return 'data/%s/%s/%s_0.json' % (
            str(date.year),
            str(date.month).zfill(2),
            str(date.day).zfill(2)
        )

    @staticmethod
    def iterate_files(folder, start_date, end_date):
        for i in range((end_date - start_date).days + 1):
            current_date = start_date + datetime.timedelta(i)
            log_relative_path = LogsExtractor._get_log_relative_path(
                current_date
            )
            log_path = os.path.join(folder, log_relative_path)
            if os.path.isfile(log_path):
                yield log_path
        return
        yield

class ps_logs_provider:
    def __init__(self, folder, start, end):
        self.folder = folder
        self.start = start
        self.end = end

    def get(self):
        return list(LogsExtractor.iterate_files(self.folder, self.start, self.end))