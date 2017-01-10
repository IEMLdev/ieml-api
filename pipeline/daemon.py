from progressbar.bar import ProgressBar

from pipeline.driver.scoopit import ScoopIt
from pipeline.model.post import PostConnector

drivers = {
    'scoopit': ScoopIt()
}


if __name__ == '__main__':
    posts = PostConnector()
    for post in ProgressBar()(drivers['scoopit'].posts()):
        posts.save(post)


