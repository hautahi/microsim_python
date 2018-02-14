class StaticObj:
    val = 0

    @classmethod
    def increment(cls):
        cls.val += 1


StaticObj.increment()
