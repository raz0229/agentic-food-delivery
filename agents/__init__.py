from .simple_reflex import SimpleReflexAgent
from .model_based import ModelBasedReflexAgent
from .goal_based import GoalBasedAgent
from .utility_based import UtilityBasedAgent
from .learning import LearningAgent
from .hierarchical import HierarchicalAgent
from .contextual import ContextualAgent


def all_agents():
    return [
        SimpleReflexAgent(),
        ModelBasedReflexAgent(),
        GoalBasedAgent(),
        UtilityBasedAgent(),
        LearningAgent(),
        HierarchicalAgent(),
        ContextualAgent(),
    ]
