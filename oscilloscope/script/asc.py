import numpy as np
import serial
import time

BAUD_RATE = 460800
INACTIVE, STARTED, FINISHED = 0, 1 ,2

# GUI class
class ASC:
    
    def __init__(self, port, dataset):
        # Serial interface
        self.port = port
        self.ds = dataset
        self.num_classes = len(dataset.class_labels)
        self.index = np.arange(self.num_classes)
        self.start_time = None
        self.activities = []
        self.life_log = []
        self.status = INACTIVE
        weighted = dataset.application['weight']
        self.weight = []
        for label in self.ds.class_labels:
            if label in weighted.keys():
                self.weight.append(weighted[label])
            else:
                self.weight.append(1)

    def _plot_stats(self, ax):
        ax.set_xticks(self.index)
        ax.set_xticklabels(self.ds.class_labels, rotation=65)
        ax.bar(self.index, self.stats)
        ax.set_ylabel('Counts')
        ax.set_title('Activities in my home')

    def _plot_life_log(self, ax, tick):
        print(len(tick), len(self.life_log))
        ax.step(tick, self.life_log, where='pre', marker='s')
        ax.set_yticks(self.index)
        ax.set_yticklabels(self.ds.class_labels, fontsize=12)
        ax.set_xlabel('Elapsed time (sec)')
        ax.grid()
        ax.set_title('Activities in my home')

    def plot(self, ax, cmd, measurement_time, num_section):
        '''
        Note: this function is stateless, and an instance of this object keeps the states.
        '''

        # Initalization for the first time
        if self.start_time is None or self.status == FINISHED:
            self.start_time = time.time()
            self.activities = []
            self.stats = np.zeros(self.num_classes)
            self.life_log = []
            self.status = STARTED

        # Read an inference result from the device
        with serial.Serial(self.port, BAUD_RATE, timeout=3) as ser:
            class_ = ser.readline().decode('ascii')
            class_ = int(class_)
            self.activities.append(class_)
            self.stats[class_] += 1
            print(class_)

        if cmd == 'stats':
            ax.clear()
            self._plot_stats(ax)

        # Split the activities data into chunks at a certain interval
        len_activities = len(self.activities)
        if (len_activities % num_section) == 0:
            num_records = int(len_activities / num_section)
            activities_reshaped = np.array(self.activities[:num_records * num_section], dtype=int).reshape(num_records, num_section)
            tick = np.linspace(0, time.time() - self.start_time, num_records+1)[1:]

            # Record a life log
            self.life_log = []
            for a_reshaped in activities_reshaped:
                stats_section = np.zeros(self.num_classes)
                for a in a_reshaped:
                    stats_section[a] += 1 * self.weight[a]
                self.life_log.append(np.argmax(stats_section))
            print(self.life_log)
            
            if cmd == 'life_log':
                ax.clear()
                self._plot_life_log(ax, tick)

        if (time.time() - self.start_time) > measurement_time:
            self.status = FINISHED
            return True   # Finished
        else:
            return False  # Continue