import pymunk
from constants import Coll_Type

class Collision_Handler:
    def initialize_handler(space, tanks, projectiles):
        projectile_tank_handler = space.add_collision_handler(Coll_Type.TANK, Coll_Type.PROJECTILE)
        projectile_environment_handler = space.add_collision_handler(Coll_Type.ENVIRONMENT, Coll_Type.PROJECTILE)

        def begin(arbiter, space, data):
            tankShape = arbiter.shapes[0]
            projectileShape = arbiter.shapes[1]
            tank = tanks[tankShape.idn]
            if projectiles.get(projectileShape.idn) is not None:
                projectile = projectiles[projectileShape.idn]
                if projectile.src_idn != tank.idn:
                    print(projectile.src_idn)
                    tank.hp -= projectile.damage
                    projectile.destroy()
                    projectiles.pop(projectile.idn)
                    if tank.hp <= 0 and tank.alive:
                        tank.body.velocity = 0,0
                        tank.body.angular_velocity = 0
                        tank.destroy()
                    else:
                        tank.hit()
            return True

        def beginP(arbiter, space, data):
            projectileShape = arbiter.shapes[1]
            if projectiles.get(projectileShape.idn) is not None:
                projectile = projectiles[projectileShape.idn]
                projectile.destroy()
                projectiles.pop(projectile.idn)
            return True
        
        projectile_environment_handler.begin = beginP
        projectile_tank_handler.begin = begin