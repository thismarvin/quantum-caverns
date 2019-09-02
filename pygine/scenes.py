import pygame
from enum import IntEnum
from pygame import Rect
from pygine.entities import *
from pygine.input import InputType, pressed
from pygine.maths import Vector2
from pygine.structures import Quadtree, Bin
from pygine.transitions import Pinhole, TransitionType
from pygine.utilities import Camera
from random import randint


class SceneType(IntEnum):
    TOPDOWN = 0
    FLOCKING = 1


class SceneManager:
    def __init__(self):
        self.__reset()

    def get_scene(self, scene_type):
        return self.__all_scenes[int(scene_type)]

    def get_current_scene(self):
        return self.__current_scene

    def queue_next_scene(self, scene_type):
        self.__previous_scene = self.__current_scene
        self.__next_scene = self.__all_scenes[int(scene_type)]
        self.__setup_transition()

    def __reset(self):
        self.__all_scenes = []
        self.__current_scene = None
        self.__previous_scene = None
        self.__next_scene = None
        self.leave_transition = None
        self.enter_transition = None
        self.start_transition = False

        self.__initialize_scenes()
        self.__set_starting_scene(SceneType.FLOCKING)

    def __add_scene(self, scene):
        self.__all_scenes.append(scene)
        scene.manager = self

    def __initialize_scenes(self):
        self.__all_scenes = []
        self.__add_scene(TopDown())
        self.__add_scene(Flocking())

    def __set_starting_scene(self, starting_scene_type):
        assert (len(self.__all_scenes) > 0), \
            "It looks like you never initialized all the scenes! Make sure to setup and call __initialize_scenes()"

        self.__current_scene = self.__all_scenes[int(starting_scene_type)]

    def __setup_transition(self):
        if self.__previous_scene.leave_transition_type == TransitionType.PINHOLE_CLOSE:
            self.leave_transition = Pinhole(TransitionType.PINHOLE_CLOSE)

        if self.__next_scene.enter_transition_type == TransitionType.PINHOLE_OPEN:
            self.enter_transition = Pinhole(TransitionType.PINHOLE_OPEN)

        self.start_transition = True

    def __change_scenes(self):
        self.__current_scene = self.__next_scene

    def __update_input(self, delta_time):
        if pressed(InputType.RESET):
            self.__reset()

    def __update_transition(self, delta_time):
        if self.start_transition:
            self.leave_transition.update(delta_time)
            if self.leave_transition.done:
                self.enter_transition.update(delta_time)
                self.__change_scenes()

    def update(self, delta_time):
        assert (self.__current_scene != None), \
            "It looks like you never set a starting scene! Make sure to call __set_starting_scene(starting_scene_type)"

        self.__update_input(delta_time)
        self.__update_transition(delta_time)
        self.__current_scene.update(delta_time)

    def __draw_transitions(self, surface):
        if self.start_transition:
            if self.leave_transition != None and not self.leave_transition.done:
                self.leave_transition.draw(surface)
                if self.leave_transition.done:
                    self.enter_transition.draw(surface)
            else:
                self.enter_transition.draw(surface)

    def draw(self, surface):
        assert (self.__current_scene != None), \
            "It looks like you never set a starting scene! Make sure to call __set_starting_scene(starting_scene_type)"

        self.__current_scene.draw(surface)
        self.__draw_transitions(surface)


class SceneDataRelay(object):
    def __init__(self):
        self.scene_bounds = None
        self.entities = None
        self.entity_quad_tree = None
        self.entity_bin = None

    def set_scene_bounds(self, bounds):
        self.scene_bounds = bounds

    def update(self, entites, entity_quad_tree, entity_bin):
        self.entities = entites
        self.entity_quad_tree = entity_quad_tree
        self.entity_bin = entity_bin


class Scene(object):
    VIEWPORT_BUFFER = 32

    def __init__(self):
        self.scene_bounds = Rect(
            0,
            0,
            Camera.BOUNDS.width,
            Camera.BOUNDS.height
        )

        self.camera = Camera()
        self.camera_location = Vector2(0, 0)
        self.camera_viewport = Rectangle(
            -Scene.VIEWPORT_BUFFER,
            -Scene.VIEWPORT_BUFFER,
            Camera.BOUNDS.width + Scene.VIEWPORT_BUFFER * 2,
            Camera.BOUNDS.height + Scene.VIEWPORT_BUFFER * 2,
            Color.RED,
            2
        )

        self.entities = []
        self.sprites = []
        self.shapes = []
        self.triggers = []

        self.sprite_quad_tree = Quadtree(self.scene_bounds, 4)
        self.shape_quad_tree = Quadtree(self.scene_bounds, 4)
        self.entity_quad_tree = Quadtree(self.scene_bounds, 4)
        self.entity_bin = Bin(self.scene_bounds, 4)
        self.query_result = None
        self.first_pass = True
        self.entities_are_uniform = False
        self.optimal_bin_size = 0

        self.leave_transition_type = TransitionType.PINHOLE_CLOSE
        self.enter_transition_type = TransitionType.PINHOLE_OPEN
        self.manager = None
        self.actor = None

        self.scene_data = SceneDataRelay()
        self.scene_data.set_scene_bounds(self.scene_bounds)

    def setup(self, entities_are_uniform, maximum_entity_dimension = 0):
        self.entities_are_uniform = entities_are_uniform
        if self.entities_are_uniform:
            self.optimal_bin_size = int(math.ceil(math.log(2, maximum_entity_dimension)))

        self._reset()
        self._create_triggers()

    def set_scene_bounds(self, bounds):
        self.scene_bounds = bounds
        self.scene_data.set_scene_bounds(self.scene_bounds)

        buffer = 8
        modified_bounds = Rect(
            -buffer,
            -buffer,
            self.scene_bounds.width + buffer * 2,
            self.scene_bounds.height + buffer * 2,
        )

        self.sprite_quad_tree = Quadtree(modified_bounds, 4)
        self.shape_quad_tree = Quadtree(modified_bounds, 4)
        self.entity_quad_tree = Quadtree(modified_bounds, 4)
        self.entity_bin = Bin(modified_bounds, 5)
        self.first_pass = True

    def relay_actor(self, actor):
        if actor != None:
            self.actor = actor
            self.entities.append(self.actor)

    def relay_entity(self, entity):
        self.entities.append(entity)
        # We can potentially add aditional logic for certain entites. For example, if the entity is a NPC then spawn it at (x, y)

    def _reset(self):
        raise NotImplementedError(
            "A class that inherits Scene did not implement the reset() method")

    def _create_triggers(self):
        raise NotImplementedError(
            "A class that inherits Scene did not implement the create_triggers() method")

    def __update_spatial_partitioning(self):
        if self.first_pass:
            self.sprite_quad_tree.clear()
            for i in range(len(self.sprites)):
                self.sprite_quad_tree.insert(self.sprites[i])

            self.shape_quad_tree.clear()
            for i in range(len(self.shapes)):
                self.shape_quad_tree.insert(self.shapes[i])
            self.first_pass = False

        self.entity_quad_tree.clear()
        if self.entities_are_uniform:
            self.entity_bin.clear()
        for i in range(len(self.entities)):
            self.entity_quad_tree.insert(self.entities[i])
            if self.entities_are_uniform:
                self.entity_bin.insert(self.entities[i])

    def __update_entities(self, delta_time):
        for i in range(len(self.entities)-1, -1, -1):
            self.entities[i].update(delta_time, self.scene_data)
        #self.entities.sort(key=lambda e: 1000 * (e.y + e.height) - e.x)

    def __update_triggers(self, delta_time):
        for t in self.triggers:
            t.update(delta_time, self.entities, self.manager)

    def __update_camera(self):
        if self.actor != None:
            self.camera_location = Vector2(
                self.actor.x + self.actor.width / 2 - self.camera.BOUNDS.width / 2,
                self.actor.y + self.actor.height / 2 - self.camera.BOUNDS.height / 2
            )

        self.camera.update(self.camera_location, self.scene_bounds)
        self.camera_viewport.set_location(
            self.camera.get_viewport_top_left().x - Scene.VIEWPORT_BUFFER,
            self.camera.get_viewport_top_left().y - Scene.VIEWPORT_BUFFER)

    def update(self, delta_time):
        self.__update_spatial_partitioning()
        self.scene_data.update(
            self.entities,
            self.entity_quad_tree,
            self.entity_bin
        )
        self.__update_entities(delta_time)
        self.__update_triggers(delta_time)
        self.__update_camera()

    def draw(self, surface):
        self.query_result = self.shape_quad_tree.query(
            self.camera_viewport.bounds)
        for s in self.query_result:
            s.draw(surface, CameraType.DYNAMIC)

        self.query_result = self.sprite_quad_tree.query(
            self.camera_viewport.bounds)
        for s in self.query_result:
            s.draw(surface, CameraType.DYNAMIC)

        if globals.debugging:
            for t in self.triggers:
                t.draw(surface, CameraType.DYNAMIC)

        self.query_result = self.entity_quad_tree.query(self.camera_viewport.bounds)
        self.query_result.sort(key=lambda e: 1000 * (e.y + e.height) - e.x)
        for e in self.query_result:
            e.draw(surface)

class TopDown(Scene):
    def __init__(self):
        super(TopDown, self).__init__()
        self.setup(False)   
        self.relay_actor(Player(self.scene_bounds.width / 2, self.scene_bounds.height / 2)) 

    def _reset(self):
        self.set_scene_bounds(
            Rect(0, 0, Camera.BOUNDS.width * 2, Camera.BOUNDS.height))

        self.entities = []
        for y in range(int(math.ceil(self.scene_bounds.height / 8))):
            for x in range(int(math.ceil(self.scene_bounds.width / 52))):
                if randint(1, 10) <= 1:
                    self.entities.append(Block(x * 52, y * 8))

        self.sprites = []
        for y in range(int(math.ceil(self.scene_bounds.height / 32))):
            for x in range(int(math.ceil(self.scene_bounds.width / 32))):
                if randint(1, 10) <= 3:
                    self.sprites.append(Sprite(x * 32, y * 32 - 8, SpriteType.TILE))

        self.shapes = []
        self.shapes.append(
            Rectangle(
                0,
                0,
                self.scene_bounds.width,
                self.scene_bounds.height,
                Color.TEAL
            )
        )

    def _create_triggers(self):
        self.triggers = []


class Flocking(Scene):
    def __init__(self):
        super(Flocking, self).__init__()
        self.setup(True, 16)  

    def _reset(self):
        self.set_scene_bounds(
            Rect(0, 0, Camera.BOUNDS.width, Camera.BOUNDS.height))
        self.entities = []

        for i in range(0, 100):
            self.entities.append(
                Boid(randint(8, self.scene_bounds.width), randint(8, self.scene_bounds.height)))

        self.shapes = []
        self.shapes.append(Rectangle(
            0, 0, self.scene_bounds.width, self.scene_bounds.height, Color.BLACK))

    def _create_triggers(self):
        self.triggers = []
