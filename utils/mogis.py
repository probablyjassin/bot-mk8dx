from utils.models import Mogi

mogi_registry = {}

def create_mogi(channel_id: int):
    if channel_id in mogi_registry:
        raise ValueError("Mogi with this ID already exists.")
    mogi_registry[channel_id] = Mogi(channel_id=channel_id)

def get_mogi(channel_id: int):
    if channel_id not in mogi_registry:
        return None
    return mogi_registry[channel_id]

def close_mogi(channel_id: int):
    if channel_id not in mogi_registry:
        raise ValueError("Mogi with this ID does not exist.")
    del mogi_registry[channel_id]