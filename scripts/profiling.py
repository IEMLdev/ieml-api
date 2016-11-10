from ieml.usl.tools import usl, random_usl


def paths():
    for i in range(1000):
        u = random_usl()
        usl(u.paths)

if __name__ == '__main__':
    paths()