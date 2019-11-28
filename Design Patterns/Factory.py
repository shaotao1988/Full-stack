from abc import ABCMeta, abstractmethod

class Animal(metaclass = ABCMeta):

    @abstractmethod
    def say(self):
        pass

class Dog(Animal):
    
    def say(self):
        print("I'm dog!")

class Cat(Animal):

    def say(self):
        print("I'm cat!")

class SimpleAnimalFactory():

    @classmethod
    def make_animal(cls, animal_type):
        """
        if animal_type == 'Dog':
            return Dog()
        if animal_type == 'Cat':
            return Cat()
        """
        return eval(animal_type)()

class AbstractFactoryMethod(metaclass = ABCMeta):

    @abstractmethod
    def make_animal(self):
        pass

class DogFactory(AbstractFactoryMethod):

    def make_animal(self):
        return Dog()

class CatFactory(AbstractFactoryMethod):

    def make_animal(self):
        return Cat()


if __name__ == "__main__":
    # 简单工厂模式
    SimpleAnimalFactory.make_animal('Dog').say()
    SimpleAnimalFactory.make_animal('Cat').say()

    # 工厂方法模式
    DogFactory().make_animal().say()
    CatFactory().make_animal().say()


