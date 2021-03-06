from sc2.bot_ai import BotAI #parent ai class that you'll inherit from
from sc2.data import Difficulty, Race
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2 import maps
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
import random
import asyncio
import os

os.environ["SC2PATH"] = "E:\Program Files (x86)\StarCraft II"

class Node:
    def __init__(self, data):
        self.data = data
        self.inc = []
        self.out = []

    def connect_dir(self, inc, out):
        if inc:
            for node in inc:
                if not node in self.inc:
                    self.inc.append(node)
                if not self in node.out:
                    node.out.append(self)

        if out:
            for node in out:
                if not node in self.out:
                    self.out.append(node)
                if not self in node.inc:
                    node.inc.append(self)

    def print_connections(self):
        print(f"Self: {self}")
        incStr = ""
        for node in self.inc:
            incStr = incStr + str(node) + ", "

        print(f"Incoming nodes: {incStr}")

        outStr = ""
        for node in self.out:
            outStr = outStr + str(node) + ", "

    def get_node(self, data):
        


    def __str__(self):
        return str(self.data)



def build_tech_tree():
    ghost = Node(UnitTypeId.GHOST)
    ghostAca = Node(UnitTypeId.GHOSTACADEMY)
    techLab = Node(UnitTypeId.TECHLAB)
    ghost.connect_dir([ghostAca, techLab], None)
    ghostAca.connect_dir(None, [ghost])
    techLab.connect_dir(None, [ghost])

    return ghost

class TemplarBot(BotAI):
    techTreeRoot = build_tech_tree()

    async def on_step(self, iteration:int):
        async def ManageEco():

            action = ""

            await self.distribute_workers()

            if (self.townhalls):
                cmdcntr = self.townhalls.random

                if self.supply_left <= 4 and self.already_pending(UnitTypeId.SUPPLYDEPOT) == 0 and self.can_afford(UnitTypeId.SUPPLYDEPOT):
                    await self.build(UnitTypeId.SUPPLYDEPOT, near = cmdcntr)
                    action = "Building supply depot"

                if self.supply_left > 0 and self.can_afford(UnitTypeId.MARINE):
                    for bk in self.structures(UnitTypeId.BARRACKS).ready.idle:
                        bk.train(UnitTypeId.MARINE)
                        action = "Training marine"

                if cmdcntr.is_idle and self.can_afford(UnitTypeId.SCV) and self.units(UnitTypeId.SCV).amount < 22:
                    cmdcntr.train(UnitTypeId.SCV)
                    action = "Training SCV"

                elif self.structures(UnitTypeId.BARRACKS).amount < 4 and self.can_afford(UnitTypeId.BARRACKS):
                    await self.build(UnitTypeId.BARRACKS, near = self.structures(UnitTypeId.SUPPLYDEPOT).closest_to(cmdcntr))
                    action = "Building Barrack"

                elif self.structures(UnitTypeId.BARRACKS).ready and self.structures(UnitTypeId.BUNKER).amount < 2:
                    if self.can_afford(UnitTypeId.BUNKER) and not self.already_pending(UnitTypeId.BUNKER):
                        await self.build(UnitTypeId.BUNKER, near = cmdcntr)
                        action = "Building Bunker"

                elif self.structures(UnitTypeId.REFINERY).amount < 2:
                    vespenes = self.vespene_geyser.closer_than(15, cmdcntr)
                    for vespene in vespenes:
                        if self.can_afford(UnitTypeId.REFINERY) and not self.already_pending(UnitTypeId.REFINERY):
                            await self.build(UnitTypeId.REFINERY, vespene)
                            action = "Building Refinery"

            else:
                if self.can_afford(UnitTypeId.COMMANDCENTER):
                    await self.expand_now()
                    action = "Expanding"

                else:
                    action = "Resorting to final push"
                    for unit in self.units.ready.idle:
                        unit.attack(self.enemy_start_locations[0])

            
            if action:
                print(f"Bot took (Eco) action ({action}) on iteration ({iteration})")
            return



        async def ManageDef():
            action = ""
            if action:
                print(f"Bot took (Eco) action ({action}) on iteration ({iteration})")
            return



        async def ManageAtt():
            action = ""

            if self.units(UnitTypeId.MARINE).amount >= 20:
                action = "Sending attack units"

                for mr in self.units(UnitTypeId.MARINE).idle:
                    mr.move(self.units(UnitTypeId.MARINE)[0])

                if self.enemy_units:
                    for mr in self.units(UnitTypeId.MARINE).idle:
                        mr.attack(random.choice(self.enemy_units))


                elif self.enemy_structures:
                    for mr in self.units(UnitTypeId.MARINE).idle:
                        mr.attack(random.choice(self.enemy_structures))

                else:
                    for mr in self.units(UnitTypeId.MARINE).idle:
                        mr.attack(self.enemy_start_locations[0])
            
            if action:
                print(f"Bot took (Att) action ({action}) on iteration ({iteration})")
            return

        await ManageEco()
        await ManageDef()
        await ManageAtt()
        
        targetNode = self.techTreeRoot.get_node(UnitTypeId.GHOSTACADEMY)
        print(self.all_own_units(targetNode.data).amount)
        # while self.all_own_units(targetNode.data).amount == 0 and self.already_pending(targetNode.data):
        #     if targetNode.parent.data == "None" or not targetNode.parent or self.all_own_units(targetNode.parent.data).amount > 0: #Check if we have the prerequisite building
        #             break
        #     else: #If we dont, make that the next thing to build
        #         targetNode = targetNode.parent

        # if self.can_afford(targetNode.data) and not self.already_pending(targetNode.data):
        #     await self.build(targetNode.data, near = self.townhalls[0])
        #     for build in self.structures(targetNode.parent.data):
        #         await build.train(targetNode.data)
            


        
from os import listdir
from os.path import isfile, join
mypath = "E:\Program Files (x86)\StarCraft II\Maps"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
map = random.choice(onlyfiles)
map = map[:map.index('.')]
print(map)

root = build_tech_tree()
root.print_connections()
# root = build_tech_tree()
#root.print_tree()

# mNode = root.get_node(UnitTypeId.MARINE)
# print(str(mNode.parent.data))

# run_game(
#     maps.get(map),
#     [Bot(Race.Terran, TemplarBot()),
#      Computer(Race.Zerg, Difficulty.Hard)],
#     realtime=False
# )
