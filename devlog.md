# The Importance of Delta Time (Part 4)

## Tying it all together

In order to implement delta time into our method properly we need to use an *integrator*.  

An integrator allows us to step through time very slowing and approximate physics. One of the most common approaches for game development is using [Euler's Method](https://en.wikipedia.org/wiki/Euler_method). (If you're interested in other methods then check out [Verlet Integration](https://en.wikipedia.org/wiki/Verlet_integration) and the [Runge-Kutta method](https://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods)).

Explaining exactly why Euler's method works is outside of the scope of this explanation, but at the end of the day implementing Euler's method in code is actually really easy! The new update method would look like this.

```python
def update(delta_time):
    if pressed(JUMP_BUTTON):
        velocity.y = -jump_velocity

    location.y += velocity.y * delta_time
    velocity.y += gravity * delta_time
```

We simply rearranged the location and velocity lines and multiplied each of them by delta time. Now the player jumps consistently across different frame rates!

This is great, but what if we want to have more control of our jump code. For example, what if we want the player to jump *n* amount of pixels high in *k* amount of time? Well now that we are using an integrator we are actually simulating real-world physics, and we can use fundamental kinematic equations to achieve this.

 So we want to manually specify a `jump_height` and `jump_duration` variable in our code. For this example let's have the player jump 32 pixels high in 1 second. We also need to calculate what value `gravity` and `jump_velocity` must be to reflect the `jump_height` and `jump_duration` variables.

First we can solve for gravity by using this kinematic equation for a free falling object.

![find_gravity|690x393,75%](upload://sauLGMcOX5t6V0BiFZ1GJCkLKiv.png)

Now that we found gravity we can use another kinematic equation to find what the initial jump velocity should be.
![find_jump_velocity|690x264,75%](upload://wfbKkiEFV6hsa7yoYQvFOYYdJhV.png)
That wasn't too bad. Here is what our new initialize method looks like.

```python
def initialize():
    jump_height = 32
    jump_duration = 1

    gravity = 2 * jump_height / (jump_duration * jump_duration)
    jump_velocity = gravity * jump_duration
    velocity = Vector2(0, 0)
    location = Vector2(0, 0)
```

We can check if all this is correct by graphing out our acceleration, velocity, and position functions. We can do some quick calculus to find these functions given a constant acceleration.
![find_methods|630x500](upload://mqhgW8X4bia99JVUA1V9Re39h2.png)
Now we can visualze these functions and see if manipulating jump height and jump duration works as intended.

![final_physics|690x431,100%](upload://Ak78ugY2mfNcMlOMYMDrGmmqnd6.gif)
(The sliders j and d represent jump height and jump duration respectively).

Well looks like everything works! Here is what our final code looks like.

```python
def initialize():
    jump_height = 32
    jump_duration = 1

    gravity = 2 * jump_height / (jump_duration * jump_duration)
    jump_velocity = gravity * jump_duration
    velocity = Vector2(0, 0)
    location = Vector2(0, 0)

def update(delta_time):
    if pressed(JUMP_BUTTON):
        velocity.y = -jump_velocity

    location.y += velocity.y * delta_time
    velocity.y += gravity * delta_time
```
