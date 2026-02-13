from strategy.VAAC_strategy import VAACStrategy


class VAACEStrategy(VAACStrategy):
    def __init__(self):
        super().__init__()
        self.extra_fov_range = 10
        self.eov = [self.eov[0] + self.extra_fov_range, self.eov[1] + self.extra_fov_range]
