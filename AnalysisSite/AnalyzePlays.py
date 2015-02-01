class List_plays:
    '''
    This class stores and sorts objects of the Play class so that they can be efficiently accessed for processing.
    Overall list consisting of three separate lists each of which stores multiple instances of the Play class.
    '''

    def __init__(self):
        self.first_down = [[],[],[],[],[],[],[],[],[],[]]
        self.second_down = [[],[],[],[],[],[],[],[],[],[]]
        self.third_down = [[],[],[],[],[],[],[],[],[],[]]
        self.plays_array = [self.first_down,self.second_down,self.third_down]
        self.number_plays = 0

    def __getnewargs__(self):
        return ()

    def add_play(self,play):
        down = play.start_down
        to_go = play.distance_to_first
        self.plays_array[down-1][min(play.distance_to_first-1,9)].append(play)

    def retrieve_plays(self,down,yards):
        return self.plays_array[down-1][min(yards-1,9)]
