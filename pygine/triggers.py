from enum import IntEnum
from pygine.base import PygineObject
from pygine.draw import draw_rectangle
from pygine.entities import Direction, Player
from pygine.input import pressed, InputType


class Trigger(PygineObject):
    def __init__(self, x, y, width, height, end_location, next_scene):
        super(Trigger, self).__init__(x, y, width, height)
        self.next_scene = next_scene
        self.end_location = end_location

    def _queue_next_scene(self, manager):
        manager.queue_next_scene(self.next_scene)

    def _move_entity_to_next_scene(self, entity, manager):
        next_scene = manager.get_scene(self.next_scene)
        current_scene = manager.get_current_scene()

        if isinstance(entity, Player):
            self._queue_next_scene(manager)
            next_scene.relay_actor(entity)
        else:
            next_scene.relay_entity(entity)

        current_scene.entities.remove(entity)
        entity.set_location(self.end_location.x, self.end_location.y)

    def update(self, delta_time, scene_data, manager):
        raise NotImplementedError(
            "A class that inherits Trigger did not implement the update(delta_time, scene_data, manager) method")

    def draw(self, surface, camera_type):
        raise NotImplementedError(
            "A class that inherits Trigger did not implement the draw(surface, camera_type) method")


class CollisionTrigger(Trigger):
    def __init__(self, x, y, width, height, end_location, next_scene, direction=Direction.UP):
        super(CollisionTrigger, self).__init__(
            x, y, width, height, end_location, next_scene)
        self.direction = direction
        self.query_result = None

    def __collision(self, scene_data, manager):
        self.query_result = scene_data.entity_quad_tree.query(self.bounds)
        for e in self.query_result:
            if e.bounds.colliderect(self.bounds):
                self._move_entity_to_next_scene(e, manager)

    def update(self, delta_time, scene_data, manager):
        self.__collision(scene_data, manager)

    def draw(self, surface, camera_type):
        draw_rectangle(
            surface,
            self.bounds,
            camera_type
        )


class OnButtonPressTrigger(Trigger):
    def __init__(self, button, end_location, next_scene):
        super(OnButtonPressTrigger, self).__init__(
            0, 0, 1, 1, end_location, next_scene)
        self.button = button

    def update(self, delta_time, scene_data, manager):
        if pressed(self.button):
            self._queue_next_scene(manager)

            if scene_data.actor != None:
                self._move_entity_to_next_scene(scene_data.actor, manager)

    def draw(self, surface, camera_type):
        draw_rectangle(
            surface,
            self.bounds,
            camera_type
        )