import sys
from csparse.demo import DemoFile
from csparse.parser import DemoParser


def on_player_death(event):
    print "{} was killed with a {} by {}".format(
        event.userid, event.weapon, event.attacker
    )


def main():
    demo = DemoFile(open(sys.argv[1], 'r'))
    parser = DemoParser(demo)
    parser.on("player_death", on_player_death)
    parser.parse()


if __name__ == '__main__':
    main()
