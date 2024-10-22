from utils.models.mogi import Mogi

mogi_registry = {}

def create_mogi(channel_id: int) -> None:
    if channel_id in mogi_registry:
        raise ValueError("Mogi with this ID already exists.")
    mogi_registry[channel_id] = Mogi(channel_id=channel_id)

def get_mogi(channel_id: int) -> Mogi | None:
   return mogi_registry.get(channel_id, None)

def destroy_mogi(channel_id: int) -> None:
    if channel_id not in mogi_registry:
        raise ValueError("Mogi with this ID does not exist.")
    del mogi_registry[channel_id]