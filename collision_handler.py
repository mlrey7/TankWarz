import pymunk
import legume
from constants import Coll_Type
from shared import TankHit
from shared import ProjectileDestroy

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
                    projectile.destroy()
                    projectiles.pop(projectile.idn)
                    tank.hit(projectile.damage)
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


class Server_Collision_Handler:
    def initialize_handler(space, tanks, projectiles, server):
        projectile_tank_handler = space.add_collision_handler(Coll_Type.TANK, Coll_Type.PROJECTILE)
        projectile_environment_handler = space.add_collision_handler(Coll_Type.ENVIRONMENT, Coll_Type.PROJECTILE)

        def begin(arbiter, space, data):
            tankShape = arbiter.shapes[0]
            projectileShape = arbiter.shapes[1]
            tank = tanks[tankShape.idn]
            if projectiles.get(projectileShape.idn) is not None:
                projectile = projectiles[projectileShape.idn]
                if projectile.src_idn != tank.idn:
                    projectile.destroy()
                    projectiles.pop(projectile.idn)
                    tank.hit(projectile.damage)
                    msg = TankHit()
                    msg.id.value = tank.idn
                    msg.projectile_id.value = projectile.idn
                    server.send_reliable_message_to_all(msg)
            return True

        def beginP(arbiter, space, data):
            projectileShape = arbiter.shapes[1]
            if projectiles.get(projectileShape.idn) is not None:
                projectile = projectiles[projectileShape.idn]
                projectile.destroy()
                projectiles.pop(projectile.idn)
                msg = ProjectileDestroy()
                msg.projectile_id.value = projectileShape.idn
                server.send_reliable_message_to_all(msg)
            return True
        
        projectile_environment_handler.begin = beginP
        projectile_tank_handler.begin = begin