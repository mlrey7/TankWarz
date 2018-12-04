import legume

UPDATES_PER_SECOND = 60
UPDATE_RATE = 1.0 / UPDATES_PER_SECOND

class TankCreate(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+1
    MessageValues = {
        'id' : 'int',
        'client_id' : 'int',
        'pos_x' : 'float',
        'pos_y' : 'float',
        'rot' : 'float',
        'l_vel_x' : 'float',
        'l_vel_y' : 'float',
        'a_vel' : 'float',
        'color' : 'int',
        'alive' : 'bool'}

class TankUpdate(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+2
    MessageValues = {
        'id' : 'int',
        'client_id' : 'int',
        'pos_x' : 'float',
        'pos_y' : 'float',
        'rot' : 'float',
        'l_vel_x' : 'float',
        'l_vel_y' : 'float',
        'a_vel' : 'float',
        'turret_rot' : 'float',
        'turret_vel' : 'float',
        'color' : 'int',
        'alive' : 'bool'}

class TankCommand(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+3
    MessageValues = {
        'id' : 'int',
        'command' : 'int'
    }

class FakeValues(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+80
    MessageValues = {
        'id' : 'int',
        'command' : 'int'
    }

class ProjectileCreate(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+4
    MessageValues = {
        'id' : 'int',
        'src_id' : 'int',
        'client_id' : 'int',
        'pos_x' : 'float',
        'pos_y' : 'float',
        'rot' : 'float',
        'type' : 'int',
        'color' : 'int'}

class ProjectileDestroy(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+55
    MessageValues = {
        'projectile_id' : 'int'}
class TankFire(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+50
    MessageValues = {
        'id' : 'int',
        'projectile_id' : 'int'}

class TankHit(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+53
    MessageValues = {
        'id' : 'int',
        'projectile_id' : 'int'}

class TankFireClient(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+51
    MessageValues = {
        'id' : 'int',
        'projectile_id' : 'int'}

class TankSwitchAmmo(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+56
    MessageValues = {
        'id' : 'int',
        'ammo_type' : 'int'}

class ProjectileUpdate(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+5
    MessageValues = {
        'id' : 'int',
        'src_id' : 'int',
        'client_id' : 'int',
        'pos_x' : 'float',
        'pos_y' : 'float',
        'rot' : 'float',
        'color' : 'int',
        'type' : 'int',
        'l_vel_x' : 'float',
        'l_vel_y' : 'float'}

class MapCreate(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+6
    MessageValues = {
        'l' : 'int',
        'w' : 'int',
        'seed_a' : 'int',
        'seed_b' : 'int'}
class GameOver(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+36
    MessageValues = {
        'winner_id' : 'int',
        'score' : 'int'}
class ClientStart(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+35
    MessageValues = {
        'client_id' : 'int'}    
class UpdateTime(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+37
    MessageValues = {
        'time' : 'string 10'}

legume.messages.message_factory.add(TankCreate)
legume.messages.message_factory.add(TankUpdate)
legume.messages.message_factory.add(TankCommand)
legume.messages.message_factory.add(ProjectileCreate)
legume.messages.message_factory.add(ProjectileUpdate)
legume.messages.message_factory.add(MapCreate)
legume.messages.message_factory.add(FakeValues)
legume.messages.message_factory.add(TankFire)
legume.messages.message_factory.add(TankFireClient)
legume.messages.message_factory.add(TankHit)
legume.messages.message_factory.add(ProjectileDestroy)
legume.messages.message_factory.add(TankSwitchAmmo)
legume.messages.message_factory.add(ClientStart)
legume.messages.message_factory.add(GameOver)
legume.messages.message_factory.add(UpdateTime)



