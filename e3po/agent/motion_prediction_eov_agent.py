from e3po.agent.motion_prediction_agent import MotionPredictionAgent


class MotionPredictionEOVAgent(MotionPredictionAgent):
    def __init__(self):
        super().__init__()
        self.extra_fov_range = 20
        self.eov = [self.eov[0] + self.extra_fov_range, self.eov[1] + self.extra_fov_range]
